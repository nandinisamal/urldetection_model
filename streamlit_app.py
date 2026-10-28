
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# --------------------------------------------------
# Interface translations
# --------------------------------------------------

UI = {
    "en": {
        "brand": "🛡️ TRUSTCHECK AI",
        "headline": "Think before you trust.",
        "subtitle": "Analyze suspicious SMS messages, emails, links, and job offers.",
        "language": "Result language",
        "auto": "Auto-detect from message",
        "english": "English",
        "hindi": "Hindi",
        "marathi": "Marathi",
        "scan_title": "🔎 Scan a suspicious message",
        "category": "Message category",
        "general": "General message",
        "sms": "SMS / Text message",
        "email": "Email",
        "job": "Job offer",
        "message": "Paste your message here",
        "placeholder": "Paste a suspicious message, email, or job offer...",
        "privacy": "Never paste real passwords, OTPs, or private banking details.",
        "button": "✦ Scan for Scams",
        "empty": "Please enter a message before scanning.",
        "results": "📋 Scan Results",
        "score": "Risk Score",
        "warnings": "⚠️ Warning Signs",
        "no_warnings": "No specific warning signs were detected.",
        "urls": "🔗 URLs Found",
        "no_urls": "No URLs found in this message.",
        "url_checks": "🔍 URL Safety Checks",
        "no_checks": "No URL checks were needed.",
        "category_label": "Category",
        "note": "This is an automated screening tool. Verify important messages independently.",
        "connection": "Cannot connect to the FastAPI backend. Make sure it is running on port 8000.",
        "timeout": "The backend took too long to respond. Please try again.",
        "request_error": "The request could not be completed.",
        "footer": "TrustCheck AI · Stay alert. Stay protected.",
        "unsafe": "🚨 Unsafe URL detected",
        "safe_url": "✅ No known threat found by Google Safe Browsing",
        "not_checked": "⚠️ Not checked: Google API key is not configured",
        "failed": "⚠️ URL safety check failed",
        "invalid": "⚠️ This URL appears invalid",
        "unknown": "URL check status",
        "reason": "Details",
        "server_error": "The backend returned an error",
    },
    "hi": {
        "brand": "🛡️ TRUSTCHECK AI",
        "headline": "सोचें, फिर भरोसा करें।",
        "subtitle": "संदिग्ध SMS, ईमेल, लिंक और नौकरी के प्रस्तावों की जाँच करें।",
        "language": "परिणाम की भाषा",
        "auto": "संदेश से भाषा पहचानें",
        "english": "अंग्रेज़ी",
        "hindi": "हिंदी",
        "marathi": "मराठी",
        "scan_title": "🔎 संदिग्ध संदेश की जाँच करें",
        "category": "संदेश की श्रेणी",
        "general": "सामान्य संदेश",
        "sms": "SMS / टेक्स्ट संदेश",
        "email": "ईमेल",
        "job": "नौकरी का प्रस्ताव",
        "message": "अपना संदेश यहाँ डालें",
        "placeholder": "संदिग्ध संदेश, ईमेल या नौकरी का प्रस्ताव यहाँ डालें...",
        "privacy": "असली पासवर्ड, OTP या बैंक की निजी जानकारी न डालें।",
        "button": "✦ धोखाधड़ी की जाँच करें",
        "empty": "कृपया जाँच करने से पहले संदेश लिखें।",
        "results": "📋 जाँच के परिणाम",
        "score": "जोखिम स्कोर",
        "warnings": "⚠️ चेतावनी के संकेत",
        "no_warnings": "कोई विशेष चेतावनी संकेत नहीं मिला।",
        "urls": "🔗 मिले हुए लिंक",
        "no_urls": "इस संदेश में कोई लिंक नहीं मिला।",
        "url_checks": "🔍 लिंक की सुरक्षा जाँच",
        "no_checks": "किसी लिंक की जाँच आवश्यक नहीं थी।",
        "category_label": "श्रेणी",
        "note": "यह स्वचालित जाँच है। महत्वपूर्ण संदेशों की स्वतंत्र रूप से पुष्टि करें।",
        "connection": "FastAPI बैकएंड से कनेक्ट नहीं हो पा रहा। सुनिश्चित करें कि पोर्ट 8000 पर सर्वर चल रहा है।",
        "timeout": "बैकएंड से उत्तर आने में बहुत समय लगा। फिर कोशिश करें।",
        "request_error": "अनुरोध पूरा नहीं हो सका।",
        "footer": "TrustCheck AI · सतर्क रहें, सुरक्षित रहें।",
        "unsafe": "🚨 असुरक्षित लिंक मिला",
        "safe_url": "✅ Google Safe Browsing को कोई ज्ञात खतरा नहीं मिला",
        "not_checked": "⚠️ जाँच नहीं हुई: Google API key सेट नहीं है",
        "failed": "⚠️ लिंक की सुरक्षा जाँच विफल रही",
        "invalid": "⚠️ यह लिंक अमान्य दिखाई देता है",
        "unknown": "लिंक की जाँच की स्थिति",
        "reason": "विवरण",
        "server_error": "बैकएंड ने त्रुटि दी",
    },
    "mr": {
        "brand": "🛡️ TRUSTCHECK AI",
        "headline": "विश्वास ठेवण्यापूर्वी विचार करा.",
        "subtitle": "संशयास्पद SMS, ईमेल, लिंक आणि नोकरीच्या ऑफर तपासा.",
        "language": "निकालाची भाषा",
        "auto": "संदेशावरून भाषा ओळखा",
        "english": "इंग्रजी",
        "hindi": "हिंदी",
        "marathi": "मराठी",
        "scan_title": "🔎 संशयास्पद संदेश तपासा",
        "category": "संदेशाचा प्रकार",
        "general": "सामान्य संदेश",
        "sms": "SMS / मजकूर संदेश",
        "email": "ईमेल",
        "job": "नोकरीची ऑफर",
        "message": "तुमचा संदेश येथे टाका",
        "placeholder": "संशयास्पद संदेश, ईमेल किंवा नोकरीची ऑफर येथे टाका...",
        "privacy": "खरे पासवर्ड, OTP किंवा बँकेची गोपनीय माहिती टाकू नका.",
        "button": "✦ फसवणूक तपासा",
        "empty": "तपासणी करण्यापूर्वी कृपया संदेश लिहा.",
        "results": "📋 तपासणीचा निकाल",
        "score": "धोक्याची पातळी",
        "warnings": "⚠️ धोक्याची चिन्हे",
        "no_warnings": "धोक्याची कोणतीही विशिष्ट चिन्हे आढळली नाहीत.",
        "urls": "🔗 आढळलेले दुवे",
        "no_urls": "या संदेशात कोणताही दुवा आढळला नाही.",
        "url_checks": "🔍 दुव्याची सुरक्षा तपासणी",
        "no_checks": "कोणत्याही दुव्याची तपासणी आवश्यक नव्हती.",
        "category_label": "प्रकार",
        "note": "ही स्वयंचलित तपासणी आहे. महत्त्वाच्या संदेशांची स्वतंत्रपणे पडताळणी करा.",
        "connection": "FastAPI बॅकएंडशी जोडता येत नाही. पोर्ट 8000 वर सर्व्हर सुरू आहे याची खात्री करा.",
        "timeout": "बॅकएंडकडून उत्तर मिळण्यास उशीर झाला. पुन्हा प्रयत्न करा.",
        "request_error": "विनंती पूर्ण करता आली नाही.",
        "footer": "TrustCheck AI · सतर्क राहा, सुरक्षित राहा.",
        "unsafe": "🚨 असुरक्षित दुवा आढळला",
        "safe_url": "✅ Google Safe Browsing ला कोणताही ज्ञात धोका आढळला नाही",
        "not_checked": "⚠️ तपासणी झाली नाही: Google API key सेट केलेली नाही",
        "failed": "⚠️ दुव्याची सुरक्षा तपासणी अयशस्वी झाली",
        "invalid": "⚠️ हा दुवा अवैध दिसत आहे",
        "unknown": "दुव्याच्या तपासणीची स्थिती",
        "reason": "तपशील",
        "server_error": "बॅकएंडमध्ये त्रुटी आली",
    },
}


