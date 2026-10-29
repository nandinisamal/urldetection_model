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

API_URL = os.getenv("URL_DETECTION_API_URL", "http://127.0.0.1:8000/detect")
HEALTH_URL = API_URL.replace("/detect", "/health")

# ---------------------------------------------------------------------------
# THEME — single source of truth
# ---------------------------------------------------------------------------
LIGHT = {
    "bg": "linear-gradient(135deg,#faf8ff,#eee5ff)",
    "bg_solid": "#faf8ff",
    "card": "#ffffff",
    "panel": "#faf8ff",
    "input": "#fdfcff",
    "text": "#24183b",
    "muted": "#786d8c",
    "border": "#e7ddf8",
    "purple": "#6d28d9",
    "purple_dark": "#4c1d95",
    "track": "#ece6f7",
    "tag_bg": "#e9ddff",
    "tag_fg": "#4c1d95",
    "safe_bg": "#dcfce7", "safe_fg": "#166534",
    "warn_bg": "#fef3c7", "warn_fg": "#92400e",
    "danger_bg": "#fee2e2", "danger_fg": "#b91c1c",
    "shadow": "rgba(76,29,149,.09)",
    "code_bg": "#f4f4f5",
    "divider": "#e7ddf8",
}

DARK = {
    "bg": "linear-gradient(135deg,#0f0a1e,#1a1233)",
    "bg_solid": "#0f0a1e",
    "card": "#1a1230",
    "panel": "#211838",
    "input": "#221a3b",
    "text": "#efeaff",
    "muted": "#a79bc2",
    "border": "#3a2d5c",
    "purple": "#a78bfa",
    "purple_dark": "#ddd6fe",
    "track": "#2c2248",
    "tag_bg": "#2e2250",
    "tag_fg": "#ddd6fe",
    "safe_bg": "#123a22", "safe_fg": "#86efac",
    "warn_bg": "#4a3512", "warn_fg": "#fcd34d",
    "danger_bg": "#4a1620", "danger_fg": "#fca5a5",
    "shadow": "rgba(0,0,0,.5)",
    "code_bg": "#0f0a1e",
    "divider": "#3a2d5c",
}


