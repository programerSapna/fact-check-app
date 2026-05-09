import streamlit as st
import PyPDF2
import json
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Configure Groq
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)

# Page config
st.set_page_config(
    page_title="FactLens — AI Fact Checker",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Header */
.hero {
    background: linear-gradient(135deg, #0d0d20 0%, #13132e 40%, #0d0d20 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 24px;
    padding: 72px 56px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 80px rgba(99,102,241,0.08), 0 0 0 1px rgba(99,102,241,0.1);
}
.hero::before {
    content: '';
    position: absolute;
    top: -100px; right: -100px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 65%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6366f1;
    margin: 0 0 16px 0;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #e0e7ff, #a5b4fc, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 16px 0;
    letter-spacing: -2px;
    line-height: 1.05;
}
.hero-sub {
    color: #4b5563;
    font-size: 1.05rem;
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.2px;
    max-width: 480px;
}

/* Upload area */
.upload-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 8px;
    display: block;
}

/* Claim cards */
.claim-card {
    background: #111120;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 12px 0;
    transition: border-color 0.2s;
}
.claim-card:hover { border-color: rgba(99,102,241,0.3); }

.claim-text {
    font-size: 0.95rem;
    color: #c4c4d4;
    margin-bottom: 12px;
    line-height: 1.5;
}

.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-verified   { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
.badge-inaccurate { background: rgba(245,158,11,0.12);  color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
.badge-false      { background: rgba(239,68,68,0.12);   color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }
.badge-unknown    { background: rgba(107,114,128,0.12); color: #9ca3af; border: 1px solid rgba(107,114,128,0.25); }

.fact-label {
    font-size: 0.72rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 4px;
}
.fact-value {
    font-size: 0.88rem;
    color: #9ca3af;
    line-height: 1.5;
}

/* Summary cards */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
}
.summary-card {
    background: #111120;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.summary-number {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
}
.summary-label {
    font-size: 0.78rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4b5563;
    margin-top: 6px;
}

/* Override Streamlit defaults */
.stFileUploader > div {
    background: #111120 !important;
    border: 1px dashed rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: #6366f1 !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}

/* Progress */
.stProgress > div > div { background: #6366f1 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #111120 !important;
    border-radius: 10px !important;
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.05) !important; }

/* Success/Error messages */
.stSuccess { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 10px !important; }
.stError   { background: rgba(239,68,68,0.08)  !important; border: 1px solid rgba(239,68,68,0.2)  !important; border-radius: 10px !important; }
.stWarning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero">
    <p class="hero-eyebrow">AI-Powered Fact Verification</p>
    <p class="hero-title">FactLens</p>
    <p class="hero-sub">Upload any PDF — AI extracts every claim and verifies it against real-world knowledge instantly.</p>
</div>
""", unsafe_allow_html=True)

# Check API key
if not api_key:
    st.error("GROQ_API_KEY not found in .env file. Add it and restart.")
    st.stop()

# Upload section
st.markdown('<span class="upload-label">Upload Document</span>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        st.success(f"Document loaded — {len(pdf_reader.pages)} page(s), {len(text)} characters extracted")

        with st.expander("Preview extracted text"):
            st.text(text[:2000] + "..." if len(text) > 2000 else text)

    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        st.stop()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Analyse Document"):

        with st.spinner("Identifying claims..."):
            try:
                extract_prompt = f"""
                From the following text, extract all factual claims that can be verified.
                Focus on: statistics, numbers, dates, percentages, named facts.

                Return ONLY a JSON array like this (no extra text, no markdown):
                [
                    {{"claim": "exact claim text", "category": "statistic/date/fact"}},
                    ...
                ]

                Text:
                {text[:3000]}
                """

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": extract_prompt}],
                    temperature=0.1
                )
                raw = response.choices[0].message.content.strip()

                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]

                claims = json.loads(raw.strip())
                st.success(f"{len(claims)} claims identified")

            except Exception as e:
                st.error(f"Error extracting claims: {e}")
                st.stop()

        st.markdown("---")
        st.markdown('<span class="upload-label">Verification Results</span>', unsafe_allow_html=True)

        results = []
        progress = st.progress(0)

        for i, item in enumerate(claims[:10]):
            claim = item.get("claim", "")
            progress.progress((i + 1) / min(len(claims), 10))

            with st.spinner(f"Verifying {i+1} of {min(len(claims), 10)}..."):
                try:
                    verify_prompt = f"""
                    Fact-check this claim: "{claim}"

                    Return ONLY a JSON object (no extra text, no markdown):
                    {{
                        "status": "VERIFIED" or "INACCURATE" or "FALSE" or "UNVERIFIABLE",
                        "actual_fact": "what is actually true",
                        "confidence": "HIGH" or "MEDIUM" or "LOW",
                        "explanation": "brief explanation"
                    }}
                    """

                    verify_response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": verify_prompt}],
                        temperature=0.1
                    )
                    raw_v = verify_response.choices[0].message.content.strip()

                    if "```json" in raw_v:
                        raw_v = raw_v.split("```json")[1].split("```")[0]
                    elif "```" in raw_v:
                        raw_v = raw_v.split("```")[1].split("```")[0]

                    result = json.loads(raw_v.strip())
                    result["claim"] = claim
                    results.append(result)

                    status = result.get("status", "UNKNOWN")

                    if status == "VERIFIED":
                        badge_class = "badge-verified"
                        badge_text = "Verified"
                        number_color = "#10b981"
                    elif status == "INACCURATE":
                        badge_class = "badge-inaccurate"
                        badge_text = "Inaccurate"
                        number_color = "#f59e0b"
                    elif status == "FALSE":
                        badge_class = "badge-false"
                        badge_text = "False"
                        number_color = "#ef4444"
                    else:
                        badge_class = "badge-unknown"
                        badge_text = "Unverifiable"
                        number_color = "#9ca3af"

                    st.markdown(f"""
                    <div class="claim-card">
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                            <span style="font-family:'Syne',sans-serif; font-weight:700; color:{number_color}; font-size:1.1rem;">#{i+1}</span>
                            <span class="badge {badge_class}">{badge_text}</span>
                            <span style="font-size:0.75rem; color:#374151; margin-left:auto;">Confidence: {result.get('confidence','N/A')}</span>
                        </div>
                        <p class="claim-text">"{claim}"</p>
                        <div class="fact-label">Actual Fact</div>
                        <div class="fact-value">{result.get('actual_fact','N/A')}</div>
                        <div style="margin-top:10px; font-size:0.82rem; color:#374151; font-style:italic;">{result.get('explanation','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.warning(f"Could not verify claim {i+1}: {e}")

        progress.empty()

        # Summary
        if results:
            verified = sum(1 for r in results if r.get("status") == "VERIFIED")
            inaccurate = sum(1 for r in results if r.get("status") == "INACCURATE")
            false_count = sum(1 for r in results if r.get("status") == "FALSE")
            unverifiable = sum(1 for r in results if r.get("status") == "UNVERIFIABLE")

            st.markdown("---")
            st.markdown('<span class="upload-label">Summary</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-number" style="color:#10b981">{verified}</div>
                    <div class="summary-label">Verified</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number" style="color:#f59e0b">{inaccurate}</div>
                    <div class="summary-label">Inaccurate</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number" style="color:#ef4444">{false_count}</div>
                    <div class="summary-label">False</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            report = json.dumps(results, indent=2)
            st.download_button(
                label="Download Full Report (JSON)",
                data=report,
                file_name="factlens_report.json",
                mime="application/json"
            )