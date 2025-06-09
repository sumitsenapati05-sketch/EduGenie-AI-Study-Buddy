**StudySage 🧠 – Offline AI Note Assistant**

```

░██████╗████████╗██╗░░░██╗██████╗░██╗░░░██╗  ░██████╗░█████╗░░██████╗░███████╗
██╔════╝╚══██╔══╝██║░░░██║██╔══██╗╚██╗░██╔╝  ██╔════╝██╔══██╗██╔════╝░██╔════╝
╚█████╗░░░░██║░░░██║░░░██║██║░░██║░╚████╔╝░  ╚█████╗░███████║██║░░██╗░█████╗░░
░╚═══██╗░░░██║░░░██║░░░██║██║░░██║░░╚██╔╝░░  ░╚═══██╗██╔══██║██║░░╚██╗██╔══╝░░
██████╔╝░░░██║░░░╚██████╔╝██████╔╝░░░██║░░░  ██████╔╝██║░░██║╚██████╔╝███████╗
╚═════╝░░░░╚═╝░░░░╚═════╝░╚═════╝░░░░╚═╝░░░  ╚═════╝░╚═╝░░╚═╝░╚═════╝░╚══════╝
             StudySage – Offline AI Note Assistant by Sahaj33
```

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
\[![Offline AI](https://img.shields.io/badge/Offline%20AI-Yes-green)]
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen)](LICENSE)

---

## 📖 Overview

**StudySage** is a versatile, offline AI-powered note assistant tailored for students. Whether you have text files, markdown notes, or images of handwritten pages, StudySage helps you:

* **Summarize** long lecture notes into concise overviews
* **Generate** quiz questions to test your comprehension
* **Extract** text from images via OCR (handwritten or printed)
* **Export** summaries to PDF or text files
* **Use** through both a sleek CLI or a modern desktop GUI
* **BIG THANKS TO HUGGINGFACE MODEL CREATOR: [sshleifer/distilbart-cnn-12-6](https://huggingface.co/sshleifer/distilbart-cnn-12-6)**

All processing runs locally—no internet required once dependencies are installed.

---

## ⚙️ Features

| Feature                       | Description                                          | Trigger                                 |
| ----------------------------- | ---------------------------------------------------- | --------------------------------------- |
| 📝 Text Summarizer            | Summarize `.txt`/`.md` notes via offline LLM         | CLI: `1` / GUI: **Generate Summary**    |
| 🧪 Quiz Generator             | Create MCQs (3–5) from summaries                     | CLI: `2` / GUI: *(Coming in next GUI)*  |
| 🖼 OCR from Image             | Extract text from `.png`, `.jpg`, `.jpeg`            | CLI: `4` / GUI: **OCR (Image to Text)** |
| 📄 PDF Export                 | Save summary as formatted PDF                        | CLI: `3` / GUI: **Export as PDF**       |
| 💾 Save to Text File          | Save any displayed text to `.txt`                    | CLI: prompt / GUI: **Save as .txt**     |
| 🎛️ Modular Feature Selection | Combine any features (`1,2,3,4`) in one run          | CLI menu selection                      |
| 🎨 Modern CLI Design          | Colorful banners & menus via `pyfiglet` + `colorama` | CLI launcher                            |
| 🖥️ Desktop GUI               | GUI with `customtkinter` for file picker & buttons   | Run `main.exe` or `python main.py` GUI  |

---

## 📂 Project Structure

```bash
StudySage/
├── core/                   # Backend logic modules
│   ├── __init__.py
│   ├── summarize.py        # Summarization logic
│   ├── quiz_gen.py         # Quiz generation logic
│   ├── ocr_reader.py       # OCR extraction logic
│   └── export_pdf.py       # PDF export logic
├── assets/                 # Optional: icons, banners
│   └── banner.png          # GUI banner image
├── output/                 # Generated outputs (.txt/.pdf)
├── gui.py                  # CustomTkinter GUI implementation
├── main.py                 # CLI & GUI entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project overview (this file)
└── .gitignore              # Excluded files/folders
```

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Sahaj33-op/StudySage.git
   cd StudySage
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Tesseract (for OCR)**

   * Download and install Tesseract OCR engine: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   * Ensure `tesseract.exe` is in your PATH or configure `pytesseract.pytesseract.tesseract_cmd` in `core/ocr_reader.py`

---

## 🚀 Usage

### 🖥️ CLI Mode

Run the CLI interface:

```bash
python main.py
```

Follow prompts to:

1. Enter file path (.txt/.md/.png/.jpg)
2. (For images) Choose OCR language
3. Select features:

   * `1` Summarize
   * `2` Generate Quiz
   * `3` Export PDF
   * `4` OCR only
   * Combinations like `1,2,3`
4. Save outputs when prompted

### 🎨 GUI Mode

Run the GUI:

```bash
python gui.py
```

* Click **Choose File** to load notes or images
* Use buttons:

  * **Generate Summary**
  * **OCR (Image to Text)**
  * **Export as PDF**
  * **Save as .txt**

---

## 🛠️ Packaging as `.exe`

Once tested, build your Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Your `.exe` will appear in `dist/`.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to:

* Fork the repo
* Create a new branch: `git checkout -b feature-name`
* Commit your changes: `git commit -m 'Add new feature'`
* Push to the branch: `git push origin feature-name`
* Open a Pull Request

Please ensure code follows PEP8 and includes docstrings.

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

*Crafted with ❤️ by Sahaj33*