def build_css(c: dict, is_dark: bool) -> str:
    """One CSS block per theme. Streamlit re-renders st.markdown on every run,
    so we emit ONE style tag — never stack. This forces the swap."""
    streamlit_bg = c["bg_solid"]
    return f"""
    <style id="trustcheck-theme">
      /* ============================================================
         FORCE everything to theme colors — this beats Streamlit's default
         ============================================================ */
      html, body,
      .stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stSidebar"],
      [data-testid="stSidebar"] > div,
      .main .block-container {{
        background: {streamlit_bg} !important;
        background-image: {c['bg']} !important;
        color: {c['text']} !important;
      }}

      /* All text — aggressive override */
      .stApp, .stApp *:not(svg):not(path) {{
        color: {c['text']};
      }}
      h1, h2, h3, h4, h5, h6 {{ color: {c['purple_dark']} !important; }}
      a {{ color: {c['purple']} !important; }}

      /* Sidebar specific */
      [data-testid="stSidebar"],
      [data-testid="stSidebar"] > div {{
        background: {c['card']} !important;
        border-right: 1px solid {c['border']} !important;
      }}

      /* Top toolbar / hamburger menu */
      [data-testid="stHeader"],
      [data-testid="stToolbar"] {{
        background: {streamlit_bg} !important;
        border-bottom: 1px solid {c['border']} !important;
      }}
      [data-testid="stHeader"] * {{ color: {c['text']} !important; }}

      /* Content area padding */
      .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1000px; }}

      /* ============================================================
         Hero
         ============================================================ */
      .hero {{ text-align: center; padding: 42px 24px 26px; }}
      .hero .tag {{
        display: inline-block;
        padding: 8px 15px;
        background: {c['tag_bg']};
        color: {c['tag_fg']} !important;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 14px;
      }}
      .hero h1 {{
        font-size: clamp(32px, 5vw, 48px);
        margin: 12px 0 10px;
        letter-spacing: -1.5px;
        color: {c['text']} !important;
      }}
      .hero h1 span {{ color: {c['purple']} !important; }}
      .hero p {{
        max-width: 620px;
        margin: auto;
        color: {c['muted']} !important;
        line-height: 1.7;
        font-size: 16px;
      }}

      /* ============================================================
         Cards
         ============================================================ */
      .card {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 18px;
        box-shadow: 0 12px 35px {c['shadow']};
      }}
      .card h2 {{ margin-top: 0; font-size: 20px; color: {c['purple_dark']} !important; }}
      .card .subtext {{ color: {c['muted']} !important; font-size: 14px; line-height: 1.6; margin-bottom: 18px; }}

      /* ============================================================
         Verdict pill
         ============================================================ */
      .verdict {{
        display: inline-block; padding: 7px 14px;
        border-radius: 30px; font-weight: 700; font-size: 14px;
        margin-bottom: 12px;
      }}
      .verdict.safe    {{ background: {c['safe_bg']};   color: {c['safe_fg']} !important; }}
      .verdict.warning {{ background: {c['warn_bg']};   color: {c['warn_fg']} !important; }}
      .verdict.danger  {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}

      /* ============================================================
         Reasons
         ============================================================ */
      .reason {{
        padding: 11px 14px 11px 40px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.55;
        position: relative;
        color: {c['text']} !important;
        overflow-wrap: anywhere;
      }}
      .reason::before {{ content: "⚠"; position: absolute; left: 14px; top: 10px; color: #f59e0b; }}

      /* ============================================================
         URL card
         ============================================================ */
      .url-card {{
        display: flex; gap: 12px; align-items: flex-start;
        padding: 12px 14px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-left-width: 4px;
        border-radius: 10px;
        font-size: 13px;
        margin-bottom: 8px;
      }}
      .url-card.safe    {{ border-left-color: #16a34a; }}
      .url-card.danger  {{ border-left-color: #dc2626; }}
      .url-card.unknown {{ border-left-color: {c['muted']}; }}
      .url-card code {{
        font-size: 13px; word-break: break-all;
        color: {c['text']} !important;
        background: transparent !important;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      }}
      .pill {{ padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; flex-shrink: 0; }}
      .pill.safe    {{ background: {c['safe_bg']};   color: {c['safe_fg']} !important; }}
      .pill.danger  {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}
      .pill.unknown {{ background: {c['track']};     color: {c['muted']} !important; }}

      /* ============================================================
         Advice
         ============================================================ */
      .advice {{
        padding: 14px 16px;
        border-radius: 12px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        font-size: 14px;
        line-height: 1.7;
        color: {c['text']} !important;
      }}
      .advice ul {{ margin: 6px 0 0; padding-left: 20px; }}
      .advice li {{ color: {c['text']} !important; }}

      /* ============================================================
         History
         ============================================================ */
      .history-item {{
        display: grid; grid-template-columns: 54px 1fr auto;
        gap: 12px; align-items: center;
        padding: 10px 12px;
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        font-size: 13px;
        margin-bottom: 8px;
      }}
      .history-item .score {{
        font-weight: 800; text-align: center;
        padding: 6px 0; border-radius: 8px; font-size: 13px;
      }}
      .score.safe    {{ background: {c['safe_bg']};   color: {c['safe_fg']} !important; }}
      .score.warning {{ background: {c['warn_bg']};   color: {c['warn_fg']} !important; }}
      .score.danger  {{ background: {c['danger_bg']}; color: {c['danger_fg']} !important; }}
      .score.unknown {{ background: {c['track']};     color: {c['muted']} !important; }}
      .history-item .txt {{
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 12px;
        color: {c['text']} !important;
      }}
      .history-item .when {{ color: {c['muted']} !important; font-size: 11px; white-space: nowrap; }}

      /* ============================================================
         Feature cards
         ============================================================ */
      .feature {{
        background: {c['card']};
        border: 1px solid {c['border']};
        padding: 20px 16px;
        border-radius: 15px;
        text-align: center;
        height: 100%;
      }}
      .feature .icon {{ font-size: 26px; margin-bottom: 8px; }}
      .feature strong {{ display: block; font-size: 14px; margin-bottom: 6px; color: {c['text']} !important; }}
      .feature p {{ font-size: 12px; color: {c['muted']} !important; line-height: 1.5; margin: 0; }}

      /* ============================================================
         Streamlit widgets — inputs, selects, buttons, alerts
         ============================================================ */
      /* Text input */
      div[data-baseweb="input"] > div {{
        background: {c['input']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
      }}
      div[data-baseweb="input"] > div:focus-within {{
        border-color: {c['purple']} !important;
        box-shadow: 0 0 0 3px rgba(109,40,217,.15) !important;
      }}
      div[data-baseweb="input"] input {{
        color: {c['text']} !important;
        background: transparent !important;
      }}
      div[data-baseweb="input"] input::placeholder {{ color: {c['muted']} !important; }}

      /* Selectbox */
      div[data-baseweb="select"] > div {{
        background: {c['input']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
        color: {c['text']} !important;
      }}
      div[data-baseweb="select"] * {{ color: {c['text']} !important; }}
      ul[role="listbox"] {{
        background: {c['card']} !important;
        border: 1px solid {c['border']} !important;
      }}
      ul[role="listbox"] li {{ color: {c['text']} !important; }}
      ul[role="listbox"] li:hover {{ background: {c['panel']} !important; }}

      /* Toggle */
      div[data-baseweb="toggle"] * {{ color: {c['text']} !important; }}
      [data-testid="stToggle"] label * {{ color: {c['text']} !important; }}

      /* Buttons */
      div.stButton > button,
      button[kind="primaryFormSubmit"] {{
        background: linear-gradient(100deg, #6d28d9, #8b5cf6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        min-height: 46px;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 8px 18px rgba(109,40,217,.25);
        transition: transform .15s, box-shadow .15s;
        width: 100%;
      }}
      div.stButton > button:hover,
      button[kind="primaryFormSubmit"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(109,40,217,.35);
      }}
      div.stButton > button[kind="secondary"] {{
        background: {c['panel']} !important;
        color: {c['purple_dark']} !important;
        border: 1px solid {c['border']} !important;
      }}

      /* Alerts */
      [data-testid="stAlert"] {{
        background: {c['panel']} !important;
        border: 1px solid {c['border']} !important;
        color: {c['text']} !important;
        border-radius: 12px !important;
      }}
      [data-testid="stAlert"] * {{ color: {c['text']} !important; }}

      /* Expander */
      details, [data-testid="stExpander"] {{
        background: {c['panel']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
      }}
      details summary, [data-testid="stExpander"] summary {{
        color: {c['purple_dark']} !important;
      }}
      [data-testid="stExpander"] * {{ color: {c['text']} !important; }}

      /* JSON viewer */
      [data-testid="stJson"] {{ background: {c['panel']} !important; border-radius: 10px; }}
      [data-testid="stJson"] * {{ color: {c['text']} !important; }}

      /* Code */
      pre, code, .stCode {{ background: {c['code_bg']} !important; color: {c['text']} !important; }}

      /* Divider */
      hr {{
        border: none !important;
        border-top: 1px solid {c['divider']} !important;
        margin: 18px 0 !important;
      }}

      /* Spinner */
      [data-testid="stSpinner"] * {{ color: {c['text']} !important; }}

      /* Toast */
      [data-testid="stToast"] {{
        background: {c['card']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
      }}

      /* Footer */
      .footer {{
        text-align: center; padding: 20px 0 10px;
        color: {c['muted']} !important; font-size: 12px; line-height: 1.6;
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
        "error_conn": "Could not connect to the API. Is FastAPI running on port 8000?",
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
        "test_conn": "🔌 Test connection",
        "server_online": "Server online", "server_offline": "Server offline",
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
        "error_conn": "API से कनेक्ट नहीं हो पाया। FastAPI पोर्ट 8000 पर चल रहा है?",
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
        "test_conn": "🔌 कनेक्शन जाँचें",
        "server_online": "सर्वर ऑनलाइन", "server_offline": "सर्वर ऑफ़लाइन",
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
        "error_conn": "API शी कनेक्ट होता आले नाही. FastAPI पोर्ट 8000 वर सुरू आहे का?",
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
        "test_conn": "🔌 कनेक्शन तपासा",
        "server_online": "सर्व्हर ऑनलाइन", "server_offline": "सर्व्हर ऑफलाइन",
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
# Sidebar — theme toggle drives CSS regeneration via st.session_state
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

    lang_names = ["English", "हिंदी", "मराठी"]
    st.session_state.lang = st.selectbox(
        T[st.session_state.lang]["lang"],
        lang_names,
        index=lang_names.index(st.session_state.lang),
    )
    t = T[st.session_state.lang]

    # Toggle — key ensures Streamlit rebuilds immediately when toggled
    st.session_state.dark = st.toggle(t["dark"], value=st.session_state.dark, key="dark_toggle")

    st.divider()
    if st.button(t["test_conn"], use_container_width=True):
        try:
            r = requests.get(HEALTH_URL, timeout=3)
            st.success(t["server_online"]) if r.ok else st.error(t["server_offline"])
        except Exception:
            st.error(t["server_offline"])

# ---------------------------------------------------------------------------
# INJECT CSS AFTER toggle is read → swap happens on the SAME rerun
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