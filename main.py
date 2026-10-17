import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")

app = FastAPI(
    title="URL Detection System",
    description="A secure URL threat detection API using the Google Safe Browsing API.",
    version="1.0.0"
)

# Request model
class URLRequest(BaseModel):
    url: str

# Response model
class URLResponse(BaseModel):
    submitted_url: str
    prediction: str
    threat_found: bool
    threat_category: str | None = None
    message: str

@app.get("/", tags=["Status"])
def root():
    """Returns a message confirming that the API is running."""
    return {
        "status": "online",
        "message": "Welcome to the URL Detection System API. Use /docs to test endpoints."
    }

@app.get("/health", tags=["Status"])
def health_check():
    """Checks whether the application is running without exposing secret API keys."""
    key_configured = bool(API_KEY and len(API_KEY) > 5)
    return {
        "status": "healthy",
        "api_key_configured": key_configured
    }

@app.post("/detect", response_model=URLResponse, tags=["Detection"])
async def detect_url(request: URLRequest):
    """
    Accepts a URL, validates it, checks it against the Google Safe Browsing API,
    and returns a structured security analysis.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: Google Safe Browsing API key is missing."
        )

    target_url = request.url

    # Google Safe Browsing v4 endpoint
    gsb_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

    payload = {
        "client": {
            "clientId": "url-detection-system",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": target_url}
            ]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(gsb_url, json=payload)
            
        if response.status_code == 400:
            # Include exact API error detail for easier debugging
            err_detail = response.json().get("error", {}).get("message", "Invalid request format.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Safe Browsing API Error: {err_detail}"
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API authentication error: Check if your Google Safe Browsing API key is valid and enabled."
            )
        elif response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please try again later."
            )
        elif response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Threat intelligence API returned an unexpected error (Status: {response.status_code})"
            )

        data = response.json()
        matches = data.get("matches", [])

        if matches:
            threat_type = matches[0].get("threatType", "UNKNOWN")
            category_mapping = {
                "SOCIAL_ENGINEERING": "phishing",
                "MALWARE": "malware",
                "UNWANTED_SOFTWARE": "potentially_unsafe",
                "POTENTIALLY_HARMFUL_APPLICATION": "potentially_unsafe"
            }
            mapped_category = category_mapping.get(threat_type, "unknown")
            
            return URLResponse(
                submitted_url=target_url,
                prediction=mapped_category,
                threat_found=True,
                threat_category=threat_type,
                message=f"Warning: A known threat ({threat_type}) was detected for this URL."
            )
        else:
            return URLResponse(
                submitted_url=target_url,
                prediction="unknown",
                threat_found=False,
                threat_category=None,
                message="No known threats were found in the database for this URL. Note: This does not guarantee that the URL is safe or legitimate."
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to the threat-intelligence API timed out."
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network communication failure with threat-intelligence API: {str(exc)}"
        )