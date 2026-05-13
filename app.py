import streamlit as st
import pdfplumber
import json
import re
from groq import Groq
from tavily import TavilyClient
import os

st.set_page_config(page_title="FactLens AI", page_icon="🔬", layout="wide")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Custom CSS with fixed alignment
st.markdown("""
<style>
/* Global resets */
.main > div {padding-left: 5rem; padding-right: 5rem;}

/* Hero section alignment */
.fl-hero {text-align: center; padding: 2rem 0 3rem 0;}
.fl-badge {
    display: inline-block;
    background: rgba(102, 126, 234, 0.15);
    border: 1px solid rgba(102, 126, 234, 0.3);
    padding: 0.5rem 1.2rem;
    border-radius: 20px;
    font-size: 0.85rem;
    color: #818CF8;
    margin-bottom: 2rem;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.fl-title {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    color: white;
}
.fl-title strong {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-style: italic;
}
.fl-subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.7;
    padding: 0 1rem;
}

/* Header */
.fl-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 0;
    margin-bottom: 2rem;
}
.fl-logo {
    font-size: 1.8rem;
    font-weight: 700;
    color: white;
    text-decoration: none;
}
.fl-nav {
    display: flex;
    gap: 2.5rem;
    align-items: center;
}
.fl-nav a {
    color: #94A3B8;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
}
.fl-nav a:hover {color: #818CF8;}
.fl-cta {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    color: white !important;
    padding: 0.6rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: transform 0.2s;
}
.fl-cta:hover {transform: translateY(-2px);}

/* Input container */
.fl-input-wrap {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 900px;
}
.fl-privacy {
    text-align: center;
    color: #64748B;
    font-size: 0.85rem;
    margin: 1.5rem 0;
    padding: 1rem 0;
}

/* Stats */
.fl-stats {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 3rem 0;
    flex-wrap: wrap;
}
.fl-stat {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem 2.5rem;
    text-align: center;
    min-width: 160px;
}
.fl-stat-v {
    font-size: 1.8rem;
    font-weight: 700;
    color: #818CF8;
    margin-bottom: 0.3rem;
}
.fl-stat-l {
    font-size: 0.8rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Sections */
.fl-section {
    margin: 5rem 0;
    padding: 3rem 0;
}
.fl-sec-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.5rem;
    color: white;
}
.fl-sec-sub {
    text-align: center;
    color: #94A3B8;
    margin-bottom: 3rem;
    font-size: 1.1rem;
}

/* Feature grid */
.fl-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
.fl-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 2rem;
    transition: transform 0.2s, border-color 0.2s;
}
.fl-card:hover {
    transform: translateY(-3px);
    border-color: rgba(102, 126, 234, 0.3);
}
.fl-icon {font-size: 2.5rem; margin-bottom: 1rem;}
.fl-card h3 {
    color: white;
    margin-bottom: 0.75rem;
    font-size: 1.2rem;
}
.fl-card p {
    color: #94A3B8;
    line-height: 1.6;
    margin: 0;
}

/* About card */
.fl-about {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}
.fl-about-icon {font-size: 3.5rem; margin-bottom: 1.5rem;}
.fl-about h3 {
    color: white;
    margin-bottom: 1.25rem;
    font-size: 1.5rem;
}
.fl-about p {
    color: #94A3B8;
    line-height: 1.8;
    margin-bottom: 2rem;
}
.fl-btns {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}
.fl-btn {
    display: inline-block;
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
    color: white !important;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s;
}
.fl-btn:hover {transform: translateY(-2px);}
.fl-btn-sec {
    background: rgba(255, 255, 255, 0.08);
}

/* Results */
.fl-results {margin: 3rem 0;}
.fl-res-title {
    font-size: 2rem;
    color: white;
    text-align: center;
    margin-bottom: 1.5rem;
}
.fl-pills {
    text-align: center;
    margin-bottom: 2rem;
}
.fl-pill {
    display: inline-block;
    padding: 0.5rem 1.2rem;
    border-radius: 8px;
    margin: 0.3rem;
    font-weight: 600;
    font-size: 0.95rem;
}
.fl-card-res {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 2rem;
    margin: 1.5rem 0;
}
.fl-card-res.fl-rc-v {border-left: 4px solid #22C55E;}
.fl-card-res.fl-rc-w {border-left: 4px solid #F59E0B;}
.fl-card-res.fl-rc-f {border-left: 4px solid #EF4444;}
.fl-card-res.fl-rc-u {border-left: 4px solid #4A5A80;}
.fl-res-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
    gap: 1rem;
}
.fl-claim-n {
    color: #94A3B8;
    font-weight: 600;
    font-size: 0.9rem;
}
.fl-cat {
    background: rgba(102, 126, 234, 0.2);
    color: #818CF8;
    padding: 0.3rem 0.9rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
}
.fl-bv {background: rgba(34, 197, 94, 0.2); color: #22C55E;}
.fl-bw {background: rgba(245, 158, 11, 0.2); color: #F59E0B;}
.fl-bf {background: rgba(239, 68, 68, 0.2); color: #EF4444;}
.fl-bu {background: rgba(74, 90, 128, 0.3); color: #94A3B8;}
.fl-claim-text {
    color: white;
    font-size: 1.15rem;
    margin: 1.25rem 0;
    font-style: italic;
    line-height: 1.6;
}
.fl-purpose {
    background: rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667EEA;
    padding: 1rem 1.25rem;
    margin: 1.25rem 0;
    border-radius: 0 8px 8px 0;
}
.fl-purpose strong {
    color: #818CF8;
    font-size: 0.85rem;
    display: block;
    margin-bottom: 0.5rem;
}
.fl-purpose p {
    color: #94A3B8;
    margin: 0;
    line-height: 1.6;
}
.fl-verdict {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.fl-verdict strong {
    color: #94A3B8;
    font-size: 0.9rem;
    display: block;
    margin-bottom: 0.5rem;
}
.fl-verdict p {
    color: #E2E8F0;
    margin: 0;
    line-height: 1.6;
}

/* Footer */
.fl-footer {
    text-align: center;
    padding: 3rem 0;
    margin-top: 5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: #64748B;
}
.fl-footer-logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 1rem;
}
.fl-footer a {
    color: #94A3B8;
    text-decoration: none;
    margin: 0 1rem;
    transition: color 0.2s;
}
.fl-footer a:hover {color: #818CF8;}

/* Streamlit overrides */
.stTextArea textarea, .stTextInput input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}
.stButton button {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
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
    match = re.search(r'{.*?}', text, re.DOTALL)
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
        "Verified": ("fl-rc-v", "fl-bv", "✓ Verified"),
        "Inaccurate": ("fl-rc-w", "fl-bw", "⚠ Inaccurate"),
        "False": ("fl-rc-f", "fl-bf", "✕ False"),
        "Unverifiable": ("fl-rc-u", "fl-bu", "— Unverifiable"),
    }
    return mapping.get(verdict, ("fl-rc-u", "fl-bu", "— Unverifiable"))

# Header
st.markdown("""
<div class="fl-header">
    <a href="#" class="fl-logo">FactLens</a>
    <nav class="fl-nav">
        <a href="#how-it-works">How it works</a>
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="#" class="fl-cta">Try it free</a>
    </nav>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="fl-hero">
    <div class="fl-badge">🔬 AI-POWERED FACT VERIFICATION</div>
    <h1 class="fl-title">Paste any text.<br>Know what's <strong>actually</strong> true.</h1>
    <p class="fl-subtitle">No account. No API keys. Drop any paragraph, news snippet, or WhatsApp forward — FactLens checks it against live web sources in seconds.</p>
</div>
""", unsafe_allow_html=True)

# Input Section
st.markdown('<div class="fl-input-wrap">', unsafe_allow_html=True)

mode = st.selectbox(
    "mode",
    ["📝 Paste text", "🔗 Paste URL", "📄 Upload PDF"],
    label_visibility="collapsed",
)

verify = False
input_text = ""

if mode == "📝 Paste text":
    input_text = st.text_area(
        "text",
        placeholder="Paste any text here — a news article, WhatsApp forward, or any claim you want verified...",
        height=130,
        label_visibility="collapsed",
    )

elif mode == "🔗 Paste URL":
    url_val = st.text_input("url", placeholder="https://example.com/article", label_visibility="collapsed")
    if url_val:
        try:
            import urllib.request
            from html.parser import HTMLParser
            class _TX(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.bits=[]
                    self.skip=False
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

st.markdown('<div class="fl-privacy">🔒 Groq LLM + Tavily live web search · Your text is never stored</div>', unsafe_allow_html=True)
verify = st.button("🔬 Verify claims", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Stats
st.markdown("""
<div class="fl-stats">
    <div class="fl-stat">
        <div class="fl-stat-v">3–8</div>
        <div class="fl-stat-l">Claims found</div>
    </div>
    <div class="fl-stat">
        <div class="fl-stat-v">&lt;15s</div>
        <div class="fl-stat-l">Avg check time</div>
    </div>
    <div class="fl-stat">
        <div class="fl-stat-v">Live</div>
        <div class="fl-stat-l">Web sources</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Verification Logic
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
                        "claim": item.get("claim", str(item)),
                        "purpose": item.get("purpose", ""),
                        "category": item.get("category", get_category(item.get("claim","")))
                    })
                else:
                    claims.append({"claim":str(item),"purpose":"","category":get_category(str(item))})

            if not claims:
                st.error("Could not extract claims — try pasting more specific or factual text.")
                st.stop()

            st.markdown(f"""
<div style="text-align: center; margin: 2rem 0; padding: 2.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.2);">
    <h3 style="color: white; margin-bottom: 1rem; font-size: 1.5rem;">✅ Analysis complete</h3>
    <div style="display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap;">
        <div>
            <div style="font-size: 2rem; font-weight: 700; color: #818CF8;">{len(claims)}</div>
            <div style="color: #94A3B8; font-size: 0.9rem;">Claims extracted</div>
        </div>
        <div>
            <div style="font-size: 2rem; font-weight: 700; color: #818CF8;">{len(set(c['category'] for c in claims))}</div>
            <div style="color: #94A3B8; font-size: 0.9rem;">Topics covered</div>
        </div>
        <div>
            <div style="font-size: 2rem; font-weight: 700; color: #818CF8;">{len(input_text):,}</div>
            <div style="color: #94A3B8; font-size: 0.9rem;">Characters scanned</div>
        </div>
    </div>
    <p style="color: #94A3B8; margin-top: 1.5rem; font-size: 1rem;">Verifying each one against live web sources now...</p>
</div>
""", unsafe_allow_html=True)

            counts = {"Verified":0,"Inaccurate":0,"False":0,"Unverifiable":0}
            cards = []

            for i, item in enumerate(claims):
                claim = item["claim"]
                purpose = item["purpose"]
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
                            verdict = vd.get("verdict","Unverifiable") if vd else "Unverifiable"
                            explanation = vd.get("explanation","No explanation.") if vd else "Could not parse response."

                        counts[verdict] = counts.get(verdict,0) + 1
                        card_class, badge_class, badge_label = verdict_html(verdict)

                        purpose_block = f"""
<div class="fl-purpose">
    <strong>Why this matters</strong>
    <p>{purpose}</p>
</div>
""" if purpose else ""

                        cards.append(f"""
<div class="fl-card-res {card_class}">
    <div class="fl-res-head">
        <span class="fl-claim-n">Claim {i+1}</span>
        <span class="fl-cat">{category}</span>
        <span class="{badge_class}">{badge_label}</span>
    </div>
    <p class="fl-claim-text">"{claim}"</p>
    {purpose_block}
    <div class="fl-verdict">
        <strong>Verification finding</strong>
        <p>{explanation}</p>
    </div>
</div>
""")
                    except Exception as e:
                        cards.append(f"""
<div class="fl-card-res fl-rc-u">
    <div class="fl-res-head">
        <span class="fl-claim-n">Claim {i+1}</span>
        <span class="fl-bu">Error</span>
    </div>
    <p class="fl-claim-text">"{claim}"</p>
    <p style="color: #EF4444; margin-top: 0.5rem;">Could not verify: {str(e)}</p>
</div>
""")

            dot_map = {"Verified":"#22C55E","Inaccurate":"#F59E0B","False":"#EF4444","Unverifiable":"#4A5A80"}
            pills = "".join([
                f'<span class="fl-pill" style="background: {dot_map[k]}; color: white;">{counts[k]} {k}</span>'
                for k in ["Verified","Inaccurate","False","Unverifiable"] if counts[k]>0
            ])

            st.markdown(f"""
<div class="fl-results">
    <h2 class="fl-res-title">📊 Results</h2>
    <div class="fl-pills">
        <span style="color: #94A3B8; margin-right: 1rem; font-size: 1.1rem;">Verification complete</span>
        {pills}
    </div>
    {''.join(cards)}
</div>
""", unsafe_allow_html=True)