# --------------------------------------------------
# Page configuration and purple-white design
# --------------------------------------------------

st.set_page_config(
    page_title="TrustCheck AI | Scam Detection",
    page_icon="🛡️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #faf8ff, #f0e7ff);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .brand {
        color: #5b21b6;
        font-size: 17px;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .hero {
        text-align: center;
        padding: 20px 0;
    }
    .hero h1 {
        color: #2e1065;
        font-size: 40px;
        font-weight: 800;
    }
    .hero p {
        color: #756787;
        font-size: 16px;
    }
    div[data-testid="stForm"] {
        background: white;
        padding: 22px;
        border: 1px solid #e7ddf8;
        border-radius: 20px;
        box-shadow: 0 12px 35px rgba(76, 29, 149, 0.08);
    }
    div[data-testid="stFormSubmitButton"] button {
        background: #6d28d9;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        min-height: 45px;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: #4c1d95;
        color: white;
    }
    .footnote {
        color: #756787;
        font-size: 12px;
        text-align: center;
        margin-top: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Language and form
# --------------------------------------------------

language_options = {
    "Auto-detect": "auto",
    "English": "en",
    "हिंदी": "hi",
    "मराठी": "mr",
}

chosen_label = st.selectbox(
    "🌐 Language / भाषा",
    list(language_options.keys()),
)

requested_language = language_options[chosen_label]

# Use the selected language for the interface.
# In Auto-detect mode, the interface starts in English;
# the result language follows the detected message language.
interface_language = (
    requested_language if requested_language != "auto" else "en"
)
u = UI[interface_language]

st.markdown(
    f'<div class="brand">{u["brand"]}</div>',
    unsafe_allow_html=True,
)

headline = u["headline"]
subtitle = u["subtitle"]

st.markdown(
    f"""
    <div class="hero">
        <h1>{headline}</h1>
        <p>{subtitle}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

category_options = {
    u["general"]: "general",
    u["sms"]: "sms",
    u["email"]: "email",
    u["job"]: "job",
}

with st.form("scam_scan_form"):
    st.subheader(u["scan_title"])

    selected_category_label = st.selectbox(
        u["category"],
        list(category_options.keys()),
    )

    message = st.text_area(
        u["message"],
        height=180,
        max_chars=10000,
        placeholder=u["placeholder"],
    )

    st.caption(u["privacy"])

    submitted = st.form_submit_button(
        u["button"],
        use_container_width=True,
    )


# --------------------------------------------------
# Submit message to FastAPI
# --------------------------------------------------

if submitted:
    if not message.strip():
        st.warning(u["empty"])

    else:
        try:
            with st.spinner("Analyzing..." if interface_language == "en"
                            else "जाँच हो रही है..." if interface_language == "hi"
                            else "तपासणी सुरू आहे..."):

                response = requests.post(
                    f"{BACKEND_URL}/scan",
                    json={
                        "text": message.strip(),
                        "category": category_options[
                            selected_category_label
                        ],
                        "language": requested_language,
                    },
                    timeout=30,
                )

                if not response.ok:
                    detail = response.text[:1000]
                    st.error(
                        f'{u["server_error"]}: '
                        f'{response.status_code}'
                    )
                    st.code(detail)
                    st.stop()

                result = response.json()

            # Use the result language returned by the backend.
            result_language = result.get("language", "en")
            if result_language not in UI:
                result_language = "en"

            r = UI[result_language]
            t_verdict = result.get("verdict", "Analysis completed")
            score = max(
                0,
                min(10, int(result.get("risk_score", 0))),
            )

            st.markdown("---")
            st.subheader(r["results"])

            # Show verdict with appropriate styling.
            if t_verdict == "Likely Scam" or t_verdict == "संभावित धोखाधड़ी" or t_verdict == "संभाव्य फसवणूक":
                st.error(f"🚨 {t_verdict}")
            elif (
                t_verdict in {
                    "Suspicious", "Needs Further Verification",
                    "संदिग्ध संदेश", "अधिक जाँच आवश्यक है",
                    "संशयास्पद", "अधिक पडताळणी आवश्यक आहे",
                }
            ):
                st.warning(f"⚠️ {t_verdict}")
            else:
                st.success(f"🛡️ {t_verdict}")

            st.metric(r["score"], f"{score}/10")
            st.progress(score / 10)

            st.caption(
                f'{r["category_label"]}: '
                f'{result.get("category", "general").upper()}'
            )

            st.markdown(f'### {r["warnings"]}')
            warnings = result.get("warning_signs", [])

            if warnings:
                for warning in warnings:
                    st.markdown(f"- {warning}")
            else:
                st.write(r["no_warnings"])

            st.markdown(f'### {r["urls"]}')
            urls = result.get("urls_found", [])

            if urls:
                for url in urls:
                    st.code(url, language=None)
            else:
                st.write(r["no_urls"])

            st.markdown(f'### {r["url_checks"]}')
            url_checks = result.get("url_checks", [])

            if url_checks:
                for check in url_checks:
                    url = check.get("url", "Unknown URL")
                    status = check.get("status", "unknown")

                    with st.expander(url):
                        if status == "unsafe":
                            st.error(r["unsafe"])
                        elif status == "no_known_threat_found":
                            st.success(r["safe_url"])
                        elif status == "not_checked":
                            st.warning(r["not_checked"])
                        elif status == "check_failed":
                            st.warning(r["failed"])
                        elif status == "invalid_url":
                            st.warning(r["invalid"])
                        else:
                            st.info(
                                f'{r["unknown"]}: {status}'
                            )

                        if check.get("reason"):
                            st.caption(
                                f'{r["reason"]}: {check["reason"]}'
                            )
            else:
                st.write(r["no_checks"])

            st.info(result.get("note", r["note"]))
            st.caption(r["note"])

        except requests.exceptions.ConnectionError:
            st.error(u["connection"])

        except requests.exceptions.Timeout:
            st.error(u["timeout"])

        except requests.exceptions.RequestException as error:
            st.error(f'{u["request_error"]} {error}')

        except (ValueError, TypeError, KeyError) as error:
            st.error(f'Could not display scan results: {error}')


st.markdown(
    f'<div class="footnote">{u["footer"]}</div>',
    unsafe_allow_html=True,
)
