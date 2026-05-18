import os
import streamlit as st
import pdfplumber
import json
import re
from groq import Groq
from tavily import TavilyClient

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="FactLens AI", page_icon="🔬", layout="wide")

# ── Load API keys from Render environment variables ────────────────────────────
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.error("⚠️ API keys not configured. Set GROQ_API_KEY and TAVILY_API_KEY in your Render dashboard under Environment Variables.")
    st.stop()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Global ── */
.stApp { background: #f5f2eb; color: #1a1a18; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: #1a1a18 !important;
  border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #c8c4b8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] strong { color: #f0ece2 !important; }
section[data-testid="stSidebar"] .stMarkdown { color: #908c80 !important; }

/* ── File uploader: fix invisible button text ── */
[data-testid="stFileUploaderDropzone"] {
  background: #ffffff !important;
  border: 1.5px dashed #c8c4b8 !important;
  border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] button {
  background: #1a1a18 !important;
  color: #f0ece2 !important;
  border: none !important;
  border-radius: 7px !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  padding: 0.45rem 1.2rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
  background: #3a3a32 !important;
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
  color: #7a7a72 !important;
  font-family: 'Outfit', sans-serif !important;
}
[data-testid="stFileUploaderDropzone"] svg { fill: #b8a880 !important; }
[data-testid="stFileUploaderFile"] {
  background: #f0ece2 !important;
  border: 1px solid #dedad2 !important;
  border-radius: 6px !important;
}
[data-testid="stFileUploaderFile"] span { color: #3a3a32 !important; }

/* ── Hero ── */
.hero-wrap {
  display: flex; align-items: flex-start;
  justify-content: space-between;
  padding: 3.5rem 0 2rem 0;
  border-bottom: 1px solid #d8d4ca;
  margin-bottom: 2.5rem; gap: 2rem;
}
.hero-left { flex: 1; }
.hero-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 0.7rem; font-weight: 500;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: #8a6f3c; margin-bottom: 1rem;
  display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow::before {
  content: ''; display: inline-block;
  width: 24px; height: 1px; background: #8a6f3c;
}
.hero-title {
  font-family: 'Instrument Serif', serif !important;
  font-size: 4.5rem !important; font-weight: 400 !important;
  color: #1a1a18 !important; line-height: 1.0 !important;
  letter-spacing: -0.02em; margin-bottom: 1.2rem !important;
}
.hero-title em { font-style: italic; color: #7a5c28; }
.hero-desc {
  font-size: 1rem !important; color: #5a5a52 !important;
  line-height: 1.7; font-weight: 300; max-width: 420px;
}
.hero-right {
  display: flex; flex-direction: column;
  gap: 1rem; align-items: flex-end;
  min-width: 180px; padding-top: 0.5rem;
}
.hero-stat { text-align: right; }
.hero-stat-num {
  font-family: 'Instrument Serif', serif;
  font-size: 2.4rem; color: #1a1a18; line-height: 1;
}
.hero-stat-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.6rem; color: #9a9a8e;
  letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px;
}

/* ── Section label ── */
.section-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: #9a9a8e;
  margin: 2.5rem 0 1.2rem 0;
  display: flex; align-items: center; gap: 12px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: #d8d4ca; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #e8e4da !important; border-radius: 8px !important;
  padding: 4px !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 5px !important; font-family: 'Outfit', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  color: #7a7a72 !important; background: transparent !important;
  padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] { background: #1a1a18 !important; color: #f0ece2 !important; }

/* ── Text area ── */
.stTextArea textarea {
  background: #ffffff !important; border: 1px solid #dedad2 !important;
  border-radius: 8px !important; font-family: 'Outfit', sans-serif !important;
  font-size: 0.9rem !important; color: #2a2a22 !important;
}

/* ── CTA button ── */
.stButton > button {
  background: #1a1a18 !important; color: #f0ece2 !important;
  border: none !important; border-radius: 8px !important;
  padding: 0.65rem 2rem !important; font-family: 'Outfit', sans-serif !important;
  font-weight: 500 !important; font-size: 0.9rem !important;
  width: 100% !important; letter-spacing: 0.01em;
}
.stButton > button:hover { background: #2a2a26 !important; }

/* ── Claim card ── */
.claim-card {
  background: #ffffff; border: 1px solid #dedad2;
  border-radius: 12px; padding: 1.6rem 1.8rem;
  margin-bottom: 1rem; transition: border-color 0.2s;
}
.claim-card:hover { border-color: #c8c4b8; }
.claim-card-verified     { border-top: 3px solid #2d7a4a; }
.claim-card-inaccurate   { border-top: 3px solid #c97a1a; }
.claim-card-false        { border-top: 3px solid #c43a3a; }
.claim-card-unverifiable { border-top: 3px solid #9a9a8e; }

.claim-header { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:1rem; }
.claim-num {
  font-family:'DM Mono',monospace; font-size:0.62rem;
  font-weight:500; letter-spacing:0.1em; color:#9a9a8e;
  background:#f0ece2; padding:3px 10px; border-radius:4px;
}
.claim-cat {
  font-size:0.68rem; font-weight:500; color:#7a5c28;
  background:#f5ead8; border:1px solid #e8d8b8; padding:3px 10px; border-radius:4px;
}
.verdict-pill-verified    { background:#eaf5ed; color:#1a5c30; border:1px solid #b8e0c4; font-size:0.72rem; font-weight:600; padding:3px 12px; border-radius:100px; }
.verdict-pill-inaccurate  { background:#faf0e0; color:#7a4a08; border:1px solid #e8cc90; font-size:0.72rem; font-weight:600; padding:3px 12px; border-radius:100px; }
.verdict-pill-false        { background:#faeaea; color:#7a1a1a; border:1px solid #e8b0b0; font-size:0.72rem; font-weight:600; padding:3px 12px; border-radius:100px; }
.verdict-pill-unverifiable { background:#f0ece2; color:#5a5a52; border:1px solid #d0ccc0; font-size:0.72rem; font-weight:600; padding:3px 12px; border-radius:100px; }

.claim-text {
  font-family:'Instrument Serif',serif; font-size:1.12rem;
  color:#2a2a22; line-height:1.6; font-style:italic; margin-bottom:1.2rem;
}
.claim-divider { border:none; border-top:1px solid #ece8e0; margin:1rem 0; }

/* ── Confidence bar ── */
.conf-wrap { margin-bottom: 1rem; }
.conf-label-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; }
.conf-label { font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.1em; text-transform:uppercase; color:#9a9a8e; }
.conf-value { font-family:'DM Mono',monospace; font-size:0.75rem; font-weight:500; color:#3a3a32; }
.conf-track { width:100%; height:5px; background:#ece8e0; border-radius:100px; overflow:hidden; }
.conf-fill-verified     { height:100%; background:#2d7a4a; border-radius:100px; }
.conf-fill-inaccurate   { height:100%; background:#c97a1a; border-radius:100px; }
.conf-fill-false        { height:100%; background:#c43a3a; border-radius:100px; }
.conf-fill-unverifiable { height:100%; background:#9a9a8e; border-radius:100px; }

/* ── Sub-labels ── */
.sub-label { font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.12em; text-transform:uppercase; color:#7a5c28; margin-bottom:4px; }
.sub-text    { font-size:0.86rem; color:#5a5a52; line-height:1.6; margin-bottom:0.9rem; }
.sub-text-em { font-size:0.9rem;  color:#3a3a32; line-height:1.65; }

/* ── Source chips ── */
.sources-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:0.8rem; }
.source-chip {
  display:inline-flex; align-items:center; gap:5px;
  background:#f5f2eb; border:1px solid #dedad2; border-radius:6px;
  padding:4px 10px; font-size:0.73rem; color:#5a5a52; text-decoration:none;
  max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.source-chip:hover { border-color:#9a9a8e; color:#2a2a22; }
.source-dot { width:6px; height:6px; border-radius:50%; background:#b8a880; flex-shrink:0; }

/* ── Summary grid ── */
.summary-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:1.5rem 0 2.5rem 0; }
.summary-cell { background:#ffffff; border:1px solid #dedad2; border-radius:10px; padding:1.2rem 1rem; text-align:center; }
.summary-num { font-family:'Instrument Serif',serif; font-size:2.4rem; line-height:1; margin-bottom:4px; }
.summary-num-verified     { color:#2d7a4a; }
.summary-num-inaccurate   { color:#c97a1a; }
.summary-num-false        { color:#c43a3a; }
.summary-num-unverifiable { color:#9a9a8e; }
.summary-cell-label { font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.12em; text-transform:uppercase; color:#9a9a8e; }

/* ── Heatmap ── */
.heatmap-wrap { background:#ffffff; border:1px solid #dedad2; border-radius:12px; padding:1.4rem 1.8rem; margin-bottom:2rem; }
.heatmap-title { font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:#9a9a8e; margin-bottom:1rem; }
.heatmap-bar-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.heatmap-bar-label { font-size:0.8rem; color:#5a5a52; width:100px; flex-shrink:0; }
.heatmap-bar-track { flex:1; height:20px; background:#f0ece2; border-radius:4px; overflow:hidden; }
.heatmap-bar-fill {
  height:100%; border-radius:4px; display:flex; align-items:center; padding-left:8px;
  font-family:'DM Mono',monospace; font-size:0.63rem; font-weight:500;
  color:rgba(255,255,255,0.92); min-width:26px;
}

/* ── Export note ── */
.export-note {
  background:#faf0e0; border:1px solid #e8d8b0; border-radius:8px;
  padding:0.8rem 1.2rem; font-size:0.8rem; color:#7a5c28; margin-top:1rem;
  font-family:'DM Mono',monospace; letter-spacing:0.03em;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    if any(w in cl for w in ["diagnos","detect","disease","cancer","diabetes","heart","clinical"]):
        return "Diagnostics"
    if any(w in cl for w in ["drug","treatment","therap","medicine","dose","prescri"]):
        return "Treatment"
    if any(w in cl for w in ["data","patient record","dataset","privacy","security","breach"]):
        return "Data & Privacy"
    if any(w in cl for w in ["bias","ethic","fairness","disparit","discriminat"]):
        return "Ethics & Bias"
    if any(w in cl for w in ["chatbot","virtual","assistant","workflow","admin","automat","llm","gpt"]):
        return "AI Systems"
    if any(w in cl for w in ["fund","financ","cost","resource","budget","invest"]):
        return "Funding"
    if any(w in cl for w in ["legal","regulat","framework","law","comply","gdpr"]):
        return "Legal"
    if any(w in cl for w in ["study","research","trial","experiment","result"]):
        return "Research"
    return "General"


def confidence_from_verdict(verdict, explanation):
    base  = {"Verified": 82, "Inaccurate": 58, "False": 30, "Unverifiable": 15}
    score = base.get(verdict, 15)
    bonus = min(len(explanation) // 40, 10)
    return min(score + bonus, 99)


def domain_from_url(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url[:40]


# ── Sidebar (info only — no API key inputs needed) ────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 FactLens AI")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
1. **Extract** — AI finds factual claims
2. **Categorise** — Topic tags applied
3. **Purpose** — Why the claim matters
4. **Search** — Live web search
5. **Score** — Confidence 0–100%
6. **Verdict** — Verified / Inaccurate / False / Unverifiable
7. **Sources** — Real URLs cited
""")
    st.markdown("---")
    st.markdown("**Supported inputs**")
    st.markdown("📄 PDF documents\n\n✏️ Pasted text\n\nResearch papers, news articles, reports, transcripts")
    st.markdown("---")
    st.caption("Built with Groq · Tavily · Streamlit")
    st.caption("Model: llama-3.3-70b-versatile")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-left">
    <div class="hero-eyebrow">AI-Powered Fact Verification</div>
    <div class="hero-title">Fact<em>Lens</em></div>
    <p class="hero-desc">
      Drop any PDF or paste text — we extract every claim, search the live web,
      score confidence, cite real sources, and return a clean verdict.
    </p>
  </div>
  <div class="hero-right">
    <div class="hero-stat">
      <div class="hero-stat-num">3–8</div>
      <div class="hero-stat-label">Claims per doc</div>
    </div>
    <div class="hero-stat">
      <div class="hero-stat-num">live</div>
      <div class="hero-stat-label">Web sources</div>
    </div>
    <div class="hero-stat">
      <div class="hero-stat-num">0→99%</div>
      <div class="hero-stat-label">Confidence score</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Input Tabs ────────────────────────────────────────────────────────────────
tab_pdf, tab_text = st.tabs(["📄  PDF Upload", "✏️  Paste Text"])

extracted_text = ""
source_name    = ""

with tab_pdf:
    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type="pdf",
        label_visibility="collapsed"
    )
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""
        source_name = uploaded_file.name
        st.success(f"✅ **{uploaded_file.name}** — {len(extracted_text):,} characters extracted")

with tab_text:
    pasted = st.text_area(
        "Paste article, abstract, or any text here",
        height=220,
        placeholder="Paste any news article, research abstract, speech transcript, or claim-rich text here...",
        label_visibility="collapsed"
    )
    if pasted.strip():
        extracted_text = pasted.strip()
        source_name    = "Pasted text"
        st.success(f"✅ {len(extracted_text):,} characters ready")


# ── Main Flow ─────────────────────────────────────────────────────────────────
if not extracted_text:
    st.info("📄 Upload a PDF or paste text above to begin fact-checking.")
else:
    if st.button("🔬  Extract & Verify All Claims"):

        # Step 1 — Extract claims
        with st.spinner("🤖 Extracting factual claims from document..."):
            client = Groq(api_key=GROQ_API_KEY)
            prompt = f"""
You are an expert fact-checking assistant. From the text below, extract between 3 and 8 specific, verifiable claims.

For each claim provide:
- "claim": the full factual assertion as stated or implied (one sentence)
- "purpose": one sentence explaining WHY this claim matters to a non-expert reader
- "category": one of [Diagnostics, Treatment, Data & Privacy, Ethics & Bias, AI Systems, Funding, Legal, Research, General]

Return ONLY valid JSON array. No markdown, no preamble.

Format:
[
  {{
    "claim": "...",
    "purpose": "This claim establishes that ...",
    "category": "Research"
  }}
]

Text:
{extracted_text[:4500]}
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw         = response.choices[0].message.content.strip()
            claims_data = extract_json_array(raw)

        normalised = []
        for item in claims_data:
            if isinstance(item, dict):
                normalised.append({
                    "claim":    item.get("claim", str(item)),
                    "purpose":  item.get("purpose", ""),
                    "category": item.get("category", get_category(item.get("claim", "")))
                })
            else:
                c = str(item)
                normalised.append({"claim": c, "purpose": "", "category": get_category(c)})

        if not normalised:
            st.error("❌ Could not extract claims. Try a longer or more specific piece of text.")
            st.stop()

        # Step 2 — Verify each claim
        st.markdown('<div class="section-label">Claim Verification</div>', unsafe_allow_html=True)

        tavily      = TavilyClient(api_key=TAVILY_API_KEY)
        counts      = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
        all_results = []

        for i, item in enumerate(normalised):
            claim    = item["claim"]
            purpose  = item["purpose"]
            category = item["category"]

            with st.spinner(f"Verifying claim {i+1} of {len(normalised)}..."):

                # Web search
                snippets, source_urls = "", []
                try:
                    sr          = tavily.search(query=claim, search_depth="basic", max_results=4)
                    results     = sr.get("results", [])
                    snippets    = " ".join(r.get("content", "") for r in results)
                    source_urls = [r.get("url", "") for r in results if r.get("url")]
                except Exception:
                    pass

                if not snippets.strip():
                    try:
                        short_q     = " ".join(claim.split()[:8])
                        sr          = tavily.search(query=short_q, search_depth="basic", max_results=3)
                        results     = sr.get("results", [])
                        snippets    = " ".join(r.get("content", "") for r in results)
                        source_urls = [r.get("url", "") for r in results if r.get("url")]
                    except Exception:
                        pass

                # LLM verdict
                if not snippets.strip():
                    verdict     = "Unverifiable"
                    explanation = "No web sources could be found to verify or contradict this claim."
                else:
                    vp = f"""
You are a careful fact-checker. Based ONLY on the web results below, verify the claim.

Claim: "{claim}"

Web Results:
{snippets[:2500]}

Return ONLY valid JSON (no markdown):
{{"verdict": "Verified", "explanation": "one clear sentence explaining your verdict and the key evidence"}}

verdict must be exactly one of: "Verified", "Inaccurate", "False", "Unverifiable"
"""
                    vr = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": vp}],
                        temperature=0
                    )
                    vd          = extract_json_object(vr.choices[0].message.content.strip())
                    verdict     = vd.get("verdict",     "Unverifiable") if vd else "Unverifiable"
                    explanation = vd.get("explanation", "No explanation available.") if vd else "Could not parse response."

                counts[verdict] = counts.get(verdict, 0) + 1
                confidence      = confidence_from_verdict(verdict, explanation)

                all_results.append({
                    "claim":       claim,
                    "verdict":     verdict,
                    "explanation": explanation,
                    "purpose":     purpose,
                    "category":    category,
                    "confidence":  confidence,
                    "source_urls": source_urls   # list[str] — JSON serialisable
                })

            # Render card
            v_lc  = verdict.lower()
            icons = {
                "Verified":     "✅ Verified",
                "Inaccurate":   "⚠️ Inaccurate",
                "False":        "❌ False",
                "Unverifiable": "○ Unverifiable"
            }

            sources_html = ""
            if source_urls:
                chips = "".join(
                    f'<a class="source-chip" href="{u}" target="_blank">'
                    f'<span class="source-dot"></span>{domain_from_url(u)}</a>'
                    for u in source_urls[:4]
                )
                sources_html = (
                    f'<div class="sub-label" style="margin-top:0.9rem;">Web Sources</div>'
                    f'<div class="sources-row">{chips}</div>'
                )

            purpose_html = (
                f'<div class="sub-label">Why This Claim Matters</div>'
                f'<div class="sub-text">{purpose}</div>'
            ) if purpose else ""

            st.markdown(f"""
<div class="claim-card claim-card-{v_lc}">
  <div class="claim-header">
    <span class="claim-num">CLAIM {i+1:02d}</span>
    <span class="claim-cat">{category}</span>
    <span class="verdict-pill-{v_lc}">{icons[verdict]}</span>
  </div>
  <div class="claim-text">"{claim}"</div>
  <div class="conf-wrap">
    <div class="conf-label-row">
      <span class="conf-label">Confidence Score</span>
      <span class="conf-value">{confidence}%</span>
    </div>
    <div class="conf-track">
      <div class="conf-fill-{v_lc}" style="width:{confidence}%;"></div>
    </div>
  </div>
  <hr class="claim-divider">
  {purpose_html}
  <div class="sub-label">Verification Finding</div>
  <div class="sub-text-em">{explanation}</div>
  {sources_html}
</div>
""", unsafe_allow_html=True)

        # ── Summary ────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="summary-grid">
  <div class="summary-cell">
    <div class="summary-num summary-num-verified">{counts['Verified']}</div>
    <div class="summary-cell-label">Verified</div>
  </div>
  <div class="summary-cell">
    <div class="summary-num summary-num-inaccurate">{counts['Inaccurate']}</div>
    <div class="summary-cell-label">Inaccurate</div>
  </div>
  <div class="summary-cell">
    <div class="summary-num summary-num-false">{counts['False']}</div>
    <div class="summary-cell-label">False</div>
  </div>
  <div class="summary-cell">
    <div class="summary-num summary-num-unverifiable">{counts['Unverifiable']}</div>
    <div class="summary-cell-label">Unverifiable</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Credibility heatmap ────────────────────────────────────────────────
        total = sum(counts.values()) or 1
        bars  = [
            ("Verified",     counts["Verified"],     "#2d7a4a"),
            ("Inaccurate",   counts["Inaccurate"],   "#c97a1a"),
            ("False",        counts["False"],         "#c43a3a"),
            ("Unverifiable", counts["Unverifiable"], "#9a9a8e"),
        ]
        bars_html = ""
        for label, count, color in bars:
            pct = int(count / total * 100)
            num = str(count) if count > 0 else ""
            bars_html += f"""
<div class="heatmap-bar-row">
  <div class="heatmap-bar-label">{label}</div>
  <div class="heatmap-bar-track">
    <div class="heatmap-bar-fill" style="width:{max(pct,0)}%;background:{color};">{num}</div>
  </div>
  <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#9a9a8e;width:32px;text-align:right;">{pct}%</span>
</div>"""

        avg_conf = int(sum(r["confidence"] for r in all_results) / len(all_results)) if all_results else 0
        st.markdown(f"""
<div class="heatmap-wrap">
  <div class="heatmap-title">Credibility Breakdown — {len(all_results)} claims · avg confidence {avg_conf}%</div>
  {bars_html}
</div>
""", unsafe_allow_html=True)

        # ── Export ─────────────────────────────────────────────────────────────
        export_data = {
            "source":             source_name,
            "total_claims":       len(all_results),
            "average_confidence": avg_conf,
            "summary":            counts,
            "claims":             all_results   # source_urls are list[str] — fully serialisable
        }
        st.download_button(
            label="⬇️  Download Full Report (JSON)",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name="factlens_report.json",
            mime="application/json"
        )
        st.markdown("""
<div class="export-note">
  Tip — import this JSON into Excel, Notion, or any dashboard for further analysis.
</div>
""", unsafe_allow_html=True)
