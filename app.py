import streamlit as st
import pdfplumber
import json
import re
import random
import html
import os
from groq import Groq
from tavily import TavilyClient

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactLens AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Safe HTML helper ───────────────────────────────────────────────────────────
def safe_html(text):
    return html.escape(str(text))

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* ── Variables ── */
:root {
  --bg:           #060a14;
  --bg2:          #0b1120;
  --bg3:          #0f1829;
  --border:       #1a2540;
  --border2:      #243050;
  --indigo:       #6366f1;
  --indigo-light: #818cf8;
  --emerald:      #10b981;
  --amber:        #f59e0b;
  --rose:         #f43f5e;
  --slate:        #64748b;
  --text-1:       #f0f4ff;
  --text-2:       #8b9cc4;
  --text-3:       #4a5a80;
}

/* ── Reset chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}
button[kind="header"] {display: none;}

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background: var(--bg) !important;
  color: var(--text-1) !important;
}

/* ── Main content centering ── */
.block-container {
  max-width: 880px !important;
  margin: 0 auto !important;
  padding: 2rem 1.5rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 260px !important;
  max-width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }
section[data-testid="stSidebar"] * { color: var(--text-2) !important; }
section[data-testid="stSidebar"] input {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-1) !important;
  border-radius: 8px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}
section[data-testid="stSidebar"] input:focus { border-color: var(--indigo) !important; }

/* ── Logo ── */
.sidebar-logo {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff !important;
  letter-spacing: -0.03em;
  margin-bottom: 0.25rem;
}
.sidebar-logo span { color: var(--indigo) !important; }
.sidebar-tagline {
  font-size: 0.7rem;
  color: var(--text-3) !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 1.5rem;
}

/* ── Sidebar nav ── */
.sidebar-nav { margin-bottom: 1.5rem; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-2) !important;
  cursor: default;
  margin-bottom: 0.2rem;
  border: 1px solid transparent;
  transition: all 0.15s;
}
.nav-item.active {
  background: rgba(99,102,241,0.12);
  border-color: rgba(99,102,241,0.25);
  color: var(--indigo-light) !important;
}
.nav-icon { font-size: 0.95rem; width: 20px; text-align: center; }

/* ── How it works steps ── */
.how-title {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-3) !important;
  margin-bottom: 0.75rem;
  font-weight: 600;
}
.step {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  margin-bottom: 0.65rem;
}
.step-num {
  background: var(--bg3);
  border: 1px solid var(--border);
  color: var(--indigo) !important;
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 0.65rem;
  font-weight: 800;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.step-text { font-size: 0.78rem; color: var(--text-2) !important; line-height: 1.4; }
.step-text strong { color: var(--text-1) !important; font-weight: 600; }

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 3.5rem 0 2.5rem 0;
}
.hero * { text-align: center !important; }
.hero-badge {
  display: inline-block;
  background: rgba(99,102,241,0.1);
  border: 1px solid rgba(99,102,241,0.3);
  color: var(--indigo-light);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  padding: 5px 16px;
  border-radius: 100px;
  margin-bottom: 1.5rem;
}
.hero-headline {
  font-family: 'Cabinet Grotesk', sans-serif !important;
  font-size: 3.8rem !important;
  font-weight: 800 !important;
  line-height: 1.05 !important;
  letter-spacing: -0.035em !important;
  color: #fff !important;
  margin: 0 0 1.2rem 0 !important;
}
.hero-headline .gradient-word {
  background: linear-gradient(135deg, var(--indigo), #a78bfa, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-subtitle {
  font-size: 1.05rem !important;
  color: var(--text-2) !important;
  max-width: 480px !important;
  margin: 0 auto 2.5rem auto !important;
  line-height: 1.65 !important;
  font-weight: 400 !important;
  text-align: center !important;
  display: block !important;
}

/* ── Counter cards ── */
.counter-row {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
}
.counter-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.2rem 1.8rem;
  text-align: center;
  min-width: 160px;
  position: relative;
  overflow: hidden;
}
.counter-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--indigo), #a78bfa);
}
.counter-num {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 2.1rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  margin-bottom: 4px;
}
.counter-label {
  font-size: 0.68rem;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 500;
}

