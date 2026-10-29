import os
import re
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
GSB_ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

THREAT_TYPES = [
    "MALWARE",
    "SOCIAL_ENGINEERING",
    "UNWANTED_SOFTWARE",
    "POTENTIALLY_HARMFUL_APPLICATION",
]

# Map Google threat type → (prediction, risk_level)
THREAT_MAPPING = {
    "MALWARE": ("malware", "high"),
    "SOCIAL_ENGINEERING": ("phishing", "high"),
    "UNWANTED_SOFTWARE": ("potentially_unsafe", "medium"),
    "POTENTIALLY_HARMFUL_APPLICATION": ("potentially_unsafe", "medium"),
}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="URL Detection System",
    description="A secure URL threat detection API using the Google Safe Browsing API.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class URLRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("URL must not be empty.")
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must start with http:// or https://")
        if not parsed.hostname:
            raise ValueError("URL must contain a valid hostname.")
        return value


class URLResponse(BaseModel):
    submitted_url: str
    url: str  # alias for frontend compatibility
    prediction: str
    risk_level: str  # "high" | "medium" | "low"
    threat_found: bool
    threat_category: Optional[str] = None
    message: str
    threat_matches: list[Any] = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "message": "Welcome to the URL Detection System API.",
    }


@app.get("/health", tags=["Status"])
def health_check():
    key_configured = bool(API_KEY and len(API_KEY) > 5)
    return {
        "status": "healthy",
        "api_key_configured": key_configured,
    }


@app.post("/detect", response_model=URLResponse, tags=["Detection"])
async def detect_url(request: URLRequest):
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: GOOGLE_SAFE_BROWSING_API_KEY is missing.",
        )

    target_url = request.url
    gsb_url = f"{GSB_ENDPOINT}?key={API_KEY}"

    payload = {
        "client": {
            "clientId": "url-detection-system",
            "clientVersion": "1.1.0",
        },
        "threatInfo": {
            "threatTypes": THREAT_TYPES,
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": target_url}],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(gsb_url, json=payload)

        # --- Google error handling ---
        if response.status_code == 400:
            try:
                err_detail = response.json().get("error", {}).get("message", "Invalid request format.")
            except Exception:
                err_detail = "Invalid request format."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Safe Browsing API error: {err_detail}",
            )
        if response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API authentication error: check that your Google Safe Browsing API key is valid and enabled.",
            )
        if response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API quota exceeded. Please try again later.",
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Threat intelligence API returned HTTP {response.status_code}.",
            )

        data = response.json()
        matches = data.get("matches", [])

        # --- Threat found ---
        if matches:
            threat_type = matches[0].get("threatType", "UNKNOWN")
            prediction, risk_level = THREAT_MAPPING.get(threat_type, ("unknown", "medium"))
            return URLResponse(
                submitted_url=target_url,
                url=target_url,
                prediction=prediction,
                risk_level=risk_level,
                threat_found=True,
                threat_category=threat_type,
                message=f"Warning: A known threat ({threat_type}) was detected for this URL.",
                threat_matches=matches,
            )

        # --- Clean ---
        return URLResponse(
            submitted_url=target_url,
            url=target_url,
            prediction="unknown",
            risk_level="low",
            threat_found=False,
            threat_category=None,
            message=(
                "No known threats were found in the database for this URL. "
                "Note: this does not guarantee that the URL is safe."
            ),
            threat_matches=[],
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to the threat-intelligence API timed out.",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network failure contacting threat-intelligence API: {exc}",
        )