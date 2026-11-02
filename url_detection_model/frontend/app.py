import os
from datetime import datetime
from urllib.parse import urlparse

import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TrustCheck | URL Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CLOUD DEPLOYMENT FIX: Try st.secrets first, safely fallback if not found
try:
    API_URL = st.secrets["URL_DETECTION_API_URL"]
except (KeyError, FileNotFoundError):
    # Fallback for local development if secrets.toml doesn't exist or key is missing
    API_URL = os.getenv("URL_DETECTION_API_URL", "http://127.0.0.1:8000/detect")

# ---------------------------------------------------------------------------
# THEME — single source of truth
# ---------------------------------------------------------------------------
LIGHT = {
    "bg": "linear-gradient(135deg,#faf8ff,#eee5ff)",
    "bg_solid": "#faf8ff",
    "card": "#ffffff",
    "panel": "#f7f3ff",
    "input": "#fdfcff",
    "text": "#302044",
    "muted": "#81758d",
    "border": "#eee6fa",
    "purple": "#6335a5",
    "purple_dark": "#472078",
    "track": "#ece6f7",
    "tag_bg": "#e9ddff",
    "tag_fg": "#6335a5",
    "safe_bg": "#e4f8ed", "safe_fg": "#247c50",
    "warn_bg": "#fef3c7", "warn_fg": "#92400e",
    "danger_bg": "#fee2e2", "danger_fg": "#b91c1c",
    "shadow": "rgba(75,42,115,.09)",
    "code_bg": "#f4f4f5",
    "divider": "#eee6fa",
}

DARK = {
    "bg": "linear-gradient(135deg,#20182e,#171321)",
    "bg_solid": "#171321",
    "card": "#261d35",
    "panel": "#21182e",
    "input": "#2d2340",
    "text": "#f0e5ff",
    "muted": "#c2b4d2",
    "border": "#3c2c51",
    "purple": "#bd94f5",
    "purple_dark": "#eadcff",
    "track": "#2c2248",
    "tag_bg": "#3d2b56",
    "tag_fg": "#d8bdff",
    "safe_bg": "#123a22", "safe_fg": "#86efac",
    "warn_bg": "#4a3512", "warn_fg": "#fcd34d",
    "danger_bg": "#4a1620", "danger_fg": "#fca5a5",
    "shadow": "rgba(0,0,0,.30)",
    "code_bg": "#0f0a1e",
    "divider": "#3c2c51",
}


