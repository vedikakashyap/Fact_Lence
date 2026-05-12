import streamlit as st
import pdfplumber
import json
import re
from groq import Groq
from tavily import TavilyClient
import os

st.set_page_config(page_title="FactLens AI", page_icon="🔬", layout="wide")

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0B0F1A; color: #E8EDFB; }

.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewBlockContainer"] { padding: 0 !important; }
section[data-testid="stMain"] > div:first-child { padding-top: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] { gap: 0 !important; }
[data-testid="column"] { padding: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; padding: 0 !important; }
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; margin: 0 !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0B0F1A; }
::-webkit-scrollbar-thumb { background: #2A3A62; border-radius: 3px; }
html { scroll-behavior: smooth; }

.fl-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 56px;
  background: rgba(11,15,26,0.9);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  position: sticky; top: 0; z-index: 100;
  backdrop-filter: blur(14px);
}
.fl-logo { font-family:'Syne',sans-serif; font-size:22px; font-weight:700; color:#fff; letter-spacing:-0.5px; }
.fl-logo span { color:#7B8FD4; }
.fl-nav-links { display:flex; gap:32px; }
.fl-nav-links a { font-size:13px; color:rgba(255,255,255,0.42); text-decoration:none; }
.fl-nav-links a:hover { color:#fff; }
.fl-nav-btn { background:#2A3F8F; color:#C8D4F8; font-size:13px; font-weight:500; padding:8px 22px; border-radius:10px; border:none; cursor:pointer; text-decoration:none; }

.fl-hero { background:#0B0F1A; text-align:center; padding:72px 24px 32px; position:relative; overflow:hidden; }
.fl-hero-glow { position:absolute; top:-80px; left:50%; transform:translateX(-50%); width:700px; height:420px; background:rgba(42,63,143,0.13); border-radius:50%; filter:blur(80px); pointer-events:none; }
.fl-badge { display:inline-flex; align-items:center; gap:8px; background:rgba(42,63,143,0.18); border:1px solid rgba(123,143,212,0.28); color:#A0B4F0; font-size:11px; letter-spacing:0.12em; text-transform:uppercase; padding:5px 16px; border-radius:100px; margin-bottom:24px; }
.fl-badge-dot { width:6px; height:6px; border-radius:50%; background:#7B8FD4; }
.fl-hero h1 { font-family:'Syne',sans-serif; font-size:54px; font-weight:800; color:#fff; line-height:1.06; letter-spacing:-1.2px; margin-bottom:18px; }
.fl-hero h1 em { font-style:normal; color:#7B8FD4; }
.fl-hero-sub { font-size:16px; color:rgba(255,255,255,0.38); max-width:460px; margin:0 auto; line-height:1.75; }

.fl-input-card { background:rgba(255,255,255,0.045); border:1px solid rgba(255,255,255,0.11); border-radius:18px; padding:20px 22px; }
.fl-input-hint { font-size:11px; color:rgba(255,255,255,0.22); text-align:center; margin-top:8px; padding-bottom:2px; }

.fl-stats-zone { background:#0B0F1A; padding:20px 0 60px; display:flex; justify-content:center; }
.fl-stats-row { display:flex; border:1px solid rgba(255,255,255,0.08); border-radius:14px; overflow:hidden; }
.fl-stat { padding:14px 28px; text-align:center; border-right:1px solid rgba(255,255,255,0.08); }
.fl-stat:last-child { border-right:none; }
.fl-stat-n { font-family:'Syne',sans-serif; font-size:22px; font-weight:700; color:#7B8FD4; }
.fl-stat-l { font-size:11px; color:rgba(255,255,255,0.28); text-transform:uppercase; letter-spacing:0.08em; margin-top:3px; }

.stSelectbox label, .stTextArea label, .stTextInput label, .stFileUploader label { display:none !important; }
.stSelectbox > div > div { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.11) !important; border-radius:10px !important; color:#C8D4F0 !important; font-size:13px !important; font-family:'DM Sans',sans-serif !important; }
.stTextArea textarea { background:rgba(255,255,255,0.03) !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:10px !important; color:#C8D4F0 !important; font-family:'DM Sans',sans-serif !important; font-size:14px !important; resize:none !important; line-height:1.65 !important; }
.stTextArea textarea::placeholder { color:rgba(255,255,255,0.18) !important; }
.stTextArea textarea:focus { border-color:rgba(123,143,212,0.4) !important; box-shadow:none !important; }
.stTextInput input { background:rgba(255,255,255,0.03) !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:10px !important; color:#C8D4F0 !important; font-size:14px !important; }
.stTextInput input::placeholder { color:rgba(255,255,255,0.18) !important; }
.stFileUploader > div { background:rgba(255,255,255,0.03) !important; border:1px dashed rgba(255,255,255,0.12) !important; border-radius:10px !important; }
[data-testid="stFileUploaderDropzoneInstructions"] { color:rgba(255,255,255,0.3) !important; }
.stButton > button { background:#2A3F8F !important; color:#C8D4F8 !important; border:none !important; border-radius:10px !important; padding:10px 28px !important; font-family:'Syne',sans-serif !important; font-size:14px !important; font-weight:600 !important; width:100% !important; margin-top:10px !important; }
.stButton > button:hover { background:#3A52A8 !important; }
.stSpinner > div { border-top-color:#7B8FD4 !important; }

.fl-divider { height:1px; background:rgba(255,255,255,0.06); }
.fl-section     { padding:64px 56px; background:#0D1220; }
.fl-section-alt { padding:64px 56px; background:#0B0F1A; }
.fl-section-white { padding:64px 56px; background:#F4F6FC; }
.fl-slabel { font-size:11px; text-transform:uppercase; letter-spacing:0.14em; color:rgba(255,255,255,0.28); text-align:center; margin-bottom:8px; }
.fl-slabel-dark { color:rgba(10,14,26,0.38); }
.fl-stitle { font-family:'Syne',sans-serif; font-size:30px; font-weight:700; color:#fff; text-align:center; margin-bottom:8px; letter-spacing:-0.4px; }
.fl-stitle-dark { color:#0A0E1A; }
.fl-ssub { font-size:14px; color:rgba(255,255,255,0.32); text-align:center; margin-bottom:40px; line-height:1.7; }
.fl-ssub-dark { color:rgba(10,14,26,0.42); }

.fl-steps { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:rgba(255,255,255,0.06); border-radius:16px; overflow:hidden; max-width:900px; margin:0 auto; }
.fl-step { background:#0D1220; padding:24px 20px; }
.fl-step-icon { font-size:22px; margin-bottom:10px; }
.fl-step-n { width:30px; height:30px; border-radius:50%; background:rgba(42,63,143,0.2); border:1px solid rgba(123,143,212,0.25); color:#7B8FD4; font-size:12px; font-weight:600; display:flex; align-items:center; justify-content:center; margin-bottom:12px; }
.fl-step-t { font-size:14px; font-weight:500; color:#fff; margin-bottom:6px; }
.fl-step-d { font-size:12px; color:rgba(255,255,255,0.3); line-height:1.65; }

.fl-feat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; max-width:900px; margin:0 auto; }
.fl-fc { background:#fff; border:1px solid rgba(10,14,26,0.08); border-radius:14px; padding:22px 20px; }
.fl-fc-icon { font-size:22px; margin-bottom:12px; }
.fl-fc-t { font-size:14px; font-weight:500; color:#0A0E1A; margin-bottom:6px; }
.fl-fc-d { font-size:12px; color:rgba(10,14,26,0.45); line-height:1.65; }

.fl-sum-pills { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-bottom:28px; }
.fl-pill { display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:5px 16px; font-size:12px; color:rgba(255,255,255,0.38); }
.fl-dot { width:7px; height:7px; border-radius:50%; display:inline-block; }
.fl-results-wrap { max-width:700px; margin:0 auto; display:flex; flex-direction:column; gap:12px; }
.fl-rc { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:18px 20px; }
.fl-rc-v { border-left:3px solid #22C55E; border-radius:0 14px 14px 0; }
.fl-rc-w { border-left:3px solid #F59E0B; border-radius:0 14px 14px 0; }
.fl-rc-f { border-left:3px solid #EF4444; border-radius:0 14px 14px 0; }
.fl-rc-u { border-left:3px solid #4A5A80; border-radius:0 14px 14px 0; }
.fl-rc-top { display:flex; align-items:center; gap:8px; margin-bottom:10px; flex-wrap:wrap; }
.fl-rc-num { font-size:11px; color:rgba(255,255,255,0.28); background:rgba(255,255,255,0.06); padding:2px 10px; border-radius:100px; }
.fl-rc-cat { font-size:11px; color:rgba(255,255,255,0.28); background:rgba(255,255,255,0.06); padding:2px 10px; border-radius:100px; }
.fl-bv { font-size:11px; font-weight:500; padding:2px 12px; border-radius:100px; background:#052E16; color:#4ADE80; border:1px solid #166534; }
.fl-bw { font-size:11px; font-weight:500; padding:2px 12px; border-radius:100px; background:#451A03; color:#FBBF24; border:1px solid #92400E; }
.fl-bf { font-size:11px; font-weight:500; padding:2px 12px; border-radius:100px; background:#2D0707; color:#F87171; border:1px solid #7F1D1D; }
.fl-bu { font-size:11px; font-weight:500; padding:2px 12px; border-radius:100px; background:#111827; color:#9CA3AF; border:1px solid #374151; }
.fl-rc-claim { font-size:13px; color:rgba(255,255,255,0.6); line-height:1.65; margin-bottom:10px; font-style:italic; }
.fl-rc-sep { height:1px; background:rgba(255,255,255,0.06); margin:10px 0; }
.fl-rc-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#7B8FD4; margin-bottom:4px; }
.fl-rc-find { font-size:13px; color:rgba(255,255,255,0.42); line-height:1.6; }

.fl-stat-row { display:flex; gap:12px; margin:24px auto; max-width:700px; }
.fl-stat-card { flex:1; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px; text-align:center; }
.fl-stat-card-n { font-family:'Syne',sans-serif; font-size:28px; font-weight:700; color:#7B8FD4; }
.fl-stat-card-l { font-size:11px; color:rgba(255,255,255,0.28); text-transform:uppercase; letter-spacing:0.08em; margin-top:4px; }

.fl-about-card { max-width:540px; margin:0 auto; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:18px; padding:36px 32px; text-align:center; }
.fl-cert-badge { display:inline-flex; align-items:center; gap:12px; background:rgba(42,63,143,0.14); border:1px solid rgba(123,143,212,0.22); border-radius:12px; padding:10px 18px; margin-bottom:22px; }
.fl-cert-text { text-align:left; }
.fl-cert-text strong { display:block; font-size:13px; font-weight:500; color:#C7D2FE; margin-bottom:2px; }
.fl-cert-text span { font-size:12px; color:rgba(255,255,255,0.35); }
.fl-about-p { font-size:14px; color:rgba(255,255,255,0.36); line-height:1.75; margin-bottom:26px; }
.fl-about-btns { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }
.fl-abtn-p { background:#2A3F8F; color:#C8D4F8; font-size:13px; font-weight:500; padding:10px 26px; border-radius:10px; border:none; cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; gap:6px; }
.fl-abtn-s { background:transparent; color:rgba(255,255,255,0.38); font-size:13px; padding:10px 22px; border-radius:10px; border:1px solid rgba(255,255,255,0.1); cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; gap:6px; }

.fl-footer { background:#060810; border-top:1px solid rgba(255,255,255,0.05); padding:28px 56px; display:flex; align-items:center; justify-content:space-between; }
.fl-footer-logo { font-family:'Syne',sans-serif; font-size:16px; font-weight:700; color:rgba(255,255,255,0.28); }
.fl-footer-logo span { color:#2A3F8F; }
.fl-footer-links { display:flex; gap:20px; }
.fl-footer-links a { font-size:12px; color:rgba(255,255,255,0.16); text-decoration:none; }
.fl-footer-copy { font-size:11px; color:rgba(255,255,255,0.12); }
</style>
""", unsafe_allow_html=True)

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
    return []

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
    if any(w in cl for w in ["diagnos","detect","disease","cancer","diabetes","heart"]): return "Diagnostics"
    if any(w in cl for w in ["drug","treatment","therap","medicine","vaccine"]): return "Treatment"
    if any(w in cl for w in ["data","privacy","security","breach","hack"]): return "Data & Privacy"
    if any(w in cl for w in ["bias","ethic","fairness","disparit"]): return "Ethics & Bias"
    if any(w in cl for w in ["climate","temperature","carbon","emission","global warming"]): return "Climate"
    if any(w in cl for w in ["chatbot","ai","model","gpt","llm","neural"]): return "AI & Tech"
    if any(w in cl for w in ["fund","financ","cost","gdp","economy","market"]): return "Economics"
    if any(w in cl for w in ["legal","law","court","regulat","ban","policy"]): return "Policy & Law"
    if any(w in cl for w in ["election","vote","president","government","parliament"]): return "Politics"
    return "General"

def verdict_html(verdict):
    mapping = {
        "Verified":     ("fl-rc-v", "fl-bv", "✓ Verified"),
        "Inaccurate":   ("fl-rc-w", "fl-bw", "⚠ Inaccurate"),
        "False":        ("fl-rc-f", "fl-bf", "✕ False"),
        "Unverifiable": ("fl-rc-u", "fl-bu", "— Unverifiable"),
    }
    return mapping.get(verdict, ("fl-rc-u", "fl-bu", "— Unverifiable"))

st.markdown("""
<div class="fl-nav">
  <div class="fl-logo">Fact<span>Lens</span></div>
  <div class="fl-nav-links">
    <a href="#how-it-works">How it works</a>
    <a href="#features">Features</a>
    <a href="#about">About</a>
  </div>
  <a class="fl-nav-btn" href="#verify">Try it free</a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fl-hero" id="verify">
  <div class="fl-hero-glow"></div>
  <div class="fl-badge"><span class="fl-badge-dot"></span>AI-powered fact verification</div>
  <h1>Paste any text.<br>Know what's <em>actually</em> true.</h1>
  <p class="fl-hero-sub">No account. No API keys. Drop any paragraph, news snippet, or WhatsApp
  forward — FactLens checks it against live web sources in seconds.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="background:#0B0F1A; padding: 24px 0 0 0;">', unsafe_allow_html=True)

_, mid, _ = st.columns([1, 2, 1])

with mid:
    st.markdown('<div class="fl-input-card">', unsafe_allow_html=True)

    mode = st.selectbox(
        "mode",
        ["📝  Paste text", "🔗  Paste URL", "📄  Upload PDF"],
        label_visibility="collapsed",
    )

    verify     = False
    input_text = ""

    if mode == "📝  Paste text":
        input_text = st.text_area(
            "text",
            placeholder="Paste any text here — a news article, WhatsApp forward, or any claim you want verified...",
            height=130,
            label_visibility="collapsed",
        )

    elif mode == "🔗  Paste URL":
        url_val = st.text_input("url", placeholder="https://example.com/article", label_visibility="collapsed")
        if url_val:
            try:
                import urllib.request
                from html.parser import HTMLParser
                class _TX(HTMLParser):
                    def __init__(self):
                        super().__init__(); self.bits=[]; self.skip=False
                    def handle_starttag(self,t,a):
                        if t in('script','style','nav','footer'): self.skip=True
                    def handle_endtag(self,t):
                        if t in('script','style','nav','footer'): self.skip=False
                    def handle_data(self,d):
                        if not self.skip and d.strip(): self.bits.append(d.strip())
                req=urllib.request.Request(url_val,headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req,timeout=10) as r:
                    html=r.read().decode("utf-8",errors="ignore")
                p=_TX(); p.feed(html)
                input_text=" ".join(p.bits)[:5000]
                st.success(f"✅ Fetched {len(input_text):,} characters")
            except Exception as e:
                st.error(f"Could not fetch URL: {e}")

    else:
        uploaded = st.file_uploader("pdf", type="pdf", label_visibility="collapsed")
        if uploaded:
            with pdfplumber.open(uploaded) as pdf:
                input_text = "".join(p.extract_text() or "" for p in pdf.pages)
            st.success(f"✅ {uploaded.name} — {len(input_text):,} characters extracted")

    st.markdown('<p class="fl-input-hint">🔒 Groq LLM + Tavily live web search &nbsp;·&nbsp; Your text is never stored</p>', unsafe_allow_html=True)
    verify = st.button("🔬  Verify claims", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="fl-stats-zone">
  <div class="fl-stats-row">
    <div class="fl-stat"><div class="fl-stat-n">3–8</div><div class="fl-stat-l">Claims found</div></div>
    <div class="fl-stat"><div class="fl-stat-n">&lt;15s</div><div class="fl-stat-l">Avg check time</div></div>
    <div class="fl-stat"><div class="fl-stat-n">Live</div><div class="fl-stat-l">Web sources</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

if verify:
    if not input_text.strip():
        st.warning("Please provide some text, a URL, or upload a PDF first.")
    elif not GROQ_API_KEY or not TAVILY_API_KEY:
        st.error("API keys not configured — add GROQ_API_KEY and TAVILY_API_KEY in Render → Environment.")
    else:
        client = Groq(api_key=GROQ_API_KEY)
        tavily = TavilyClient(api_key=TAVILY_API_KEY)

        with st.spinner("🤖 Extracting claims from your text..."):
            prompt = f"""
You are an expert fact-checking assistant. From the text below, extract between 3 and 8 specific, verifiable claims.

For each claim also write:
- "purpose": one sentence explaining WHY this claim matters (for a non-expert reader)
- "category": one of [Diagnostics, Treatment, Climate, AI & Tech, Economics, Policy & Law, Politics, Data & Privacy, Ethics & Bias, General]

Return ONLY a valid JSON array. No markdown, no commentary.

Format:
[
  {{
    "claim": "The full factual claim as stated or implied in the text.",
    "purpose": "This claim establishes that...",
    "category": "Climate"
  }}
]

Text:
{input_text[:4500]}
"""
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":prompt}],
                temperature=0
            )
            raw = resp.choices[0].message.content.strip()
            claims_data = extract_json_array(raw)

        claims = []
        for item in claims_data:
            if isinstance(item, dict):
                claims.append({
                    "claim":    item.get("claim", str(item)),
                    "purpose":  item.get("purpose", ""),
                    "category": item.get("category", get_category(item.get("claim","")))
                })
            else:
                claims.append({"claim":str(item),"purpose":"","category":get_category(str(item))})

        if not claims:
            st.error("Could not extract claims — try pasting more specific or factual text.")
            st.stop()

        st.markdown(f"""
<div class="fl-section-alt" style="padding:40px 56px 16px">
  <div style="text-align:center;margin-bottom:6px">
    <div class="fl-slabel">Analysis complete</div>
    <div class="fl-stitle">{len(claims)} claims found</div>
    <div class="fl-ssub">Verifying each one against live web sources now...</div>
  </div>
  <div class="fl-stat-row">
    <div class="fl-stat-card"><div class="fl-stat-card-n">{len(claims)}</div><div class="fl-stat-card-l">Claims extracted</div></div>
    <div class="fl-stat-card"><div class="fl-stat-card-n">{len(set(c['category'] for c in claims))}</div><div class="fl-stat-card-l">Topics covered</div></div>
    <div class="fl-stat-card"><div class="fl-stat-card-n">{len(input_text):,}</div><div class="fl-stat-card-l">Characters scanned</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

        counts = {"Verified":0,"Inaccurate":0,"False":0,"Unverifiable":0}
        cards  = []

        for i, item in enumerate(claims):
            claim    = item["claim"]
            purpose  = item["purpose"]
            category = item["category"]

            with st.spinner(f"Verifying claim {i+1} of {len(claims)}..."):
                try:
                    try:
                        sr = tavily.search(query=claim, search_depth="basic", max_results=3)
                        snippets = " ".join([r.get("content","") for r in sr.get("results",[])])
                    except Exception:
                        snippets = ""

                    if not snippets.strip():
                        try:
                            short_q = " ".join(claim.split()[:8])
                            sr = tavily.search(query=short_q, search_depth="basic", max_results=3)
                            snippets = " ".join([r.get("content","") for r in sr.get("results",[])])
                        except Exception:
                            snippets = ""

                    if not snippets.strip():
                        verdict, explanation = "Unverifiable", "No web sources found to verify or contradict this claim."
                    else:
                        vp = f"""
You are a fact-checker. Based ONLY on the web results below, verify the claim.

Claim: "{claim}"

Web Results:
{snippets[:2000]}

Return ONLY a valid JSON object, no markdown:
{{"verdict": "Verified", "explanation": "one clear sentence"}}

verdict must be exactly one of: "Verified", "Inaccurate", "False", "Unverifiable"
"""
                        vr = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role":"user","content":vp}],
                            temperature=0
                        )
                        vd = extract_json_object(vr.choices[0].message.content.strip())
                        verdict     = vd.get("verdict","Unverifiable") if vd else "Unverifiable"
                        explanation = vd.get("explanation","No explanation.") if vd else "Could not parse response."

                    counts[verdict] = counts.get(verdict,0) + 1
                    card_class, badge_class, badge_label = verdict_html(verdict)

                    purpose_block = f"""
<div class="fl-rc-label">Why this matters</div>
<div class="fl-rc-find" style="margin-bottom:8px">{purpose}</div>
<div class="fl-rc-sep"></div>
""" if purpose else ""

                    cards.append(f"""
<div class="fl-rc {card_class}">
  <div class="fl-rc-top">
    <span class="fl-rc-num">Claim {i+1}</span>
    <span class="fl-rc-cat">{category}</span>
    <span class="{badge_class}">{badge_label}</span>
  </div>
  <div class="fl-rc-claim">"{claim}"</div>
  <div class="fl-rc-sep"></div>
  {purpose_block}
  <div class="fl-rc-label">Verification finding</div>
  <div class="fl-rc-find">{explanation}</div>
</div>
""")
                except Exception as e:
                    cards.append(f"""
<div class="fl-rc fl-rc-u">
  <div class="fl-rc-top"><span class="fl-rc-num">Claim {i+1}</span><span class="fl-bu">Error</span></div>
  <div class="fl-rc-claim">"{claim}"</div>
  <div class="fl-rc-find">Could not verify: {str(e)}</div>
</div>
""")

        dot_map = {"Verified":"#22C55E","Inaccurate":"#F59E0B","False":"#EF4444","Unverifiable":"#4A5A80"}
        pills = "".join([
            f'<div class="fl-pill"><span class="fl-dot" style="background:{dot_map[k]}"></span>{counts[k]} {k}</div>'
            for k in ["Verified","Inaccurate","False","Unverifiable"] if counts[k]>0
        ])

        st.markdown(f"""
<div class="fl-section-alt" style="padding-top:20px" id="results">
  <div class="fl-slabel">Results</div>
  <div class="fl-stitle">Verification complete</div>
  <div class="fl-sum-pills">{pills}</div>
  <div class="fl-results-wrap">{"".join(cards)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fl-divider"></div>
<div class="fl-section" id="how-it-works">
  <div class="fl-slabel">The process</div>
  <div class="fl-stitle">How FactLens works</div>
  <div class="fl-ssub">Four steps from raw text to verified truth</div>
  <div class="fl-steps">
    <div class="fl-step"><div class="fl-step-icon">📋</div><div class="fl-step-n">1</div><div class="fl-step-t">You paste</div><div class="fl-step-d">Drop any text, paste a URL, or upload a PDF. No login ever required.</div></div>
    <div class="fl-step"><div class="fl-step-icon">🧠</div><div class="fl-step-n">2</div><div class="fl-step-t">AI extracts</div><div class="fl-step-d">Groq's LLM reads the text and pulls out every verifiable claim it finds.</div></div>
    <div class="fl-step"><div class="fl-step-icon">🌐</div><div class="fl-step-n">3</div><div class="fl-step-t">Web searches</div><div class="fl-step-d">Each claim is cross-checked against live web sources in real time.</div></div>
    <div class="fl-step"><div class="fl-step-icon">📊</div><div class="fl-step-n">4</div><div class="fl-step-t">You get results</div><div class="fl-step-d">A clear verdict — Verified, Inaccurate, False, or Unverifiable — for every claim.</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fl-divider"></div>
<div class="fl-section-white" id="features">
  <div class="fl-slabel fl-slabel-dark">Why FactLens</div>
  <div class="fl-stitle fl-stitle-dark">Built different</div>
  <div class="fl-ssub fl-ssub-dark">Not just search — a full AI verification pipeline</div>
  <div class="fl-feat-grid">
    <div class="fl-fc"><div class="fl-fc-icon">⚡</div><div class="fl-fc-t">Zero friction</div><div class="fl-fc-d">No login, no API keys, no setup. Open the app and start verifying in one click.</div></div>
    <div class="fl-fc"><div class="fl-fc-icon">🌐</div><div class="fl-fc-t">Live web sources</div><div class="fl-fc-d">Claims are verified against real-time results, not a static knowledge base.</div></div>
    <div class="fl-fc"><div class="fl-fc-icon">🏷️</div><div class="fl-fc-t">Auto-categorized</div><div class="fl-fc-d">Each claim gets a topic tag — Climate, Health, Politics, AI & Tech and more.</div></div>
    <div class="fl-fc"><div class="fl-fc-icon">📄</div><div class="fl-fc-t">Three input modes</div><div class="fl-fc-d">Paste text, drop a URL, or upload a full PDF — all handled in one place.</div></div>
    <div class="fl-fc"><div class="fl-fc-icon">💬</div><div class="fl-fc-t">Explained verdicts</div><div class="fl-fc-d">Every result includes a clear explanation — not just a label, but the reasoning behind it.</div></div>
    <div class="fl-fc"><div class="fl-fc-icon">🔒</div><div class="fl-fc-t">Privacy first</div><div class="fl-fc-d">Your text is never stored or logged. Each session is completely independent.</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fl-divider"></div>
<div class="fl-section-alt" id="about">
  <div class="fl-slabel">The story</div>
  <div class="fl-stitle">About this project</div>
  <div class="fl-ssub">Built by a student, for everyone</div>
  <div class="fl-about-card">
    <div class="fl-cert-badge">
      <span style="font-size:22px">🎓</span>
      <div class="fl-cert-text">
        <strong>Anthropic AI Fluency Certificate</strong>
        <span>Built as part of Anthropic's AI Fluency program</span>
      </div>
    </div>
    <p class="fl-about-p">FactLens started as a college project exploring how large language models can make information
    more trustworthy. It grew into a real tool for anyone who wants to know if what they're reading is actually true —
    powered by Groq LLM and Tavily live search.</p>
    <div class="fl-about-btns">
      <a class="fl-abtn-p" href="#verify">▲ Verify something now</a>
      <a class="fl-abtn-s" href="https://github.com/vedikakashyap/Fact_Lence" target="_blank">⌥ View on GitHub</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fl-divider"></div>
<div class="fl-footer">
  <div class="fl-footer-logo">Fact<span>Lens</span></div>
  <div class="fl-footer-links">
    <a href="#how-it-works">How it works</a>
    <a href="#features">Features</a>
    <a href="https://github.com/vedikakashyap/Fact_Lence">GitHub</a>
  </div>
  <div class="fl-footer-copy">Python · Streamlit · Groq · Tavily</div>
</div>
""", unsafe_allow_html=True)
