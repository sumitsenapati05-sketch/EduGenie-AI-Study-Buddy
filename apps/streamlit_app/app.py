import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st
import os

# Import configuration
try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = "output"

from core.io import process_file
from core.export_pdf import export_summary_to_pdf

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="EduGenie - AI Study Buddy",
    page_icon="🧠",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    /* Keyword chips */
    .keyword-chip {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a5f, #2563eb);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* Summary box */
    .summary-box {
        background: #0f172a;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 18px 20px;
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.8;
        margin-top: 8px;
    }

    /* Quiz item */
    .quiz-item {
        background: #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #f1f5f9;
        font-size: 14px;
        border-left: 3px solid #f59e0b;
    }

    .quiz-number {
        color: #f59e0b;
        font-weight: bold;
        margin-right: 8px;
    }

    /* Flashcard */
    .flashcard {
        background: #1e293b;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 10px 0;
        border-top: 3px solid #10b981;
    }

    .flashcard-q {
        color: #10b981;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .flashcard-a {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Section header */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 24px;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 2px solid #334155;
    }

    /* Success banner */
    .success-banner {
        background: #064e3b;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 10px 16px;
        color: #6ee7b7;
        font-size: 14px;
        margin: 10px 0;
    }

    /* Groq badge */
    .groq-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

for key, default in {
    'api_key': "",
    'summary': "",
    'keywords': [],
    'quiz': [],
    'flashcards': [],
    'file_processed': False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------- OUTPUT DIRECTORY ----------------

OUTPUT_PATH = Path(OUTPUT_DIR)
OUTPUT_PATH.mkdir(exist_ok=True)

# ---------------- HEADER ----------------

col1, col2 = st.columns([1, 2.5])

with col1:
    logo_path = "assets/images/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)
    else:
        st.markdown("### 🧞")

with col2:
    st.title("EduGenie - AI Powered Study Buddy")
    st.subheader("by Sumit Senapati")
    st.caption("Smart AI assistant for summaries, quizzes, flashcards & concept explanation")
    st.info("🚀 AI Powered Educational Assistant using NLP & OCR")

st.markdown("---")

# ---------------- API KEY ----------------

api_key = st.text_input(
    "🔑 Enter Groq API Key (for AI-powered mode)",
    value=st.session_state.api_key or "",
    type="password",
    placeholder="gsk_..."
)
st.caption("Optional — leave blank to use Offline NLP mode automatically")

if api_key != st.session_state.api_key:
    st.session_state.api_key = api_key

# Show key status
if st.session_state.api_key:
    st.success("✅ Groq API Key detected — AI mode available!")
else:
    st.warning("⚠️ No API key — Offline NLP mode will be used")

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "📂 Upload Notes / Handwritten Classroom Images (PDF, TXT, PNG, JPG)",
    type=['pdf', 'txt', 'png', 'jpg', 'jpeg']
)

# ---------------- PROCESS FILE ----------------

if uploaded_file is not None:

    file_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.markdown("### ⚙️ Processing Options")

    mode = st.radio(
        "Processing Mode",
        [
            "🔒 Offline NLP (Private, No Key Needed)",
            "🤖 Online — Groq AI (Faster & Smarter, Requires Key)",
        ],
        index=0
    )

    selected_mode = "offline" if "Offline" in mode else "online"

    # Warn if Groq selected but no key
    if selected_mode == "online" and not st.session_state.api_key:
        st.warning("⚠️ Groq AI selected but no API key entered — will auto-switch to Offline mode.")

    # ---------------- SUMMARY LENGTH ----------------

    st.markdown("#### 📏 Summary Length")

    col1, col2 = st.columns(2)

    with col1:
        min_length = st.number_input("Min Words", min_value=10, max_value=100, value=30)

    with col2:
        max_length = st.number_input("Max Words", min_value=50, max_value=500, value=150)

    # ---------------- PROCESS BUTTON ----------------

    if st.button("🧠 Process Document", use_container_width=True):

        try:
            # Decide spinner label
            spinner_label = (
                "⏳ Groq AI is analysing your document..."
                if selected_mode == "online" and st.session_state.api_key
                else "⏳ Offline NLP is analysing your document..."
            )

            with st.spinner(spinner_label):

                result = process_file(
                    file_path=file_path,
                    mode=selected_mode,
                    api_key=st.session_state.api_key,
                    min_length=min_length,
                    max_length=max_length
                )

                st.session_state.summary    = result["summary"]
                st.session_state.keywords   = result["keywords"]
                st.session_state.quiz       = result["quiz"]
                st.session_state.flashcards = result["flashcards"]
                st.session_state.file_processed = True

            st.markdown('<div class="success-banner">✅ Document processed successfully!</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")

# ---------------- RESULTS ----------------

if st.session_state.file_processed:

    st.markdown("---")
    st.markdown("## 📝 AI Processing Results")

    # ---------------- SUMMARY ----------------

    st.markdown('<div class="section-header">📝 AI Generated Summary</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="summary-box">{st.session_state.summary}</div>',
        unsafe_allow_html=True
    )

    # ---------------- KEYWORDS ----------------

    st.markdown('<div class="section-header">📌 Important Topics Detected</div>', unsafe_allow_html=True)

    if st.session_state.keywords:
        chips_html = "".join(
            f'<span class="keyword-chip">{kw}</span>'
            for kw in st.session_state.keywords
        )
        st.markdown(f'<div style="margin-top:8px">{chips_html}</div>', unsafe_allow_html=True)
    else:
        st.write("No keywords found.")

    # ---------------- QUIZ ----------------

    st.markdown('<div class="section-header">❓ AI Quiz Generator</div>', unsafe_allow_html=True)

    for i, q in enumerate(st.session_state.quiz, 1):
        st.markdown(
            f'<div class="quiz-item"><span class="quiz-number">Q{i}.</span>{q}</div>',
            unsafe_allow_html=True
        )

    # ---------------- FLASHCARDS ----------------

    st.markdown('<div class="section-header">🧠 AI Flashcards</div>', unsafe_allow_html=True)
    st.caption(f"Total: {len(st.session_state.flashcards)} flashcards generated")

    for i, card in enumerate(st.session_state.flashcards, 1):
        with st.expander(f"📖 Card {i}: {card['question']}", expanded=False):
            st.markdown(
                f"""
                <div class="flashcard">
                    <div class="flashcard-q">💡 {card['question']}</div>
                    <div class="flashcard-a">{card['answer']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ---------------- EXPORT SUMMARY ----------------

    st.markdown("---")
    st.markdown('<div class="section-header">📄 Export Summary</div>', unsafe_allow_html=True)

    if st.button("📥 Export Summary as PDF", use_container_width=True):

        try:
            pdf_path = export_summary_to_pdf(st.session_state.summary)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name="EduGenie_Summary.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.success("✅ PDF exported successfully!")

        except Exception as e:
            st.error(f"❌ PDF export failed: {str(e)}")

# ---------------- FOOTER ----------------

st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#64748b; font-size:13px;">🧠 EduGenie - AI Powered Study Buddy &nbsp;|&nbsp; Built by Sumit Senapati</p>',
    unsafe_allow_html=True
)