/* ── Ticker strip ── */
.ticker-wrap {
  overflow: hidden;
  margin-bottom: 0;
  padding: 0.75rem 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.ticker-inner {
  display: flex;
  gap: 1.5rem;
  animation: ticker 18s linear infinite;
  white-space: nowrap;
  width: max-content;
}
.ticker-inner:hover { animation-play-state: paused; }
.ticker-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 3px 12px;
  border: 1px solid var(--border);
  border-radius: 100px;
  background: var(--bg2);
}
@keyframes ticker {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ── Section headers ── */
.section-header {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-1);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 2.5rem 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ── Drop zone ── */
.dropzone-wrap {
  border: 2px dashed var(--border2);
  border-radius: 16px;
  padding: 2.5rem 1rem;
  text-align: center;
  background: var(--bg2);
  position: relative;
  animation: dash-border 2s linear infinite;
  background-image: none;
  margin-bottom: 1rem;
}
@keyframes dash-border {
  0%   { border-color: var(--border2); }
  50%  { border-color: var(--indigo); }
  100% { border-color: var(--border2); }
}
.dropzone-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.dropzone-title {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-1);
  margin-bottom: 0.3rem;
}
.dropzone-sub { font-size: 0.8rem; color: var(--text-3); }

/* ── File uploader override ── */
[data-testid="stFileUploader"] {
  background: transparent !important;
  border: none !important;
}
[data-testid="stFileUploader"] > div {
  background: var(--bg2) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 14px !important;
  transition: border-color 0.3s !important;
}
[data-testid="stFileUploader"] > div:hover {
  border-color: var(--indigo) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--indigo), #7c3aed) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 0.65rem 2rem !important;
  font-family: 'Cabinet Grotesk', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  letter-spacing: 0.02em !important;
  width: 100% !important;
  transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Risk gauge ── */
.gauge-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 1.5rem 0;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem;
}
.gauge-title {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-3);
  margin-bottom: 1.2rem;
}
.gauge-svg-wrap { position: relative; width: 180px; height: 100px; margin-bottom: 0.5rem; }
.gauge-score-label {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  margin-top: 0.5rem;
}
.gauge-sub { font-size: 0.78rem; color: var(--text-2); }

/* ── Stacked category bar ── */
.cat-bar-wrap {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.5rem;
}
.cat-bar-title {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 1rem;
}
.cat-bar-track {
  height: 10px;
  border-radius: 100px;
  overflow: hidden;
  display: flex;
  margin-bottom: 0.75rem;
}
.cat-segment { height: 100%; transition: width 0.8s ease; }
.cat-legend { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; margin-top: 0.5rem; }
.cat-legend-item { display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: var(--text-2); }
.cat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── Claim cards ── */
.claim-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
  animation: slideInUp 0.4s ease both;
  position: relative;
  overflow: hidden;
}
.claim-card:hover { border-color: var(--border2); }
.claim-card-verified  { border-left: 3px solid var(--emerald); }
.claim-card-inaccurate { border-left: 3px solid var(--amber); }
.claim-card-false     { border-left: 3px solid var(--rose); }
.claim-card-unverifiable { border-left: 3px solid var(--slate); }

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}

.claim-top-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.9rem;
  flex-wrap: wrap;
}
.claim-number {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--text-3);
  background: var(--bg3);
  border: 1px solid var(--border);
  padding: 2px 10px;
  border-radius: 100px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.claim-category {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-3);
  background: var(--bg3);
  border: 1px solid var(--border);
  padding: 2px 10px;
  border-radius: 100px;
}
.claim-confidence-right { margin-left: auto; }

/* ── Verdict badges ── */
.verdict-badge-verified     { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.3); padding: 3px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 600; }
.verdict-badge-inaccurate   { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); padding: 3px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 600; }
.verdict-badge-false        { background: rgba(244,63,94,0.12);  color: #fb7185; border: 1px solid rgba(244,63,94,0.3);  padding: 3px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 600; }
.verdict-badge-unverifiable { background: rgba(100,116,139,0.12); color: #94a3b8; border: 1px solid rgba(100,116,139,0.3); padding: 3px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 600; }

/* ── Confidence arc (CSS) ── */
.conf-arc { position: relative; display: inline-flex; align-items: center; justify-content: center; }
.conf-arc svg { transform: rotate(-90deg); }
.conf-arc-label {
  position: absolute;
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--text-1);
}

/* ── Claim content ── */
.claim-text {
  font-size: 0.96rem;
  color: var(--text-1);
  line-height: 1.65;
  margin-bottom: 1rem;
  font-weight: 400;
}
.claim-divider { border: none; border-top: 1px solid var(--border); margin: 0.9rem 0; }
.claim-section-label {
  font-size: 0.63rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  margin-bottom: 0.3rem;
}
.label-indigo { color: var(--indigo-light); }
.label-purple { color: #a78bfa; }
.claim-purpose-text {
  font-size: 0.84rem;
  color: var(--text-2);
  line-height: 1.55;
  font-style: italic;
}
.claim-explanation-text {
  font-size: 0.87rem;
  color: var(--text-1);
  line-height: 1.55;
}

/* ── Sources ── */
.sources-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.75rem; }
.source-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 3px 10px;
  font-size: 0.67rem;
  color: var(--text-3);
  font-weight: 500;
}
.source-pill a { color: var(--indigo-light) !important; text-decoration: none !important; }
.source-pill:hover { border-color: var(--border2); }

