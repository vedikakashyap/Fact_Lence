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

# Custom CSS for better alignment and styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        padding: 0rem 5rem;
    }
    
    /* Header Styles */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 3rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-links a {
        color: #94A3B8;
        text-decoration: none;
        font-size: 0.95rem;
        transition: color 0.3s;
    }
    
    .nav-links a:hover {
        color: #667EEA;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 0;
    }
    
    .badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #667EEA;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .hero-title span {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        max-width: 600px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
    }
    
    /* Input Section */
    .input-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 900px;
    }
    
    .privacy-note {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Stats Section */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 3rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem 2.5rem;
        text-align: center;
        min-width: 150px;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667EEA;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Result Cards */
    .result-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .claim-number {
        font-weight: 600;
        color: #94A3B8;
    }
    
    .category-tag {
        background: rgba(102, 126, 234, 0.2);
        color: #667EEA;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    
    /* Verdict Badges */
    .badge-verified {
        background: rgba(34, 197, 94, 0.2);
        color: #22C55E;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .badge-inaccurate {
        background: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .badge-false {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .badge-unverifiable {
        background: rgba(74, 90, 128, 0.3);
        color: #94A3B8;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* Section Styles */
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 4rem 0 2rem 0;
        color: white;
    }
    
    .section-subtitle {
        text-align: center;
        color: #94A3B8;
        margin-bottom: 3rem;
        font-size: 1.1rem;
    }
    
    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Streamlit component overrides */
    .stTextArea textarea, .stTextInput input, .stSelectbox {
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
        "Verified": ("badge-verified", "✓ Verified"),
        "Inaccurate": ("badge-inaccurate", "⚠ Inaccurate"),
        "False": ("badge-false", "✕ False"),
        "Unverifiable": ("badge-unverifiable", "— Unverifiable"),
    }
    return mapping.get(verdict, ("badge-unverifiable", "— Unverifiable"))

# Header
st.markdown("""
<div class="header-container">
    <div class="logo">FactLens</div>
    <div class="nav-links">
        <a href="#how-it-works">How it works</a>
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="#" class="cta-button">Try it free</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="badge">🔬 AI-POWERED FACT VERIFICATION</div>
    <h1 class="hero-title">Paste any text.<br>Know what's <span>actually</span> true.</h1>
    <p class="hero-subtitle">No account. No API keys. Drop any paragraph, news snippet, or WhatsApp forward — FactLens checks it against live web sources in seconds.</p>
</div>
""", unsafe_allow_html=True)

# Input Section
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    mode = st.selectbox(
        "Select Input Mode",
        ["📝 Paste text", "🔗 Paste URL", "📄 Upload PDF"],
        label_visibility="collapsed",
    )
    
    verify = False
    input_text = ""
    
    if mode == "📝 Paste text":
        input_text = st.text_area(
            "Enter text to verify",
            placeholder="Paste any text here — a news article, WhatsApp forward, or any claim you want verified...",
            height=150,
            label_visibility="collapsed",
        )
    
    elif mode == "🔗 Paste URL":
        url_val = st.text_input("Enter URL", placeholder="https://example.com/article", label_visibility="collapsed")
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
        uploaded = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
        if uploaded:
            with pdfplumber.open(uploaded) as pdf:
                input_text = "".join(p.extract_text() or "" for p in pdf.pages)
                st.success(f"✅ {uploaded.name} — {len(input_text):,} characters extracted")
    
    st.markdown('<div class="privacy-note">🔒 Groq LLM + Tavily live web search · Your text is never stored</div>', unsafe_allow_html=True)
    
    verify = st.button("🔬 Verify claims", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Stats Section
st.markdown("""
<div class="stats-container">
    <div class="stat-card">
        <div class="stat-value">3–8</div>
        <div class="stat-label">Claims found</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">&lt;15s</div>
        <div class="stat-label">Avg check time</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">Live</div>
        <div class="stat-label">Web sources</div>
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
            <div style="text-align: center; margin: 2rem 0; padding: 2rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px;">
                <h3 style="color: white; margin-bottom: 1rem;">✅ Analysis complete</h3>
                <p style="color: #94A3B8; font-size: 1.1rem;">{len(claims)} claims found</p>
                <p style="color: #64748B; margin-top: 0.5rem;">Verifying each one against live web sources now...</p>
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
                        badge_class, badge_label = verdict_html(verdict)
                        
                        purpose_block = f"""
                        <div style="margin: 1rem 0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <strong style="color: #667EEA; font-size: 0.9rem;">Why this matters</strong>
                            <p style="color: #94A3B8; margin: 0.5rem 0 0 0; font-size: 0.95rem;">{purpose}</p>
                        </div>
                        """ if purpose else ""
                        
                        cards.append(f"""
                        <div class="result-card">
                            <div class="result-header">
                                <span class="claim-number">Claim {i+1}</span>
                                <span class="category-tag">{category}</span>
                                <span class="{badge_class}">{badge_label}</span>
                            </div>
                            <p style="color: white; font-size: 1.1rem; margin: 1rem 0; font-style: italic;">"{claim}"</p>
                            {purpose_block}
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                                <strong style="color: #94A3B8; font-size: 0.9rem;">Verification finding</strong>
                                <p style="color: #E2E8F0; margin: 0.5rem 0 0 0;">{explanation}</p>
                            </div>
                        </div>
                        """)
                    except Exception as e:
                        cards.append(f"""
                        <div class="result-card">
                            <div class="result-header">
                                <span class="claim-number">Claim {i+1}</span>
                                <span class="badge-false">Error</span>
                            </div>
                            <p style="color: white;">"{claim}"</p>
                            <p style="color: #EF4444; margin-top: 0.5rem;">Could not verify: {str(e)}</p>
                        </div>
                        """)
            
            dot_map = {"Verified":"#22C55E","Inaccurate":"#F59E0B","False":"#EF4444","Unverifiable":"#4A5A80"}
            pills = "".join([
                f'<span style="display: inline-block; background: {dot_map[k]}; color: white; padding: 0.4rem 1rem; border-radius: 6px; margin: 0.25rem; font-weight: 600;">{counts[k]} {k}</span>'
                for k in ["Verified","Inaccurate","False","Unverifiable"] if counts[k]>0
            ])
            
            st.markdown(f"""
            <div style="margin: 3rem 0;">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem;">📊 Results</h2>
                <div style="text-align: center; margin-bottom: 2rem;">
                    {pills}
                </div>
                {''.join(cards)}
            </div>
            """, unsafe_allow_html=True)

# How it Works Section
st.markdown("""
<div id="how-it-works" style="margin-top: 5rem;">
    <h2 class="section-title">The process</h2>
    <p class="section-subtitle">How FactLens works — Four steps from raw text to verified truth</p>
    
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">1. You paste</h3>
            <p style="color: #94A3B8;">Drop any text, paste a URL, or upload a PDF. No login ever required.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">2. AI extracts</h3>
            <p style="color: #94A3B8;">Groq's LLM reads the text and pulls out every verifiable claim it finds.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">3. Web searches</h3>
            <p style="color: #94A3B8;">Each claim is cross-checked against live web sources in real time.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">4. You get results</h3>
            <p style="color: #94A3B8;">A clear verdict — Verified, Inaccurate, False, or Unverifiable — for every claim.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features Section
st.markdown("""
<div id="features" style="margin-top: 5rem;">
    <h2 class="section-title">Why FactLens</h2>
    <p class="section-subtitle">Built different — Not just search, a full AI verification pipeline</p>
    
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Zero friction</h3>
            <p style="color: #94A3B8;">No login, no API keys, no setup. Open the app and start verifying in one click.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Live web sources</h3>
            <p style="color: #94A3B8;">Claims are verified against real-time results, not a static knowledge base.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🏷️</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Auto-categorized</h3>
            <p style="color: #94A3B8;">Each claim gets a topic tag — Climate, Health, Politics, AI & Tech and more.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Three input modes</h3>
            <p style="color: #94A3B8;">Paste text, drop a URL, or upload a full PDF — all handled in one place.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Explained verdicts</h3>
            <p style="color: #94A3B8;">Every result includes a clear explanation — not just a label, but the reasoning behind it.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Privacy first</h3>
            <p style="color: #94A3B8;">Your text is never stored or logged. Each session is completely independent.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# About Section
st.markdown("""
<div id="about" style="margin-top: 5rem; margin-bottom: 3rem;">
    <h2 class="section-title">The story</h2>
    <p class="section-subtitle">About this project — Built by a student, for everyone</p>
    
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 2.5rem; text-align: center; max-width: 800px; margin: 0 auto;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
        <h3 style="color: white; margin-bottom: 1rem; font-size: 1.5rem;">Anthropic AI Fluency Certificate</h3>
        <p style="color: #94A3B8; line-height: 1.8; margin-bottom: 1.5rem;">
            Built as part of Anthropic's AI Fluency program. FactLens started as a college project exploring how large language models can make information more trustworthy. It grew into a real tool for anyone who wants to know if what they're reading is actually true — powered by Groq LLM and Tavily live search.
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <a href="#" class="cta-button">▲ Verify something now</a>
            <a href="https://github.com/vedikakashyap/Fact_Lence" class="cta-button" style="background: rgba(255,255,255,0.1);">⌥ View on GitHub</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 5rem; color: #64748B;">
    <div style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 1rem;">FactLens</div>
    <div style="margin-bottom: 1rem;">
        <a href="#how-it-works" style="color: #94A3B8; text-decoration: none; margin: 0 1rem;">How it works</a>
        <a href="#features" style="color: #94A3B8; text-decoration: none; margin: 0 1rem;">Features</a>
        <a href="https://github.com/vedikakashyap/Fact_Lence" style="color: #94A3B8; text-decoration: none; margin: 0 1rem;">GitHub</a>
    </div>
    <p style="font-size: 0.9rem;">Python · Streamlit · Groq · Tavily</p>
</div>
""", unsafe_allow_html=True)