def build_css(c: dict, is_dark: bool) -> str:
    streamlit_bg = c["bg_solid"]
    return f"""
    <style id="trustcheck-theme">
      :root {{ color-scheme: {'dark' if is_dark else 'light'}; }}

      /* ============================================================
         PAGE BACKGROUND AND MAIN CONTENT
      ============================================================ */
      html, body,
      .stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"],
      .main,
      .main .block-container {{
        background-color: {streamlit_bg} !important;
        background-image: {c['bg']} !important;
        color: {c['text']} !important;
      }}

      .main .block-container {{
        max-width: 1120px;
        padding: 2rem 3rem 3rem;
      }}

      .stApp {{ color: {c['text']} !important; }}
      .main p, .main label, .main [data-testid="stMarkdownContainer"] {{
        color: {c['text']};
      }}
      .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {{
        color: {c['purple_dark']} !important;
        letter-spacing: -0.35px;
      }}
      a {{ color: {c['purple']} !important; }}

      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"] {{
        background: transparent !important;
        border: 0 !important;
      }}
      [data-testid="stHeader"] * {{ color: {c['text']} !important; }}

      /* ============================================================
         FIXED PURPLE SIDEBAR
      ============================================================ */
      [data-testid="stSidebar"],
      [data-testid="stSidebar"] > div,
      [data-testid="stSidebarContent"] {{
        background: linear-gradient(180deg,#54288e 0%,#3d176d 100%) !important;
        border-right: 0 !important;
      }}
      [data-testid="stSidebar"] {{
        min-width: 255px !important;
        width: 255px !important;
      }}
      [data-testid="stSidebar"] *:not(svg):not(path) {{
        color: #ffffff !important;
      }}
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #ffffff !important;
      }}
      [data-testid="stSidebar"] hr {{
        border: 0 !important;
        border-top: 1px solid rgba(255,255,255,.22) !important;
      }}
      [data-testid="stSidebar"] label {{
        color: #f1eaff !important;
        font-weight: 600;
      }}

      /* ============================================================
         SIDEBAR LANGUAGE BUTTONS
      ============================================================ */
      .lang-btn-container {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 8px;
        margin-bottom: 16px;
      }}

      /* ============================================================
         SIDEBAR TOGGLE (DARK MODE)
      ============================================================ */
      [data-testid="stSidebar"] [data-testid="stToggle"] label span {{
        color: #ffffff !important;
      }}
      [data-testid="stSidebar"] [data-testid="stToggle"] div[role="checkbox"] {{
        background-color: rgba(255,255,255,0.2) !important;
      }}
      [data-testid="stSidebar"] [data-testid="stToggle"] div[aria-checked="true"] {{
        background-color: #ffffff !important;
      }}
      [data-testid="stSidebar"] [data-testid="stToggle"] div[aria-checked="true"] > div {{
        background-color: #6335a5 !important;
      }}

      /* ============================================================
         HERO
      ============================================================ */
      .hero {{
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 48px 28px 38px;
        margin: 4px 0 24px;
        border: 1px solid {c['border']};
        border-radius: 22px;
        background: {c['bg']};
        box-shadow: 0 12px 32px {c['shadow']};
      }}
      .hero .tag {{
        display: inline-block;
        padding: 9px 16px;
        background: {c['tag_bg']};
        color: {c['tag_fg']} !important;
        border: 1px solid {c['border']};
        border-radius: 30px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .7px;
        margin-bottom: 15px;
      }}
      .hero h1 {{
        font-size: clamp(34px,5vw,52px);
        line-height: 1.15;
        margin: 10px 0 14px;
        letter-spacing: -1.5px;
        color: {c['text']} !important;
        font-weight: 800;
      }}
      .hero h1 span {{ color: {c['purple']} !important; }}
      .hero p {{
        max-width: 650px;
        margin: auto;
        color: {c['muted']} !important;
        line-height: 1.8;
        font-size: 15px;
      }}

      /* ============================================================
         SCANNER INTRO CARD AND FORM
      ============================================================ */
      .card {{
        background: {c['card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 18px;
        padding: 25px 28px;
        margin: 22px 0 12px;
        box-shadow: 0 8px 28px {c['shadow']};
      }}
      .card h2 {{
        margin: 0 0 9px;
        font-size: 21px;
        color: {c['purple_dark']} !important;
      }}
      .card .subtext {{
        color: {c['muted']} !important;
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 0;
      }}
      [data-testid="stForm"] {{
        background: {c['card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 18px !important;
        padding: 22px 26px 24px !important;
        margin: 0 0 24px !important;
        box-shadow: 0 8px 28px {c['shadow']} !important;
      }}
      [data-testid="stTextInput"] label,
      [data-testid="stTextInput"] label p {{
        color: {c['text']} !important;
        font-size: 13px !important;
        font-weight: 700 !important;
      }}
      div[data-baseweb="input"] > div {{
        background: {c['input']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 11px !important;
        min-height: 47px;
        box-shadow: none !important;
      }}
      div[data-baseweb="input"] > div:focus-within {{
        border-color: {c['purple']} !important;
        box-shadow: 0 0 0 3px rgba(99,53,165,.14) !important;
      }}
      div[data-baseweb="input"] input {{
        color: {c['text']} !important;
        -webkit-text-fill-color: {c['text']} !important;
      }}
      div[data-baseweb="input"] input::placeholder {{
        color: {c['muted']} !important;
        -webkit-text-fill-color: {c['muted']} !important;
        opacity: .85 !important;
      }}

      /* ============================================================
         BUTTONS
      ============================================================ */
      div.stButton > button,
      div[data-testid="stFormSubmitButton"] button,
      button[kind="primaryFormSubmit"] {{
        background: linear-gradient(100deg,#6335a5,#8150c4) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 0 !important;
        border-radius: 10px !important;
        min-height: 46px;
        padding: 9px 18px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        box-shadow: 0 7px 18px rgba(99,53,165,.22);
      }}
      div.stButton > button *,
      div[data-testid="stFormSubmitButton"] button * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
      }}

      /* ============================================================
         RESULT VERDICT, GAUGE, REASONS AND ADVICE
      ============================================================ */
      .verdict {{
        display: inline-block;
        padding: 8px 15px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 13px;
        margin-bottom: 12px;
      }}
      .verdict.safe {{ background: {c['safe_bg']}; color: {c['safe_fg']} !important; }}
      .verdict.warning {{ background: {c['warn_bg']}; color: {c['warn_fg']} !important; }}
      .verdict.danger {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}
      .reason {{
        padding: 12px 14px 12px 40px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 11px;
        margin-bottom: 9px;
        font-size: 13px;
        line-height: 1.6;
        position: relative;
        color: {c['text']} !important;
      }}
      .reason::before {{
        content: "⚠";
        position: absolute;
        left: 14px;
        top: 11px;
        color: #f59e0b;
      }}
      .url-card {{
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 13px 15px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-left-width: 4px;
        border-radius: 11px;
        font-size: 13px;
        margin-bottom: 9px;
      }}
      .url-card.safe {{ border-left-color: #16a34a; }}
      .url-card.danger {{ border-left-color: #dc2626; }}
      .url-card.unknown {{ border-left-color: {c['muted']}; }}
      .url-card code {{
        font-size: 13px;
        color: {c['text']} !important;
        background: transparent !important;
      }}
      .pill {{
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
      }}
      .pill.safe {{ background: {c['safe_bg']}; color: {c['safe_fg']} !important; }}
      .pill.danger {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}
      .pill.unknown {{ background: {c['track']}; color: {c['muted']} !important; }}
      .advice {{
        padding: 16px 18px;
        border-radius: 12px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        font-size: 13px;
        line-height: 1.8;
        color: {c['text']} !important;
      }}
      .advice ul {{ margin: 7px 0 0; padding-left: 20px; }}
      .advice li {{ color: {c['text']} !important; padding: 2px 0; }}
      
      /* PLOTLY CHART FIX */
      [data-testid="stPlotlyChart"] {{
        background: {c['card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 16px;
        padding: 10px;
        overflow: hidden !important;
      }}

      /* ============================================================
         RECENT SCANS / HISTORY
      ============================================================ */
      .history-item {{
        display: grid;
        grid-template-columns: 54px minmax(0,1fr) auto;
        gap: 12px;
        align-items: center;
        padding: 12px 14px;
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 11px;
        font-size: 13px;
        margin-bottom: 9px;
      }}
      .history-item .score {{
        font-weight: 800;
        text-align: center;
        padding: 7px 0;
        border-radius: 8px;
        font-size: 13px;
      }}
      .score.safe {{ background: {c['safe_bg']}; color: {c['safe_fg']} !important; }}
      .score.warning {{ background: {c['warn_bg']}; color: {c['warn_fg']} !important; }}
      .score.danger {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}
      .score.unknown {{ background: {c['track']}; color: {c['muted']} !important; }}
      .history-item .txt {{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-family: ui-monospace,SFMono-Regular,Consolas,monospace;
        font-size: 12px;
        color: {c['text']} !important;
      }}
      .history-item .when {{
        color: {c['muted']} !important;
        font-size: 11px;
        white-space: nowrap;
      }}

      /* ============================================================
         FEATURE CARDS
      ============================================================ */
      .feature {{
        background: {c['card']};
        border: 1px solid {c['border']};
        padding: 22px 17px;
        border-radius: 15px;
        text-align: center;
        height: 100%;
      }}
      .feature .icon {{ font-size: 27px; margin-bottom: 10px; }}
      .feature strong {{
        display: block;
        font-size: 14px;
        margin-bottom: 7px;
        color: {c['text']} !important;
      }}
      .feature p {{
        font-size: 12px;
        color: {c['muted']} !important;
        line-height: 1.6;
        margin: 0;
      }}

      /* ============================================================
         ALERTS / WARNINGS / ERRORS
      ============================================================ */
      [data-testid="stAlert"] {{
        background: {c['panel']} !important;
        border: 1px solid {c['border']} !important;
        color: {c['text']} !important;
        border-radius: 12px !important;
      }}
      [data-testid="stAlert"] *,
      [data-testid="stAlert"] p,
      [data-testid="stAlert"] span {{
        color: {c['text']} !important;
        -webkit-text-fill-color: {c['text']} !important;
      }}
      [data-testid="stAlert"] svg {{
        fill: {c['text']} !important;
      }}

      details, [data-testid="stExpander"] {{
        background: {c['card']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
      }}
      details summary, [data-testid="stExpander"] summary {{
        color: {c['purple_dark']} !important;
      }}
      [data-testid="stExpander"] * {{ color: {c['text']} !important; }}
      [data-testid="stJson"] {{
        background: {c['panel']} !important;
        border-radius: 10px;
      }}
      [data-testid="stJson"] * {{ color: {c['text']} !important; }}
      pre, code, .stCode {{
        background: {c['code_bg']} !important;
        color: {c['text']} !important;
      }}
      [data-testid="stCaptionContainer"],
      [data-testid="stCaptionContainer"] * {{
        color: {c['muted']} !important;
        -webkit-text-fill-color: {c['muted']} !important;
      }}
      [data-testid="stSpinner"] * {{ color: {c['text']} !important; }}
      [data-testid="stToast"] {{
        background: {c['card']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
      }}
      hr {{
        border: 0 !important;
        border-top: 1px solid {c['divider']} !important;
        margin: 22px 0 !important;
      }}
      .footer {{
        text-align: center;
        padding: 24px 10px 12px;
        color: {c['muted']} !important;
        font-size: 12px;
        line-height: 1.8;
      }}

      /* ============================================================
         RESPONSIVE LAYOUT
      ============================================================ */
      @media (max-width: 900px) {{
        .main .block-container {{ padding: 1.5rem 1.4rem 2.5rem; }}
        .hero {{ padding: 38px 20px 30px; }}
      }}
      @media (max-width: 640px) {{
        [data-testid="stSidebar"] {{ min-width: 245px !important; width: 245px !important; }}
        .main .block-container {{ padding: 1rem 1rem 2rem; }}
        .hero {{ padding: 30px 16px 25px; border-radius: 16px; }}
        .hero h1 {{ font-size: 34px; }}
        .hero p {{ font-size: 14px; }}
        .card {{ padding: 20px; }}
        [data-testid="stForm"] {{ padding: 18px !important; }}
        .history-item {{ grid-template-columns: 45px minmax(0,1fr); }}
        .history-item .when {{ grid-column: 2; }}
      }}
    </style>
    """

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
T = {
    "English": {
        "lang": "Language", "dark": "🌙 Dark mode",
        "hero_tag": "✦ YOUR DIGITAL SAFETY ASSISTANT",
        "hero_desc": "Paste a URL and let TrustCheck check it against Google Safe Browsing. Get a clear risk verdict in seconds.",
        "scanner_title": "Scan a suspicious URL",
        "scanner_sub": "Paste a website address below. Do not include passwords, OTPs, or private banking details.",
        "url_label": "Website URL",
        "placeholder": "https://example.com/suspicious-path",
        "scan_btn": "✦ Check URL",
        "analyzing": "Analyzing URL…",
        "empty": "Enter a URL first.",
        "invalid": "Enter a valid URL beginning with http:// or https://.",
        "error_conn": "Could not connect to the API. Is FastAPI running?",
        "result_title": "Scan results",
        "risk_high": "High risk", "risk_medium": "Medium risk", "risk_low": "Low risk",
        "verdict_high": "High risk", "verdict_medium": "Medium risk", "verdict_safe": "Looks safe",
        "url_prefix": "URL:", "reasons_title": "Why this was flagged",
        "link_title": "Link check", "link_hint": "Links found in the URL you submitted. Never open a link you don't trust.",
        "pill_safe": "No threat", "pill_danger": "Unsafe", "pill_unknown": "Unchecked",
        "advice_title": "What you should do",
        "raw_title": "View raw server response",
        "history_title": "🕘 Recent scans", "clear_history": "Clear history",
        "no_history": "No scans yet.", "history_cleared": "History cleared",
        "feat1_title": "Google Safe Browsing",
        "feat1_desc": "Verified against Google's live threat lists for malware, phishing and unwanted software.",
        "feat2_title": "Pattern analysis",
        "feat2_desc": "Detects suspicious URL patterns right in your browser — no upload needed.",
        "feat3_title": "Instant results",
        "feat3_desc": "One click to a clear High / Medium / Low risk verdict with actionable advice.",
        "footer_line1": "TrustCheck · Stay alert. Stay protected.",
        "footer_line2": "Automated results can be wrong. Always verify important links independently.",
    },
    "हिंदी": {
        "lang": "भाषा", "dark": "🌙 डार्क मोड",
        "hero_tag": "✦ आपका डिजिटल सुरक्षा सहायक",
        "hero_desc": "URL पेस्ट करें और TrustCheck से Google Safe Browsing के खिलाफ जाँचें। कुछ सेकंड में स्पष्ट परिणाम।",
        "scanner_title": "संदिग्ध URL स्कैन करें",
        "scanner_sub": "वेबसाइट पता पेस्ट करें। पासवर्ड, OTP या बैंकिंग जानकारी न डालें।",
        "url_label": "वेबसाइट URL",
        "placeholder": "https://example.com/suspicious-path",
        "scan_btn": "✦ URL जाँचें",
        "analyzing": "जाँच हो रही है…",
        "empty": "पहले URL दर्ज करें।",
        "invalid": "http:// या https:// से शुरू होने वाला सही URL दर्ज करें।",
        "error_conn": "API से कनेक्ट नहीं हो पाया। FastAPI सर्वर चल रहा है?",
        "result_title": "स्कैन परिणाम",
        "risk_high": "उच्च जोखिम", "risk_medium": "मध्यम जोखिम", "risk_low": "कम जोखिम",
        "verdict_high": "उच्च जोखिम", "verdict_medium": "मध्यम जोखिम", "verdict_safe": "सुरक्षित लगता है",
        "url_prefix": "URL:", "reasons_title": "यह क्यों चिह्नित हुआ",
        "link_title": "लिंक जाँच", "link_hint": "आपके URL में मिले लिंक। जिस पर भरोसा न हो उसे कभी न खोलें।",
        "pill_safe": "कोई खतरा नहीं", "pill_danger": "असुरक्षित", "pill_unknown": "अनजाँचा",
        "advice_title": "आपको क्या करना चाहिए",
        "raw_title": "सर्वर का कच्चा उत्तर देखें",
        "history_title": "🕘 हाल के स्कैन", "clear_history": "इतिहास साफ़ करें",
        "no_history": "अभी तक कोई स्कैन नहीं।", "history_cleared": "इतिहास साफ़ हो गया",
        "feat1_title": "Google Safe Browsing",
        "feat1_desc": "मैलवेयर, फ़िशिंग और अवांछित सॉफ़्टवेयर के लिए Google की लाइव थ्रेट सूचियों के खिलाफ सत्यापित।",
        "feat2_title": "पैटर्न विश्लेषण",
        "feat2_desc": "संदिग्ध URL पैटर्न आपके ब्राउज़र में ही पकड़े जाते हैं — कोई अपलोड नहीं।",
        "feat3_title": "तुरंत परिणाम",
        "feat3_desc": "एक क्लिक में स्पष्ट उच्च / मध्यम / निम्न परिणाम और सुझाव।",
        "footer_line1": "TrustCheck · सतर्क रहें। सुरक्षित रहें।",
        "footer_line2": "स्वचालित परिणाम गलत हो सकते हैं। महत्वपूर्ण लिंक स्वयं सत्यापित करें।",
    },
    "मराठी": {
        "lang": "भाषा", "dark": "🌙 डार्क मोड",
        "hero_tag": "✦ तुमचा डिजिटल सुरक्षा सहाय्यक",
        "hero_desc": "URL पेस्ट करा आणि TrustCheck कडून Google Safe Browsing विरुद्ध तपासा. काही सेकंदात स्पष्ट निकाल.",
        "scanner_title": "संशयास्पद URL स्कॅन करा",
        "scanner_sub": "वेबसाइट पत्ता पेस्ट करा. पासवर्ड, OTP किंवा बँकिंग माहिती देऊ नका.",
        "url_label": "वेबसाइट URL",
        "placeholder": "https://example.com/suspicious-path",
        "scan_btn": "✦ URL तपासा",
        "analyzing": "तपासणी सुरू…",
        "empty": "प्रथम URL टाका.",
        "invalid": "http:// किंवा https:// ने सुरू होणारा वैध URL टाका.",
        "error_conn": "API शी कनेक्ट होता आले नाही. FastAPI सर्व्हर सुरू आहे का?",
        "result_title": "स्कॅन निकाल",
        "risk_high": "उच्च धोका", "risk_medium": "मध्यम धोका", "risk_low": "कमी धोका",
        "verdict_high": "उच्च धोका", "verdict_medium": "मध्यम धोका", "verdict_safe": "सुरक्षित वाटते",
        "url_prefix": "URL:", "reasons_title": "हे का चिन्हांकित झाले",
        "link_title": "लिंक तपासणी", "link_hint": "तुमच्या URL मध्ये आढळलेल्या लिंक. ज्यावर विश्वास नाही ती कधीही उघडू नका.",
        "pill_safe": "धोका नाही", "pill_danger": "असुरक्षित", "pill_unknown": "तपासले नाही",
        "advice_title": "तुम्ही काय करावे",
        "raw_title": "सर्व्हरचा कच्चा प्रतिसाद पहा",
        "history_title": "🕘 अलीकडील स्कॅन", "clear_history": "इतिहास साफ करा",
        "no_history": "अजून कोणतीही तपासणी नाही.", "history_cleared": "इतिहास साफ झाला",
        "feat1_title": "Google Safe Browsing",
        "feat1_desc": "मालवेअर, फिशिंग आणि अवांछित सॉफ्टवेअरसाठी Google च्या लाइव्ह थ्रेट याद्यांविरुद्ध सत्यापित.",
        "feat2_title": "पॅटर्न विश्लेषण",
        "feat2_desc": "संशयास्पद URL पॅटर्न तुमच्या ब्राउझरमध्येच शोधले जातात — अपलोड नाही.",
        "feat3_title": "त्वरित निकाल",
        "feat3_desc": "एका क्लिकमध्ये स्पष्ट उच्च / मध्यम / कमी निकाल आणि सल्ला.",
        "footer_line1": "TrustCheck · सतर्क रहा. सुरक्षित रहा.",
        "footer_line2": "स्वयंचलित निकाल चुकीचे असू शकतात. महत्त्वाच्या लिंक स्वतः सत्यापित करा.",
    },
}

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
st.session_state.setdefault("lang", "English")
st.session_state.setdefault("dark", False)
st.session_state.setdefault("history", [])
st.session_state.setdefault("last_result", None)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
          <div style="font-size:1.7rem;">🛡️</div>
          <div>
            <div style="font-weight:800;font-size:1.15rem;line-height:1.1;">TrustCheck</div>
            <div style="font-size:.78rem;opacity:.7;">URL Threat Detection</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    t = T[st.session_state.lang]

    # --- CUSTOM LANGUAGE SWITCHER ---
    st.markdown(f'<p style="color:#fff;font-size:14px;font-weight:700;margin-bottom:6px;">{t["lang"]}</p>', unsafe_allow_html=True)
    
    langs = [("English", "English"), ("हिंदी", "हिंदी"), ("मराठी", "मराठी")]
    
    for display_name, lang_key in langs:
        is_active = st.session_state.lang == lang_key
        bg_color = "#ffffff" if is_active else "rgba(255,255,255,0.1)"
        text_color = "#472078" if is_active else "#ffffff"
        border = "1px solid #ffffff" if is_active else "1px solid rgba(255,255,255,0.2)"
        
        st.markdown(
            f"""
            <style>
                div[data-testid="stSidebar"] div.stButton > button[key="lang_btn_{lang_key}"] {{
                    background: {bg_color} !important;
                    color: {text_color} !important;
                    border: {border} !important;
                    font-weight: 700 !important;
                    border-radius: 8px !important;
                    margin-bottom: 4px !important;
                    text-align: left !important;
                    padding-left: 16px !important;
                }}
                div[data-testid="stSidebar"] div.stButton > button[key="lang_btn_{lang_key}"]:hover {{
                    background: {'#ffffff' if is_active else 'rgba(255,255,255,0.2)'} !important;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        
        if st.button(display_name, key=f"lang_btn_{lang_key}", use_container_width=True):
            st.session_state.lang = lang_key
            st.rerun()
    
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.divider()

    # --- DARK MODE TOGGLE ---
    dark_mode = st.toggle(t["dark"], value=st.session_state.dark, key="dark_mode_toggle")
    
    if dark_mode != st.session_state.dark:
        st.session_state.dark = dark_mode
        st.rerun()

# ---------------------------------------------------------------------------
# INJECT CSS AFTER toggle is read
# ---------------------------------------------------------------------------
theme = DARK if st.session_state.dark else LIGHT
st.markdown(build_css(theme, st.session_state.dark), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="tag">{t["hero_tag"]}</div>
      <h1>Check before you <span>click.</span></h1>
      <p>{t["hero_desc"]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="card">
      <h2>🔎 {t['scanner_title']}</h2>
      <p class="subtext">{t['scanner_sub']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("scan_form"):
    url = st.text_input(t["url_label"], placeholder=t["placeholder"], max_chars=2048)
    submitted = st.form_submit_button(t["scan_btn"], type="primary", use_container_width=True)

if submitted:
    candidate = (url or "").strip()
    if not candidate:
        st.warning(t["empty"])
    else:
        parsed = urlparse(candidate)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            st.error(t["invalid"])
        else:
            try:
                with st.spinner(t["analyzing"]):
                    # Corrected API call using the base URL
                    resp = requests.post(API_URL, json={"url": candidate}, timeout=45)
                if not resp.ok:
                    try:
                        detail = resp.json().get("detail", "Request failed.")
                    except Exception:
                        detail = "Request failed."
                    st.error(f"API error ({resp.status_code}): {detail}")
                else:
                    data = resp.json()
                    risk = str(data.get("risk_level", "")).lower()
                    if risk not in ("high", "medium", "low"):
                        risk = "high" if data.get("threat_found") else "low"
                    record = {
                        "url": data.get("url") or data.get("submitted_url") or candidate,
                        "risk": risk,
                        "prediction": str(data.get("prediction", "unknown")).lower(),
                        "message": data.get("message", ""),
                        "threat_matches": data.get("threat_matches", []),
                        "time": datetime.now().strftime("%b %d, %H:%M"),
                    }
                    st.session_state.last_result = record
                    st.session_state.history.insert(0, record)
                    st.session_state.history = st.session_state.history[:8]
            except requests.RequestException:
                st.error(t["error_conn"])

# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------
def render_gauge(risk: str) -> go.Figure:
    colors = {"high": "#dc2626", "medium": "#f59e0b", "low": "#16a34a"}
    values = {"high": 90, "medium": 55, "low": 12}
    c = colors.get(risk, "#8b5cf6")
    v = values.get(risk, 0)
    track = "#2c2248" if st.session_state.dark else "#ece6f7"
    text_color = "#efeaff" if st.session_state.dark else "#24183b"
    fig = go.Figure(go.Pie(
        values=[v, 100 - v], hole=0.72,
        marker_colors=[c, track], textinfo="none", hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0), height=200, width=200,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=str(v), x=0.5, y=0.5, font_size=30, showarrow=False, font_color=text_color)],
    )
    return fig


def risk_css_class(risk: str) -> str:
    return "safe" if risk == "low" else "warning" if risk == "medium" else "danger"


def risk_verdict(risk: str) -> str:
    return {"high": t["verdict_high"], "medium": t["verdict_medium"], "low": t["verdict_safe"]}.get(risk, "—")


def risk_level_label(risk: str) -> str:
    return {"high": t["risk_high"], "medium": t["risk_medium"], "low": t["risk_low"]}.get(risk, "—")


def advice_text(risk: str) -> str:
    sets = {
        "high": [
            "Do NOT visit this URL or enter any personal information.",
            "Never share OTPs, PINs or passwords — real organisations never ask for them.",
            "Report the link (Google Safe Browsing, or your local cybercrime authority).",
            "If you already visited and shared data, change your passwords and contact your bank.",
        ],
        "medium": [
            "Avoid opening this URL directly — verify it first.",
            "Type the domain manually into your browser if you know it.",
            "Check for look-alike spelling and suspicious subdomains.",
            "When in doubt, contact the company through its official website.",
        ],
        "low": [
            "No threats were found in Google Safe Browsing, but no tool is perfect.",
            "Still be careful with unexpected links and login requests.",
            "When in doubt, verify the sender using a different channel.",
        ],
    }
    items = sets.get(risk, sets["low"])
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
if st.session_state.last_result:
    r = st.session_state.last_result
    risk = r["risk"]
    st.markdown("---")
    st.markdown(f"## 📋 {t['result_title']}")

    col_gauge, col_info = st.columns([1, 2.2], gap="large")
    with col_gauge:
        st.plotly_chart(render_gauge(risk), use_container_width=False, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;font-weight:800;font-size:14px;'
            f'color:{ "#16a34a" if risk == "low" else "#f59e0b" if risk == "medium" else "#dc2626"};">'
            f'{risk_level_label(risk)}</div>', unsafe_allow_html=True,
        )
    with col_info:
        css = risk_css_class(risk)
        st.markdown(f'<span class="verdict {css}">{risk_verdict(risk)}</span>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="margin:8px 0 0;font-size:14px;line-height:1.6;">'
            f'<strong>{t["url_prefix"]}</strong> <code style="font-size:13px;">{r["url"]}</code></p>',
            unsafe_allow_html=True,
        )
        if r["message"]:
            st.markdown(f'<p style="margin:8px 0 0;opacity:.75;font-size:14px;">{r["message"]}</p>', unsafe_allow_html=True)

    if r["threat_matches"]:
        st.markdown(f"### ⚠ {t['reasons_title']}")
        for m in r["threat_matches"]:
            typ = m.get("threatType") or m.get("threat_type") or "Threat"
            plat = m.get("platformType") or ""
            url_ = (m.get("threat") or {}).get("url") or m.get("url") or ""
            label = f"{typ}{' (' + plat + ')' if plat else ''}{' — ' + url_ if url_ else ''}"
            st.markdown(f'<div class="reason">{label}</div>', unsafe_allow_html=True)

    st.markdown(f"### 🔗 {t['link_title']}")
    st.caption(t["link_hint"])
    status = "safe" if risk == "low" else ("danger" if risk == "high" else "unknown")
    pill_label = {"safe": t["pill_safe"], "danger": t["pill_danger"], "unknown": t["pill_unknown"]}[status]
    st.markdown(
        f'<div class="url-card {status}"><div style="flex:1"><code>{r["url"]}</code></div>'
        f'<span class="pill {status}">{pill_label}</span></div>', unsafe_allow_html=True,
    )

    st.markdown(f"### 🛡️ {t['advice_title']}")
    st.markdown(f'<div class="advice">{advice_text(risk)}</div>', unsafe_allow_html=True)

    with st.expander(t["raw_title"]):
        st.json(r)

# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
st.markdown("---")
hcol1, hcol2 = st.columns([4, 1], vertical_alignment="center")
with hcol1:
    st.markdown(f"## {t['history_title']}")
with hcol2:
    if st.button(t["clear_history"], use_container_width=True):
        st.session_state.history = []
        st.session_state.last_result = None
        st.toast(t["history_cleared"], icon="🗑️")
        st.rerun()

if st.session_state.history:
    score_map = {"high": 90, "medium": 55, "low": 12}
    for item in st.session_state.history:
        score = score_map.get(item["risk"], "–")
        st.markdown(
            f'<div class="history-item"><span class="score {item["risk"]}">{score}</span>'
            f'<span class="txt">{item["url"]}</span><span class="when">{item["time"]}</span></div>',
            unsafe_allow_html=True,
        )
else:
    st.caption(t["no_history"])

# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
st.markdown("---")
f1, f2, f3 = st.columns(3, gap="medium")
for col, icon, title, desc in [
    (f1, "🛡️", t["feat1_title"], t["feat1_desc"]),
    (f2, "🔗", t["feat2_title"], t["feat2_desc"]),
    (f3, "⚡", t["feat3_title"], t["feat3_desc"]),
]:
    with col:
        st.markdown(
            f'<div class="feature"><div class="icon">{icon}</div>'
            f'<strong>{title}</strong><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(f'<div class="footer">{t["footer_line1"]}<br/>{t["footer_line2"]}</div>', unsafe_allow_html=True)