import streamlit as st
import pdfplumber
import json
import re
import os
from groq import Groq
from tavily import TavilyClient

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactLens – AI Fact Checker",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load API keys from environment (set these in Render's dashboard) ─────────
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }

.stApp { background: #080c14 !important; }
.block-container {
    max-width: 780px !important;
    padding: 0 1.5rem 4rem !important;
    margin: 0 auto !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1220; }
::-webkit-scrollbar-thumb { background: #1e2d50; border-radius: 3px; }

.nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.6rem 0 1.4rem;
    border-bottom: 1px solid #131d30;
    margin-bottom: 3.5rem;
}
.nav-logo { font-family: 'Instrument Serif', serif; font-size: 1.45rem; color: #f0f4ff; letter-spacing: -0.01em; }
.nav-logo em { color: #5b8def; font-style: normal; }
.nav-tag { font-size: 0.68rem; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: #3a5080; background: #0d1525; border: 1px solid #1a2840; border-radius: 100px; padding: 4px 12px; }

.hero { text-align: center; padding: 0 0 3rem; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 7px; font-size: 0.72rem; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: #5b8def; margin-bottom: 1.4rem; }
.hero-eyebrow-dot { width: 6px; height: 6px; background: #5b8def; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.7); } }
.hero h1 { font-family: 'Instrument Serif', serif; font-size: clamp(2.4rem, 5vw, 3.5rem); font-weight: 400; color: #eef1fb; line-height: 1.08; letter-spacing: -0.02em; margin-bottom: 1rem; }
.hero h1 em { font-style: italic; background: linear-gradient(135deg, #5b8def 0%, #9b6dff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1rem; font-weight: 300; color: #4a6090; line-height: 1.7; max-width: 480px; margin: 0 auto 2.4rem; }

.features { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 3rem; }
.feature-pill { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; font-weight: 500; color: #5a7ab0; background: #0c1628; border: 1px solid #182540; border-radius: 100px; padding: 6px 14px; }
.fp-dot { width: 5px; height: 5px; border-radius: 50%; display: inline-block; }
.fp-blue   { background: #5b8def; }
.fp-purple { background: #9b6dff; }
.fp-teal   { background: #2ec4a7; }

[data-testid="stFileUploader"] { background: #0b1425 !important; border: 1.5px dashed #1c3058 !important; border-radius: 18px !important; padding: 2.5rem 2rem !important; text-align: center; }
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] p, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small { color: #3a5580 !important; font-size: 0.88rem !important; }
[data-testid="stFileUploader"] button { background: #0f1e38 !important; border: 1px solid #1e3a6e !important; border-radius: 10px !important; color: #7eb3ff !important; font-size: 0.82rem !important; font-family: 'DM Sans', sans-serif !important; padding: 0.4rem 1.1rem !important; }

[data-testid="stSuccess"] { background: #041a0d !important; border: 1px solid #0d4020 !important; border-radius: 12px !important; color: #3dba79 !important; }
[data-testid="stInfo"] { background: #08111e !important; border: 1px solid #162540 !important; border-radius: 12px !important; color: #4a7ab0 !important; font-size: 0.88rem !important; }

.stButton > button { background: linear-gradient(135deg, #1a50c0 0%, #6b3ec8 100%) !important; color: #fff !important; border: none !important; border-radius: 14px !important; padding: 0.8rem 0 !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.95rem !important; width: 100% !important; letter-spacing: 0.02em; transition: opacity 0.2s !important; margin-top: 1rem !important; }
.stButton > button:hover { opacity: 0.88 !important; }

[data-testid="stSpinner"] p { color: #4a6090 !important; font-size: 0.88rem !important; }

.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 2.5rem 0 2rem; }
.stat-card { background: #0b1525; border: 1px solid #131e35; border-radius: 14px; padding: 1.2rem 1rem; text-align: center; }
.stat-num { font-family: 'Instrument Serif', serif; font-size: 2.2rem; color: #5b8def; line-height: 1; margin-bottom: 6px; }
.stat-lbl { font-size: 0.68rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #2e4060; }

.sec-hdr { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.14em; color: #2e4565; border-bottom: 1px solid #111c30; padding-bottom: 0.7rem; margin: 2.5rem 0 1.4rem; }

.cc { background: #0b1525; border: 1px solid #131e35; border-radius: 18px; padding: 1.5rem 1.8rem; margin-bottom: 1rem; }
.cc-verified     { border-left: 3px solid #22c55e; }
.cc-inaccurate   { border-left: 3px solid #f59e0b; }
.cc-false        { border-left: 3px solid #ef4444; }
.cc-unverifiable { border-left: 3px solid #3a4a60; }

.cc-toprow { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 1rem; }
.cc-num { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; color: #2e4060; background: #0d1a2e; border: 1px solid #162035; border-radius: 100px; padding: 2px 10px; }
.cc-cat { font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.1em; color: #3d5a80; background: #0d1a2e; border: 1px solid #162035; border-radius: 100px; padding: 2px 10px; }
.vb-verified     { background:#031a0a; color:#4ade80; border:1px solid #0e4a22; padding:3px 12px; border-radius:100px; font-size:0.68rem; font-weight:600; }
.vb-inaccurate   { background:#1e0e00; color:#fbbf24; border:1px solid #5a3000; padding:3px 12px; border-radius:100px; font-size:0.68rem; font-weight:600; }
.vb-false        { background:#1a0505; color:#f87171; border:1px solid #5a1010; padding:3px 12px; border-radius:100px; font-size:0.68rem; font-weight:600; }
.vb-unverifiable { background:#0d1020; color:#60728a; border:1px solid #1a2540; padding:3px 12px; border-radius:100px; font-size:0.68rem; font-weight:600; }

.cc-claim { font-family: 'Instrument Serif', serif; font-size: 1.08rem; color: #c8d4ee; line-height: 1.55; margin-bottom: 1rem; }
.cc-div { border: none; border-top: 1px solid #101828; margin: 0.8rem 0; }
.cc-plabel { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #2d5090; margin-bottom: 0.35rem; }
.cc-ptext  { font-size: 0.85rem; color: #4a6890; line-height: 1.6; font-style: italic; }
.cc-elabel { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #4a3a80; margin: 0.8rem 0 0.35rem; }
.cc-etext  { font-size: 0.88rem; color: #8090b8; line-height: 1.6; }

.sum-bar { display: flex; gap: 10px; flex-wrap: wrap; margin: 0.8rem 0 2rem; }
.sum-pill { display: flex; align-items: center; gap: 7px; background: #0b1525; border: 1px solid #131e35; border-radius: 100px; padding: 6px 14px; font-size: 0.78rem; font-weight: 500; color: #3d5580; }
.d-g { width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block; }
.d-y { width:7px;height:7px;border-radius:50%;background:#f59e0b;display:inline-block; }
.d-r { width:7px;height:7px;border-radius:50%;background:#ef4444;display:inline-block; }
.d-s { width:7px;height:7px;border-radius:50%;background:#3a4a60;display:inline-block; }

.page-divider { border: none; border-top: 1px solid #0e1a28; margin: 3rem 0; }

.badge-wrap { display: flex; justify-content: center; margin: 3rem 0 2rem; }
.badge { background: #090e1c; border: 1px solid #182035; border-radius: 22px; padding: 2rem 2.5rem; text-align: center; max-width: 420px; width: 100%; position: relative; overflow: hidden; }
.badge-stripe { position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #5b8def, #9b6dff, #2ec4a7); }
.badge-issuer { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: #2e4060; margin-bottom: 0.6rem; }
.badge-title { font-family: 'Instrument Serif', serif; font-size: 1.35rem; color: #d0daf5; margin-bottom: 0.25rem; line-height: 1.3; }
.badge-sub { font-size: 0.78rem; color: #3d5580; margin-bottom: 1.2rem; }
.badge-seal { display: inline-flex; align-items: center; gap: 6px; background: #031a0a; border: 1px solid #0e4a22; border-radius: 100px; padding: 5px 16px; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #4ade80; }

.site-footer { text-align: center; padding: 1.5rem 0 0; border-top: 1px solid #0e1828; font-size: 0.76rem; color: #243040; }
.site-footer a { color: #2e4a70; text-decoration: none; }
.site-footer a:hover { color: #4a70a0; }
</style>
""", unsafe_allow_html=True)

# ── Nav ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav">
    <div class="nav-logo">Fact<em>Lens</em></div>
    <div class="nav-tag">AI Fact Checker</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        Powered by Groq &amp; Tavily
    </div>
    <h1>Every claim,<br><em>verified.</em></h1>
    <p class="hero-sub">
        Upload any PDF and FactLens extracts factual claims,
        explains why they matter, and cross-checks each one
        against live web sources in seconds.
    </p>
    <div class="features">
        <span class="feature-pill"><span class="fp-dot fp-blue"></span> Claim Extraction</span>
        <span class="feature-pill"><span class="fp-dot fp-purple"></span> Live Web Search</span>
        <span class="feature-pill"><span class="fp-dot fp-teal"></span> Instant Verdict</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.error("API keys are not configured. Set `GROQ_API_KEY` and `TAVILY_API_KEY` as environment variables on Render.")
    st.stop()

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_html(t):
    return (str(t or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def extract_json_array(text):
    text = re.sub(r"```json|```", "", text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass
    m = re.search(r'\[.*?\]', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(), strict=False)
        except Exception:
            pass
    return re.findall(r'"([^"]{10,})"', text) or []

def extract_json_object(text):
    text = re.sub(r"```json|```", "", text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass
    m = re.search(r'\{.*?\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(), strict=False)
        except Exception:
            pass
    return None

def get_category(claim_text):
    cl = claim_text.lower()
    for kws, cat in [
        (["diagnos","detect","disease","cancer","diabetes","heart"], "Diagnostics"),
        (["drug","treatment","therap","medicine"], "Treatment"),
        (["data","patient record","dataset","privacy","security"], "Data & Privacy"),
        (["bias","ethic","fairness","disparit"], "Ethics & Bias"),
        (["chatbot","virtual","assistant","workflow","admin","automat"], "AI Systems"),
        (["fund","financ","cost","resource"], "Funding"),
        (["legal","regulat","framework","law"], "Legal"),
    ]:
        if any(w in cl for w in kws):
            return cat
    return "General AI"

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop your PDF here, or click to browse",
    type="pdf",
    label_visibility="collapsed",
)

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        raw_text = "".join(page.extract_text() or "" for page in pdf.pages)
    char_count = len(raw_text)
    st.success(f"✓  **{uploaded_file.name}** loaded — {char_count:,} characters ready for analysis")

    if st.button("🔬  Extract & Verify All Claims"):

        # 1. Extract
        with st.spinner("Analysing document and extracting claims…"):
            client = Groq(api_key=GROQ_API_KEY)
            extract_prompt = f"""You are an expert fact-checking assistant. From the text below, extract between 3 and 8 specific, verifiable claims.

For each claim also write:
- "purpose": one sentence explaining WHY this claim matters (for a non-expert reader)
- "category": one of [Diagnostics, Treatment, Data & Privacy, Ethics & Bias, AI Systems, Funding, Legal, General AI]

Return ONLY a valid JSON array, no markdown.

Format:
[
  {{
    "claim": "The full factual claim.",
    "purpose": "This claim establishes that...",
    "category": "Diagnostics"
  }}
]

Text:
{raw_text[:4000]}"""

            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": extract_prompt}],
                temperature=0,
            )
            claims_data = extract_json_array(resp.choices[0].message.content.strip())

        # Normalise
        normalised = []
        for item in claims_data:
            if isinstance(item, dict):
                normalised.append({
                    "claim":    item.get("claim", str(item)),
                    "purpose":  item.get("purpose", ""),
                    "category": item.get("category", get_category(item.get("claim", ""))),
                })
            else:
                normalised.append({"claim": str(item), "purpose": "", "category": get_category(str(item))})

        if not normalised:
            st.error("Could not extract claims. The document may be too vague or image-only.")
            st.stop()

        # Stats
        st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-num">{len(normalised)}</div>
        <div class="stat-lbl">Claims Found</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{len(set(c['category'] for c in normalised))}</div>
        <div class="stat-lbl">Topics</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{char_count:,}</div>
        <div class="stat-lbl">Chars Scanned</div>
    </div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-hdr">Claim Verification Results</div>', unsafe_allow_html=True)

        # 2. Verify
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        counts = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
        icons  = {"Verified":"✓ Verified","Inaccurate":"⚠ Inaccurate","False":"✗ False","Unverifiable":"? Unverifiable"}

        for i, item in enumerate(normalised):
            claim    = item["claim"]
            purpose  = item["purpose"]
            category = item["category"]
            verdict     = "Unverifiable"
            explanation = "No web sources could be found to verify or contradict this claim."

            with st.spinner(f"Verifying claim {i+1} of {len(normalised)}…"):
                try:
                    snippets = ""
                    try:
                        sr = tavily.search(query=claim, search_depth="basic", max_results=3)
                        snippets = " ".join(r.get("content","") for r in sr.get("results",[]))
                    except Exception:
                        pass
                    if not snippets.strip():
                        try:
                            sr = tavily.search(query=" ".join(claim.split()[:8]), search_depth="basic", max_results=3)
                            snippets = " ".join(r.get("content","") for r in sr.get("results",[]))
                        except Exception:
                            pass
                    if snippets.strip():
                        vp = f"""You are a fact-checker. Based ONLY on the web results below, verify the claim.

Claim: "{claim}"
Web Results: {snippets[:2000]}

Return ONLY valid JSON, no markdown:
{{"verdict": "Verified", "explanation": "one sentence"}}

verdict must be exactly one of: "Verified", "Inaccurate", "False", "Unverifiable"
"""
                        vr = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role":"user","content":vp}],
                            temperature=0,
                        )
                        vd = extract_json_object(vr.choices[0].message.content.strip())
                        if vd:
                            verdict     = vd.get("verdict","Unverifiable")
                            explanation = vd.get("explanation","No explanation provided.")
                        if verdict not in counts:
                            verdict = "Unverifiable"
                except Exception as e:
                    verdict     = "Unverifiable"
                    explanation = f"Verification could not be completed: {e}"

            counts[verdict] = counts.get(verdict, 0) + 1

            sc  = safe_html(claim)
            sp  = safe_html(purpose) if purpose else "This claim supports a key assertion in the document."
            se  = safe_html(explanation)
            sca = safe_html(category)
            vl  = verdict.lower()
            il  = icons.get(verdict, verdict)

            st.markdown(f"""
<div class="cc cc-{vl}">
    <div class="cc-toprow">
        <span class="cc-num">CLAIM {i+1}</span>
        <span class="cc-cat">{sca}</span>
        <span class="vb-{vl}">{il}</span>
    </div>
    <div class="cc-claim">&#8220;{sc}&#8221;</div>
    <hr class="cc-div">
    <div class="cc-plabel">Why this claim matters</div>
    <div class="cc-ptext">{sp}</div>
    <div class="cc-elabel">Verification finding</div>
    <div class="cc-etext">{se}</div>
</div>""", unsafe_allow_html=True)

        # Summary
        dot_map = {"Verified":"d-g","Inaccurate":"d-y","False":"d-r","Unverifiable":"d-s"}
        pills = "".join(
            f'<div class="sum-pill"><span class="{dot_map[k]}"></span>{counts[k]} {k}</div>'
            for k in ["Verified","Inaccurate","False","Unverifiable"] if counts.get(k,0)>0
        )
        st.markdown(f'<div class="sec-hdr">Summary</div><div class="sum-bar">{pills}</div>', unsafe_allow_html=True)

else:
    st.info("Upload a PDF above to begin — no account or API key required.")

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

# ── Anthropic Badge ───────────────────────────────────────────────────────────
st.markdown("""
<div class="badge-wrap">
    <div class="badge">
        <div class="badge-stripe"></div>
        <div class="badge-issuer">Anthropic &nbsp;·&nbsp; Certificate of Completion</div>
        <div class="badge-title">AI Fluency Course</div>
        <div class="badge-sub">Awarded to <strong style="color:#8090c0">Vedika Kashyap</strong> &nbsp;·&nbsp; 2024</div>
        <div class="badge-seal">&#10022; &nbsp; Verified Completion</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
    Built by <a href="https://github.com/vedikakashyap" target="_blank">Vedika Kashyap</a>
    &nbsp;·&nbsp;
    Powered by <a href="https://groq.com" target="_blank">Groq</a>
    &amp; <a href="https://tavily.com" target="_blank">Tavily</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/vedikakashyap/Fact_Lence" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
