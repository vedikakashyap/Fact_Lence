import streamlit as st
import pdfplumber
import json
import re
from groq import Groq
from tavily import TavilyClient

# --- Page Config ---
st.set_page_config(page_title="FactLens AI", page_icon="🔬", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

.stApp { background: #0a0f1e; color: #e8eaf0; }

section[data-testid="stSidebar"] { background: #0d1428 !important; border-right: 1px solid #1e2a45; }
section[data-testid="stSidebar"] * { color: #c8cfe8 !important; }
section[data-testid="stSidebar"] input { background: #111c35 !important; border: 1px solid #1e3a6e !important; color: #e8eaf0 !important; border-radius: 8px !important; }

.hero { text-align: center; padding: 3rem 0 2rem 0; }
.hero-badge { display: inline-block; background: linear-gradient(135deg, #1e3a6e, #0d2348); border: 1px solid #2a4d8f; color: #7eb8ff; font-size: 0.7rem; font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase; padding: 6px 18px; border-radius: 100px; margin-bottom: 1.2rem; }
.hero h1 { font-family: 'Syne', sans-serif !important; font-size: 3.2rem !important; font-weight: 800 !important; color: #ffffff !important; letter-spacing: -0.02em; margin: 0 0 0.6rem 0 !important; line-height: 1.1 !important; }
.hero h1 span { background: linear-gradient(135deg, #4f8ef7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero p { color: #7a8ab0 !important; font-size: 1.05rem !important; font-weight: 300; max-width: 520px; margin: 0 auto !important; line-height: 1.6; }

.stat-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
.stat-card { flex: 1; background: #0d1428; border: 1px solid #1e2a45; border-radius: 12px; padding: 1rem 1.2rem; text-align: center; }
.stat-num { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #4f8ef7; line-height: 1; }
.stat-label { font-size: 0.72rem; color: #5a6a90; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }

.section-header { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #c8d4f0; text-transform: uppercase; letter-spacing: 0.08em; margin: 2rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px solid #1e2a45; }

.claim-card { background: #0d1428; border: 1px solid #1e2a45; border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }
.claim-card:hover { border-color: #2a4060; }
.claim-card-verified   { border-left: 4px solid #22c55e; }
.claim-card-inaccurate { border-left: 4px solid #f59e0b; }
.claim-card-false      { border-left: 4px solid #ef4444; }
.claim-card-unverifiable { border-left: 4px solid #6b7280; }

.claim-top-row { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem; flex-wrap: wrap; }
.claim-number { background: #111c38; border: 1px solid #1e2a45; color: #5a7ab0; font-family: 'Syne', sans-serif; font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 100px; letter-spacing: 0.05em; }
.claim-category { font-size: 0.68rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #7a8ab0; padding: 2px 10px; background: #111c38; border-radius: 100px; border: 1px solid #1e2a45; }

.verdict-badge-verified     { background: #052e16; color: #4ade80; border: 1px solid #166534; padding: 3px 12px; border-radius: 100px; font-size: 0.72rem; font-weight: 600; }
.verdict-badge-inaccurate   { background: #451a03; color: #fbbf24; border: 1px solid #92400e; padding: 3px 12px; border-radius: 100px; font-size: 0.72rem; font-weight: 600; }
.verdict-badge-false        { background: #2d0707; color: #f87171; border: 1px solid #7f1d1d; padding: 3px 12px; border-radius: 100px; font-size: 0.72rem; font-weight: 600; }
.verdict-badge-unverifiable { background: #111827; color: #9ca3af; border: 1px solid #374151; padding: 3px 12px; border-radius: 100px; font-size: 0.72rem; font-weight: 600; }

.claim-text { font-size: 0.98rem; color: #c8d4f0; line-height: 1.6; font-weight: 400; margin-bottom: 0.8rem; }
.claim-divider { border: none; border-top: 1px solid #1a2540; margin: 0.8rem 0; }
.claim-purpose-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #4f8ef7; margin-bottom: 0.3rem; }
.claim-purpose-text { font-size: 0.85rem; color: #8a9ab8; line-height: 1.55; font-style: italic; }
.claim-explanation-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #a78bfa; margin: 0.7rem 0 0.3rem 0; }
.claim-explanation-text { font-size: 0.88rem; color: #c0cce8; line-height: 1.55; }

.stButton > button { background: linear-gradient(135deg, #1a4fbd, #7c3aed) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 0.6rem 2rem !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; font-size: 0.95rem !important; width: 100% !important; }

.summary-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin: 0.5rem 0 1.5rem 0; }
.summary-pill { display: flex; align-items: center; gap: 6px; background: #0d1428; border: 1px solid #1e2a45; border-radius: 100px; padding: 5px 14px; font-size: 0.78rem; color: #8a9ab8; font-weight: 500; }
.dot-green  { width:8px; height:8px; background:#22c55e; border-radius:50%; display:inline-block; }
.dot-yellow { width:8px; height:8px; background:#f59e0b; border-radius:50%; display:inline-block; }
.dot-red    { width:8px; height:8px; background:#ef4444; border-radius:50%; display:inline-block; }
.dot-gray   { width:8px; height:8px; background:#6b7280; border-radius:50%; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# --- Hero ---
st.markdown("""
<div class="hero">
    <div class="hero-badge">🔬 AI-Powered Verification</div>
    <h1>Fact<span>Lens</span></h1>
    <p>Upload any PDF — we extract every claim, explain its purpose, and verify it against live web sources.</p>
</div>
""", unsafe_allow_html=True)

# --- Helpers ---
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

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🔑 API Keys")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")
    st.markdown("---")
    st.markdown("##### How it works")
    st.markdown("""
1. **Extract** — LLM finds factual claims  
2. **Categorize** — Each claim gets a topic tag  
3. **Purpose** — Why this claim matters is explained  
4. **Search** — Tavily searches the live web  
5. **Verdict** — Verified / Inaccurate / False / Unverifiable
""")
    st.caption("Keys are never stored or logged.")

# --- Upload ---
uploaded_file = st.file_uploader("📄 Upload your PDF", type="pdf")

if uploaded_file and groq_key and tavily_key:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    st.success(f"✅ **{uploaded_file.name}** uploaded — {len(text):,} characters extracted")

    if st.button("🔬 Extract & Verify All Claims"):

        with st.spinner("🤖 Analysing document and extracting claims..."):
            client = Groq(api_key=groq_key)

            prompt = f"""
You are an expert fact-checking assistant. From the text below, extract between 3 and 8 specific, verifiable claims.

For each claim also write:
- "purpose": one sentence explaining WHY this claim matters or what it is trying to establish in the document (for a non-expert reader)
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

Rules:
- Prefer concrete assertions; include qualitative ones if they are the main point
- Each claim must be a full sentence

Text:
{text[:4000]}
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = response.choices[0].message.content.strip()
            claims_data = extract_json_array(raw)

        # Normalise
        normalised = []
        for item in claims_data:
            if isinstance(item, dict):
                normalised.append({
                    "claim": item.get("claim", str(item)),
                    "purpose": item.get("purpose", ""),
                    "category": item.get("category", get_category(item.get("claim", "")))
                })
            else:
                normalised.append({
                    "claim": str(item),
                    "purpose": "",
                    "category": get_category(str(item))
                })

        if not normalised:
            st.error("❌ Could not extract claims. The text may be too vague.")
            st.stop()

        # Stats row
        st.markdown(f"""
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-num">{len(normalised)}</div>
    <div class="stat-label">Claims Found</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{len(set(c['category'] for c in normalised))}</div>
    <div class="stat-label">Topics Covered</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{len(text):,}</div>
    <div class="stat-label">Characters Scanned</div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">📋 Claim Verification Results</div>', unsafe_allow_html=True)

        tavily = TavilyClient(api_key=tavily_key)
        counts = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}

        for i, item in enumerate(normalised):
            claim    = item["claim"]
            purpose  = item["purpose"]
            category = item["category"]

            with st.spinner(f"Verifying claim {i+1} of {len(normalised)}..."):
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
                            temperature=0
                        )
                        vd = extract_json_object(vr.choices[0].message.content.strip())
                        verdict     = vd.get("verdict", "Unverifiable") if vd else "Unverifiable"
                        explanation = vd.get("explanation", "No explanation.") if vd else "Could not parse response."

                    counts[verdict] = counts.get(verdict, 0) + 1

                    badge_class = f"verdict-badge-{verdict.lower()}"
                    card_class  = f"claim-card-{verdict.lower()}"
                    icons = {"Verified": "✅ Verified", "Inaccurate": "⚠️ Inaccurate", "False": "❌ False", "Unverifiable": "⬜ Unverifiable"}
                    icon_label = icons.get(verdict, verdict)

                    purpose_html = f"""
<div class="claim-purpose-label">📌 Why This Claim Matters</div>
<div class="claim-purpose-text">{purpose if purpose else "This claim supports a key assertion in the document."}</div>
""" if True else ""

                    st.markdown(f"""
<div class="claim-card {card_class}">
  <div class="claim-top-row">
    <span class="claim-number">CLAIM {i+1}</span>
    <span class="claim-category">{category}</span>
    <span class="{badge_class}">{icon_label}</span>
  </div>
  <div class="claim-text">"{claim}"</div>
  <hr class="claim-divider">
  {purpose_html}
  <div class="claim-explanation-label">🔎 Verification Finding</div>
  <div class="claim-explanation-text">{explanation}</div>
</div>
""", unsafe_allow_html=True)

                except Exception as e:
                    st.warning(f"Could not verify claim {i+1}: {str(e)}")

        # Summary
        dot = {"Verified": "dot-green", "Inaccurate": "dot-yellow", "False": "dot-red", "Unverifiable": "dot-gray"}
        pills = "".join([
            f'<div class="summary-pill"><span class="{dot[k]}"></span>{counts[k]} {k}</div>'
            for k in ["Verified", "Inaccurate", "False", "Unverifiable"] if counts[k] > 0
        ])
        st.markdown(f'<div class="section-header">📊 Summary</div><div class="summary-bar">{pills}</div>', unsafe_allow_html=True)

else:
    if not groq_key or not tavily_key:
        st.info("👈 Enter your Groq and Tavily API keys in the sidebar to get started.")
    if not uploaded_file:
        st.info("📄 Upload a PDF above to begin fact-checking.")