# How it Works Section
st.markdown("""
<div id="how-it-works" class="fl-section">
    <h2 class="fl-sec-title">The process</h2>
    <p class="fl-sec-sub">How FactLens works — Four steps from raw text to verified truth</p>
    
    <div class="fl-grid">
        <div class="fl-card">
            <div class="fl-icon">📋</div>
            <h3>1. You paste</h3>
            <p>Drop any text, paste a URL, or upload a PDF. No login ever required.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">🧠</div>
            <h3>2. AI extracts</h3>
            <p>Groq's LLM reads the text and pulls out every verifiable claim it finds.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">🌐</div>
            <h3>3. Web searches</h3>
            <p>Each claim is cross-checked against live web sources in real time.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">📊</div>
            <h3>4. You get results</h3>
            <p>A clear verdict — Verified, Inaccurate, False, or Unverifiable — for every claim.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features Section
st.markdown("""
<div id="features" class="fl-section">
    <h2 class="fl-sec-title">Why FactLens</h2>
    <p class="fl-sec-sub">Built different — Not just search, a full AI verification pipeline</p>
    
    <div class="fl-grid">
        <div class="fl-card">
            <div class="fl-icon">⚡</div>
            <h3>Zero friction</h3>
            <p>No login, no API keys, no setup. Open the app and start verifying in one click.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">🌐</div>
            <h3>Live web sources</h3>
            <p>Claims are verified against real-time results, not a static knowledge base.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">🏷️</div>
            <h3>Auto-categorized</h3>
            <p>Each claim gets a topic tag — Climate, Health, Politics, AI & Tech and more.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">📄</div>
            <h3>Three input modes</h3>
            <p>Paste text, drop a URL, or upload a full PDF — all handled in one place.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">💬</div>
            <h3>Explained verdicts</h3>
            <p>Every result includes a clear explanation — not just a label, but the reasoning behind it.</p>
        </div>
        <div class="fl-card">
            <div class="fl-icon">🔒</div>
            <h3>Privacy first</h3>
            <p>Your text is never stored or logged. Each session is completely independent.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# About Section with Anthropic Badge
st.markdown("""
<div id="about" class="fl-section">
    <h2 class="fl-sec-title">The story</h2>
    <p class="fl-sec-sub">About this project — Built by a student, for everyone</p>
    
    <div class="fl-about">
        <div class="fl-about-icon">🎓</div>
        <h3>Anthropic AI Fluency Certificate</h3>
        <p>Built as part of Anthropic's AI Fluency program. FactLens started as a college project exploring how large language models can make information more trustworthy. It grew into a real tool for anyone who wants to know if what they're reading is actually true — powered by Groq LLM and Tavily live search.</p>
        <div class="fl-btns">
            <a href="#" class="fl-btn">▲ Verify something now</a>
            <a href="https://github.com/vedikakashyap/Fact_Lence" class="fl-btn fl-btn-sec">⌥ View on GitHub</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="fl-footer">
    <div class="fl-footer-logo">FactLens</div>
    <div style="margin-bottom: 1rem;">
        <a href="#how-it-works">How it works</a>
        <a href="#features">Features</a>
        <a href="https://github.com/vedikakashyap/Fact_Lence">GitHub</a>
    </div>
    <p>Python · Streamlit · Groq · Tavily</p>
</div>
""", unsafe_allow_html=True)