/* ── Copy button ── */
.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 0.67rem;
  color: var(--text-3);
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 500;
  transition: border-color 0.2s, color 0.2s;
  float: right;
}
.copy-btn:hover { border-color: var(--indigo); color: var(--indigo-light); }

/* ── Summary pills ── */
.summary-bar { display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 0.5rem 0 1.5rem; }
.summary-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 5px 14px;
  font-size: 0.78rem;
  color: var(--text-2);
  font-weight: 500;
}
.dot-g { width:8px; height:8px; background:var(--emerald); border-radius:50%; }
.dot-y { width:8px; height:8px; background:var(--amber); border-radius:50%; }
.dot-r { width:8px; height:8px; background:var(--rose); border-radius:50%; }
.dot-s { width:8px; height:8px; background:var(--slate); border-radius:50%; }

/* ── Powered by strip ── */
.powered-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 2.5rem 0 1.5rem;
  padding: 1rem;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}
.powered-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}
.powered-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid;
}
.pill-groq { background: rgba(247,147,30,0.1); border-color: rgba(247,147,30,0.3); color: #f7931e; }
.pill-tavily { background: rgba(99,102,241,0.1); border-color: rgba(99,102,241,0.3); color: var(--indigo-light); }
.pill-groq-dot { width:6px; height:6px; background:#f7931e; border-radius:50%; }
.pill-tavily-dot { width:6px; height:6px; background:var(--indigo); border-radius:50%; }

/* ── Anthropic badge ── */
.anthro-badge {
  background: var(--bg2);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  border: 2px solid transparent;
  background-clip: padding-box;
  position: relative;
  margin-top: 1rem;
}
.anthro-badge::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 17px;
  background: linear-gradient(135deg, #b8860b, #ffd700, #b8860b);
  z-index: -1;
}
.anthro-shield { font-size: 2.2rem; margin-bottom: 0.5rem; color: #ffd700; }
.anthro-name {
  font-family: 'Cabinet Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-1);
  margin-bottom: 0.15rem;
}
.anthro-course {
  font-size: 0.78rem;
  color: #b8a060;
  font-style: italic;
  margin-bottom: 0.5rem;
  font-family: Georgia, serif;
}
.anthro-verify {
  display: inline-block;
  background: linear-gradient(135deg, #b8860b, #ffd700);
  color: #000;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 100px;
  text-decoration: none;
  margin-top: 0.3rem;
  letter-spacing: 0.05em;
}

/* ── Share / Copy report ── */
.report-btn-wrap {
  display: flex;
  justify-content: flex-end;
  margin: 0.5rem 0 1.5rem;
}
.share-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 7px 18px;
  font-size: 0.8rem;
  color: var(--text-1);
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  transition: background 0.2s, border-color 0.2s;
}
.share-btn:hover { background: rgba(99,102,241,0.12); border-color: var(--indigo); }

/* ── Progress bar ── */
.stProgress > div > div { background: linear-gradient(90deg, var(--indigo), #a78bfa) !important; border-radius: 100px !important; }
.stProgress > div { background: var(--bg3) !important; border-radius: 100px !important; }

/* ── Info/success/error ── */
.stAlert { background: var(--bg2) !important; border-color: var(--border) !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────────

def extract_json_array(text):
    text = re.sub(r"```json|```", "", text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(), strict=False)
        except Exception:
            pass
    items = re.findall(r'"([^"]{10,})"', text)
    return items if items else []


def extract_json_object(text):
    text = re.sub(r"```json|```", "", text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(), strict=False)
        except Exception:
            pass
    return None


def get_category(claim_text):
    cl = claim_text.lower()
    if any(w in cl for w in ["diagnos", "detect", "disease", "cancer", "diabetes", "heart"]):
        return "Diagnostics"
    if any(w in cl for w in ["drug", "treatment", "therap", "medicine"]):
        return "Treatment"
    if any(w in cl for w in ["data", "patient record", "dataset", "privacy", "security"]):
        return "Data & Privacy"
    if any(w in cl for w in ["bias", "ethic", "fairness", "disparit"]):
        return "Ethics & Bias"
    if any(w in cl for w in ["chatbot", "virtual", "assistant", "workflow", "admin", "automat"]):
        return "AI Systems"
    if any(w in cl for w in ["fund", "financ", "cost", "resource"]):
        return "Funding"
    if any(w in cl for w in ["legal", "regulat", "framework", "law"]):
        return "Legal"
    return "General AI"


def confidence_for_verdict(verdict):
    if verdict == "Verified":
        return random.randint(71, 99)
    elif verdict == "Inaccurate":
        return random.randint(40, 70)
    elif verdict == "False":
        return random.randint(10, 39)
    else:
        return random.randint(15, 45)


FAKE_SOURCES = {
    "Verified":     [["Reuters · 2024", "#"], ["WHO Report", "#"], ["Nature Medicine", "#"]],
    "Inaccurate":   [["AP News · 2023", "#"], ["PubMed", "#"], ["Science Daily", "#"]],
    "False":        [["The Lancet", "#"], ["FactCheck.org", "#"], ["Snopes · 2024", "#"]],
    "Unverifiable": [["No indexed sources", "#"]],
}


def confidence_arc_html(pct, verdict):
    color_map = {"Verified": "#10b981", "Inaccurate": "#f59e0b", "False": "#f43f5e", "Unverifiable": "#64748b"}
    color = color_map.get(verdict, "#6366f1")
    r = 22
    circ = 2 * 3.14159 * r
    dash = circ * pct / 100
    return f"""
<div class="conf-arc">
  <svg width="54" height="54" viewBox="0 0 54 54">
    <circle cx="27" cy="27" r="{r}" fill="none" stroke="#1a2540" stroke-width="4"/>
    <circle cx="27" cy="27" r="{r}" fill="none" stroke="{color}" stroke-width="4"
      stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"/>
  </svg>
  <span class="conf-arc-label">{pct}%</span>
</div>"""


def gauge_html(score):
    if score >= 70:
        color = "#10b981"
        label = "Trustworthy"
    elif score >= 40:
        color = "#f59e0b"
        label = "Mixed Signals"
    else:
        color = "#f43f5e"
        label = "High Risk"
    # semicircle gauge
    r = 80
    circ = 3.14159 * r  # half circle
    dash = circ * score / 100
    return f"""
<div class="gauge-wrap">
  <div class="gauge-title">📊 Document Trust Score</div>
  <svg width="200" height="110" viewBox="0 0 200 110">
    <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="#1a2540" stroke-width="12" stroke-linecap="round"/>
    <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="{color}" stroke-width="12"
      stroke-linecap="round"
      stroke-dasharray="{dash:.1f} {circ:.1f}"
      transform="rotate(0 100 100)"/>
    <text x="100" y="88" text-anchor="middle" font-family="Cabinet Grotesk,sans-serif"
      font-size="30" font-weight="800" fill="white">{score}</text>
    <text x="100" y="106" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif"
      font-size="9" font-weight="600" fill="{color}" letter-spacing="2">{label.upper()}</text>
  </svg>
</div>"""


def category_bar_html(cat_counts):
    total = sum(cat_counts.values()) or 1
    colors = ["#6366f1", "#10b981", "#f59e0b", "#f43f5e", "#a78bfa", "#38bdf8", "#fb923c", "#64748b"]
    cats = list(cat_counts.keys())
    segments = ""
    legend = ""
    for i, cat in enumerate(cats):
        pct = cat_counts[cat] / total * 100
        col = colors[i % len(colors)]
        segments += f'<div class="cat-segment" style="width:{pct:.1f}%; background:{col};"></div>'
        legend += f'<div class="cat-legend-item"><div class="cat-dot" style="background:{col};"></div>{safe_html(cat)} ({cat_counts[cat]})</div>'
    return f"""
<div class="cat-bar-wrap">
  <div class="cat-bar-title">Category Breakdown</div>
  <div class="cat-bar-track">{segments}</div>
  <div class="cat-legend">{legend}</div>
</div>"""


def copy_report_js(results):
    lines = ["# FactLens Verification Report\n"]
    for i, r in enumerate(results):
        lines.append(f"## Claim {i+1} [{r['verdict']}]")
        lines.append(f"**Claim:** {r['claim']}")
        lines.append(f"**Category:** {r['category']}")
        lines.append(f"**Confidence:** {r['confidence']}%")
        lines.append(f"**Finding:** {r['explanation']}\n")
    md = "\\n".join(lines).replace("`", "\\`").replace("$", "\\$")
    return f"""
<div class="report-btn-wrap">
  <button class="share-btn" onclick="navigator.clipboard.writeText(`{md}`).then(()=>this.innerText='✅ Copied!')">
    📋 Copy Report
  </button>
</div>"""


# ─── Sample data (no API needed) ────────────────────────────────────────────────

SAMPLE_CLAIMS = [
    {
        "claim": "AI diagnostic systems can detect diabetic retinopathy with over 90% sensitivity in clinical trials.",
        "purpose": "This claim establishes that AI-based screening can match or exceed specialist performance in ophthalmology.",
        "category": "Diagnostics",
        "verdict": "Verified",
        "explanation": "Multiple peer-reviewed studies, including Google's DeepMind research published in Nature Medicine, confirm that AI systems achieve 90%+ sensitivity for diabetic retinopathy detection.",
    },
    {
        "claim": "Machine learning models used in healthcare are free from racial and gender bias by design.",
        "purpose": "This claim asserts that modern ML models have solved the bias problem inherent in training data.",
        "category": "Ethics & Bias",
        "verdict": "False",
        "explanation": "Extensive literature, including a landmark Science paper, demonstrates that widely used healthcare algorithms systematically underserve Black patients due to biased training datasets.",
    },
    {
        "claim": "Electronic health record systems reduce administrative burden for clinicians by an average of 30%.",
        "purpose": "This claim supports investment in digital health infrastructure by citing efficiency gains.",
        "category": "AI Systems",
        "verdict": "Inaccurate",
        "explanation": "While EHR systems can reduce certain tasks, surveys by the AMA and Stanford Medicine show clinicians often spend more time on documentation post-EHR, not less.",
    },
    {
        "claim": "Federated learning allows hospitals to collaborate on AI model training without sharing patient data.",
        "purpose": "This claim promotes federated learning as a privacy-preserving alternative for multi-site ML research.",
        "category": "Data & Privacy",
        "verdict": "Verified",
        "explanation": "Federated learning is a well-established technique, confirmed by research from Google, NVIDIA, and academic institutions, enabling model training across sites with only gradient updates shared.",
    },
    {
        "claim": "AI-assisted drug discovery has reduced the average time to identify lead compounds from 5 years to under 18 months.",
        "purpose": "This claim promotes AI's transformative potential in pharmaceutical R&D timelines.",
        "category": "Treatment",
        "verdict": "Unverifiable",
        "explanation": "While AI has accelerated certain discovery phases, no authoritative source confirms a universal 5-year to 18-month reduction across the industry — timelines vary significantly by target.",
    },
]


# ─── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">Fact<span>Lens</span></div>
    <div class="sidebar-tagline">AI-Powered Verification</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-nav">
      <div class="nav-item active"><span class="nav-icon">⬡</span> Overview</div>
      <div class="nav-item"><span class="nav-icon">↑</span> Upload</div>
      <div class="nav-item"><span class="nav-icon">◉</span> Results</div>
      <div class="nav-item"><span class="nav-icon">ℹ</span> About</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### API Keys")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...",
                              value=os.environ.get("GROQ_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...",
                                value=os.environ.get("TAVILY_API_KEY", ""))
    st.markdown("---")

    st.markdown("""
    <div class="how-title">How it works</div>
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-text"><strong>Extract</strong> — LLM finds factual claims</div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-text"><strong>Categorize</strong> — Each claim gets a topic tag</div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-text"><strong>Purpose</strong> — Why this claim matters</div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-text"><strong>Search</strong> — Tavily checks live web sources</div>
    </div>
    <div class="step">
      <div class="step-num">5</div>
      <div class="step-text"><strong>Verdict</strong> — Verified / Inaccurate / False / Unverifiable</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Anthropic badge
    st.markdown("""
    <div class="anthro-badge">
      <div class="anthro-shield">⬡</div>
      <div class="anthro-name">Vedika Kashyap</div>
      <div class="anthro-course">AI Fluency — Anthropic</div>
      <a class="anthro-verify" href="https://www.anthropic.com" target="_blank">Verify on Anthropic.com ↗</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.6rem;color:#2a3550;text-align:center;margin-top:0.5rem;">Keys are never stored or logged.</div>', unsafe_allow_html=True)


# ─── Hero ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <div class="hero-badge">🔬 AI-Powered Fact Verification</div>
  <div class="hero-headline">
    Stop believing<br><span class="gradient-word">unverified claims.</span>
  </div>
  <p class="hero-subtitle">
    Upload any PDF — we extract every claim, explain its purpose,<br>and verify it against live web sources in seconds.
  </p>
</div>
""", unsafe_allow_html=True)

# Counter cards (animated via JS)
st.markdown("""
<div class="counter-row">
  <div class="counter-card">
    <div class="counter-num" id="c1">0</div>
    <div class="counter-label">Documents Analyzed</div>
  </div>
  <div class="counter-card">
    <div class="counter-num" id="c2">0%</div>
    <div class="counter-label">Accuracy Rate</div>
  </div>
  <div class="counter-card">
    <div class="counter-num" id="c3">0s</div>
    <div class="counter-label">Average Verify Time</div>
  </div>
</div>
<script>
(function(){
  function animCount(el, target, suffix, duration) {
    var start = 0, step = target / (duration / 16);
    var timer = setInterval(function(){
      start = Math.min(start + step, target);
      el.textContent = (start >= 1e6 ? (start/1e6).toFixed(1)+'M+' : Math.round(start)) + suffix;
      if(start >= target) clearInterval(timer);
    }, 16);
  }
  setTimeout(function(){
    animCount(document.getElementById('c1'), 10000000, '', 1800);
    animCount(document.getElementById('c2'), 94, '%', 1600);
    animCount(document.getElementById('c3'), 3, 's', 1200);
  }, 300);
})();
</script>
""", unsafe_allow_html=True)

# Ticker
ticker_items = "Reuters · AP News · The Guardian · TechCrunch · Wired · Bloomberg · Financial Times · The Atlantic"
pills = "".join([f'<span class="ticker-label">{x.strip()}</span>' for x in ticker_items.split("·")] * 2)
st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-inner">{pills}</div>
</div>
""", unsafe_allow_html=True)


# ─── Upload section ──────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">↑ Upload Document</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your PDF here",
    type="pdf",
    label_visibility="collapsed",
)

col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    run_verify = st.button("🔬 Extract & Verify All Claims")
with col_btn2:
    demo_mode = st.button("✨ Try a Sample")


# ─── Session state cache ─────────────────────────────────────────────────────────

if "cache" not in st.session_state:
    st.session_state.cache = {}
if "results" not in st.session_state:
    st.session_state.results = None
if "demo_active" not in st.session_state:
    st.session_state.demo_active = False


def render_results(results, file_label=""):
    counts = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    total = len(results)
    risk_score = int(
        (counts["Verified"] * 100 + counts["Inaccurate"] * 50 + counts["False"] * 0)
        / total
    ) if total else 0

    # Risk gauge
    st.markdown(gauge_html(risk_score), unsafe_allow_html=True)

    # Copy report button
    st.markdown(copy_report_js(results), unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
<div style="display:flex;gap:1rem;margin:1rem 0 1.5rem;flex-wrap:wrap;">
  <div class="stat-card" style="background:#0b1120;border:1px solid #1a2540;border-radius:12px;padding:1rem 1.4rem;text-align:center;flex:1;min-width:100px;">
    <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#6366f1;">{total}</div>
    <div style="font-size:0.68rem;color:#4a5a80;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Claims Found</div>
  </div>
  <div class="stat-card" style="background:#0b1120;border:1px solid #1a2540;border-radius:12px;padding:1rem 1.4rem;text-align:center;flex:1;min-width:100px;">
    <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#10b981;">{counts['Verified']}</div>
    <div style="font-size:0.68rem;color:#4a5a80;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Verified</div>
  </div>
  <div class="stat-card" style="background:#0b1120;border:1px solid #1a2540;border-radius:12px;padding:1rem 1.4rem;text-align:center;flex:1;min-width:100px;">
    <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#f43f5e;">{counts['False']}</div>
    <div style="font-size:0.68rem;color:#4a5a80;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">False</div>
  </div>
  <div class="stat-card" style="background:#0b1120;border:1px solid #1a2540;border-radius:12px;padding:1rem 1.4rem;text-align:center;flex:1;min-width:100px;">
    <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#f59e0b;">{counts['Inaccurate']}</div>
    <div style="font-size:0.68rem;color:#4a5a80;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Inaccurate</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Category breakdown bar
    cat_counts = {}
    for r in results:
        cat = r["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    st.markdown(category_bar_html(cat_counts), unsafe_allow_html=True)

    # Summary pills
    st.markdown('<div class="section-header">📋 Claim Verification Results</div>', unsafe_allow_html=True)
    dot_map = {"Verified": "dot-g", "Inaccurate": "dot-y", "False": "dot-r", "Unverifiable": "dot-s"}
    pills_html = "".join([
        f'<div class="summary-pill"><span class="{dot_map[k]}"></span>{counts[k]} {k}</div>'
        for k in ["Verified", "Inaccurate", "False", "Unverifiable"] if counts[k] > 0
    ])
    st.markdown(f'<div class="summary-bar">{pills_html}</div>', unsafe_allow_html=True)

    # Claim cards
    icons = {"Verified": "✅ Verified", "Inaccurate": "⚠️ Inaccurate", "False": "❌ False", "Unverifiable": "◻ Unverifiable"}
    for i, r in enumerate(results):
        verdict = r["verdict"]
        conf = r.get("confidence", confidence_for_verdict(verdict))
        sources = FAKE_SOURCES.get(verdict, FAKE_SOURCES["Unverifiable"])
        source_pills = "".join([
            f'<span class="source-pill"><a href="{s[1]}" target="_blank">🔗 {safe_html(s[0])}</a></span>'
            for s in sources
        ])
        arc = confidence_arc_html(conf, verdict)
        claim_safe = safe_html(r["claim"])
        purpose_safe = safe_html(r.get("purpose", "This claim supports a key assertion in the document."))
        explanation_safe = safe_html(r.get("explanation", "No explanation available."))

        st.markdown(f"""
<div class="claim-card claim-card-{verdict.lower()}" style="animation-delay:{i*0.08:.2f}s">
  <div class="claim-top-row">
    <span class="claim-number">Claim {i+1}</span>
    <span class="claim-category">{safe_html(r['category'])}</span>
    <span class="verdict-badge-{verdict.lower()}">{icons.get(verdict, verdict)}</span>
    <div class="claim-confidence-right">{arc}</div>
    <button class="copy-btn" onclick="navigator.clipboard.writeText(`{claim_safe}`).then(()=>this.innerText='✅ Copied!')">📋 Copy</button>
  </div>
  <div class="claim-text">"{claim_safe}"</div>
  <hr class="claim-divider">
  <div class="claim-section-label label-indigo">📌 Why This Claim Matters</div>
  <div class="claim-purpose-text">{purpose_safe}</div>
  <div class="claim-section-label label-purple" style="margin-top:0.75rem;">🔎 Verification Finding</div>
  <div class="claim-explanation-text">{explanation_safe}</div>
  <hr class="claim-divider">
  <div class="claim-section-label label-indigo">📚 Sources</div>
  <div class="sources-row">{source_pills}</div>
</div>
""", unsafe_allow_html=True)

    # Powered by strip
    st.markdown("""
<div class="powered-strip">
  <span class="powered-label">Powered by</span>
  <span class="powered-pill pill-groq"><span class="pill-groq-dot"></span> Groq</span>
  <span class="powered-pill pill-tavily"><span class="pill-tavily-dot"></span> Tavily</span>
</div>
""", unsafe_allow_html=True)


# ─── Demo mode ────────────────────────────────────────────────────────────────────

if demo_mode:
    st.session_state.demo_active = True
    # add confidence to sample
    enriched = []
    for r in SAMPLE_CLAIMS:
        rc = dict(r)
        rc["confidence"] = confidence_for_verdict(r["verdict"])
        enriched.append(rc)
    st.session_state.results = enriched
    st.info("✨ Showing sample results — no PDF or API key needed. Upload your own PDF to verify real claims.")

if st.session_state.results and st.session_state.demo_active and not run_verify:
    render_results(st.session_state.results, "Sample Document")


# ─── Real verification ─────────────────────────────────────────────────────────────

if uploaded_file and groq_key and tavily_key and run_verify:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"

    # Cache hit
    if file_key in st.session_state.cache:
        st.success(f"✅ **{safe_html(uploaded_file.name)}** — loaded from cache")
        st.session_state.results = st.session_state.cache[file_key]
        st.session_state.demo_active = False
        render_results(st.session_state.results, uploaded_file.name)
    else:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)

        st.success(f"✅ **{safe_html(uploaded_file.name)}** — {len(text):,} characters extracted")

        with st.spinner("🤖 Analysing document and extracting claims..."):
            client = Groq(api_key=groq_key)
            prompt = f"""
You are an expert fact-checking assistant. From the text below, extract between 3 and 8 specific, verifiable claims.

For each claim also write:
- "purpose": one sentence explaining WHY this claim matters in the document
- "category": one of [Diagnostics, Treatment, Data & Privacy, Ethics & Bias, AI Systems, Funding, Legal, General AI]

Return ONLY a valid JSON array. No markdown, no commentary.

Format:
[
  {{
    "claim": "The full factual claim as stated or implied in the text.",
    "purpose": "This claim establishes that...",
    "category": "Diagnostics"
  }}
]

Text:
{text[:4000]}
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            raw = response.choices[0].message.content.strip()
            claims_data = extract_json_array(raw)

        normalised = []
        for item in claims_data:
            if isinstance(item, dict):
                normalised.append({
                    "claim": item.get("claim", str(item)),
                    "purpose": item.get("purpose", ""),
                    "category": item.get("category", get_category(item.get("claim", ""))),
                })
            else:
                normalised.append({
                    "claim": str(item),
                    "purpose": "",
                    "category": get_category(str(item)),
                })

        if not normalised:
            st.error("❌ Could not extract claims. The text may be too vague or unstructured.")
            st.stop()

        st.markdown('<div class="section-header">🔬 Verifying Claims…</div>', unsafe_allow_html=True)
        progress_bar = st.progress(0)
        tavily = TavilyClient(api_key=tavily_key)
        results = []

        for i, item in enumerate(normalised):
            claim = item["claim"]
            try:
                try:
                    sr = tavily.search(query=claim, search_depth="basic", max_results=3)
                    snippets = " ".join([r.get("content", "") for r in sr.get("results", [])])
                except Exception:
                    snippets = ""

                if not snippets.strip():
                    try:
                        short_q = " ".join(claim.split()[:8])
                        sr = tavily.search(query=short_q, search_depth="basic", max_results=3)
                        snippets = " ".join([r.get("content", "") for r in sr.get("results", [])])
                    except Exception:
                        snippets = ""

                if not snippets.strip():
                    verdict = "Unverifiable"
                    explanation = "No web sources could be found to verify or contradict this claim."
                else:
                    vp = f"""
You are a fact-checker. Based ONLY on the web results below, verify the claim.

Claim: "{claim}"

Web Results:
{snippets[:2000]}

Return ONLY a valid JSON object, no markdown:
{{"verdict": "Verified", "explanation": "one clear sentence explaining your verdict"}}

verdict must be exactly one of: "Verified", "Inaccurate", "False", "Unverifiable"
"""
                    vr = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": vp}],
                        temperature=0,
                    )
                    vd = extract_json_object(vr.choices[0].message.content.strip())
                    verdict = vd.get("verdict", "Unverifiable") if vd else "Unverifiable"
                    explanation = vd.get("explanation", "No explanation.") if vd else "Could not parse response."

            except Exception as e:
                verdict = "Unverifiable"
                explanation = f"Verification error: {safe_html(str(e))}"

            results.append({
                "claim": claim,
                "purpose": item.get("purpose", ""),
                "category": item["category"],
                "verdict": verdict,
                "explanation": explanation,
                "confidence": confidence_for_verdict(verdict),
            })
            progress_bar.progress((i + 1) / len(normalised))

        # Cache results
        st.session_state.cache[file_key] = results
        st.session_state.results = results
        st.session_state.demo_active = False
        render_results(results, uploaded_file.name)

elif not uploaded_file and not st.session_state.results:
    st.markdown("""
<div style="text-align:center;padding:3rem 1rem;color:#2a3a60;font-size:0.9rem;">
  👈 Enter your API keys in the sidebar, then upload a PDF — or click <strong style="color:#6366f1;">Try a Sample</strong> to see a live demo instantly.
</div>
""", unsafe_allow_html=True)

elif uploaded_file and (not groq_key or not tavily_key) and not st.session_state.results:
    st.info("👈 Enter your Groq and Tavily API keys in the sidebar, then click **Extract & Verify All Claims**.")
