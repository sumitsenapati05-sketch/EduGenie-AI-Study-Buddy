<div align="center">

<img src="assets/images/logo.png" alt="EduGenie Logo" width="160"/>

# EduGenie — AI Powered Study Buddy

**Transform your notes into summaries, quizzes, and flashcards — instantly.**  
Powered by Groq LLM (online) and NLP (offline). Works with any subject.

<p>
  <a href="https://edugenie-ai-study-buddy-smpkdynmuotsrylvjyw74m.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚀 Live Demo-Streamlit-ff4b4b?style=for-the-badge&logo=streamlit" />
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  &nbsp;
  <img src="https://img.shields.io/badge/Groq LLM-Powered-orange?style=for-the-badge" />
  &nbsp;
  <img src="https://img.shields.io/badge/Offline Mode-Available-green?style=for-the-badge" />
  &nbsp;
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" />
  </a>
</p>

</div>

---

## 📌 What is EduGenie?

EduGenie is an AI-powered educational assistant built for students. Upload your handwritten notes, PDFs, or classroom images and EduGenie will instantly:

- Generate a **clean, intelligent summary** of your notes
- Detect **important topics and keywords**
- Create **quiz questions** tailored to your content
- Build **flashcards** with real definitions — not generic placeholders

It works for **any subject** — DBMS, Java, Physics, Chemistry, History, Mathematics, and more.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 AI Summary | Intelligent summarization using Groq LLM or offline NLP |
| 📌 Keyword Detection | Extracts important topics and concepts from your notes |
| ❓ Quiz Generator | Generates varied, subject-aware quiz questions |
| 🃏 Flashcards | Auto-generates flashcards with real answers |
| 📷 OCR Support | Reads handwritten notes and scanned PDFs via Tesseract |
| 🔒 Offline Mode | Full functionality without any API key or internet |
| 🌐 Online Mode | Groq LLM (Llama 3) for smarter, any-subject understanding |
| 📄 PDF Export | Export your summary as a downloadable PDF |

---

## 🖥️ Live Demo

👉 **[Try EduGenie on Streamlit](https://edugenie-ai-study-buddy-smpkdynmuotsrylvjyw74m.streamlit.app/)**

Upload any notes file (PDF, TXT, PNG, JPG) and see results in seconds.

---

## 📁 Project Structure

```
EduGenie/
├── assets/
│   └── images/
│       └── logo.png
├── core/                        # Core business logic
│   ├── summarize.py             # AI + NLP summarization engine
│   ├── io.py                    # File loader (PDF, TXT, images)
│   ├── ocr_reader.py            # Tesseract OCR pipeline
│   ├── export_pdf.py            # PDF export utility
│   └── __init__.py
├── apps/
│   └── streamlit_app/
│       └── app.py               # Streamlit web interface
├── config.py                    # Centralized configuration
├── output/                      # Generated files (gitignored)
├── requirements.txt
├── packages.txt                 # System packages (tesseract)
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/SumitSenapati/EduGenie-AI-Study-Buddy.git
cd EduGenie-AI-Study-Buddy
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

| OS | Command |
|---|---|
| Windows | Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH |
| macOS | `brew install tesseract` |
| Linux | `sudo apt install tesseract-ocr` |

### 5. Run the app

```bash
streamlit run apps/streamlit_app/app.py
```

---

## ⚙️ Processing Modes

| Mode | Internet | Privacy | Best For |
|---|---|---|---|
| 🔒 Offline (NLP) | Not required | Fully private | Basic summarization, any subject with known keywords |
| 🌐 Online (Groq AI) | Required | API-based | Any subject, smarter answers, better flashcards |

### Getting a Free Groq API Key

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign up with your email (no credit card needed)
3. Navigate to **API Keys** → **Create API Key**
4. Copy your key and paste it in the app's **"Enter Your AI Assistant Key"** field
5. Select **Online (Requires API Key)** mode and process your document

---

## 🧠 How It Works

```
Upload File (PDF / TXT / PNG / JPG)
        ↓
  OCR if image/scanned PDF (Tesseract)
        ↓
  Text Extraction (PyMuPDF)
        ↓
  ┌─────────────────────────────┐
  │  Online Mode (Groq LLM)     │  → Llama 3 understands ANY subject
  │  Offline Mode (NLP Engine)  │  → Frequency + scoring + definitions
  └─────────────────────────────┘
        ↓
  Summary  |  Keywords  |  Quiz  |  Flashcards
        ↓
  Display in Streamlit UI  +  Export as PDF
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI (Online) | Groq API — Llama 3 (8B) |
| NLP (Offline) | Custom Python NLP engine |
| OCR | Tesseract via pytesseract |
| PDF Reading | PyMuPDF (fitz) |
| PDF Export | FPDF / ReportLab |
| Language | Python 3.10+ |

---

## 📄 Core API Reference

```python
# Summarize text (offline or online)
from core.summarize import summarize_text

result = summarize_text(
    text       = "your notes here",
    min_length = 30,
    max_length = 150,
    config     = {"mode": "online", "api_key": "your_groq_key"}
)
# result = { "summary": ..., "keywords": [...], "quiz": [...], "flashcards": [...] }

# Load and process any file
from core.io import process_file

result = process_file(
    file_path  = "notes.pdf",
    mode       = "online",
    api_key    = "your_groq_key",
    min_length = 30,
    max_length = 150
)

# OCR from image
from core.ocr_reader import extract_text_from_image
text = extract_text_from_image("classroom_photo.jpg", lang="auto")

# Export summary to PDF
from core.export_pdf import export_summary_to_pdf
pdf_path = export_summary_to_pdf(summary_text)
```

---

## 🗂️ Supported File Types

| Format | Method |
|---|---|
| `.pdf` | Text layer extraction → OCR fallback |
| `.txt` / `.md` | Direct read |
| `.png` / `.jpg` / `.jpeg` | Tesseract OCR |

---

## 🔒 Privacy

- **Offline mode** never sends your data anywhere. Everything runs locally on your machine.
- **Online mode** sends only the text content of your notes to the Groq API for processing. No files are stored.

---

## 👨‍💻 Author

**Sumit Senapati**  
Built as an AI-powered educational project using NLP, OCR, and Groq LLM.

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>🧠 EduGenie — Making studying smarter, one note at a time.</sub>
</div>
