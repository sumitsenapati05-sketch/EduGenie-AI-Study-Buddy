import os
from transformers import pipeline
from pathlib import Path
from quiz_gen import generate_questions
from export_pdf import export_summary_to_pdf
from ocr_reader import extract_text_from_image
from pyfiglet import figlet_format
from colorama import Fore, Style, init
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

init(autoreset=True)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    clear_screen()
    banner = figlet_format("StudySage")
    print(Fore.CYAN + banner)
    print(Fore.YELLOW + "🧠 Welcome to " + Fore.CYAN + "StudySage" + Fore.YELLOW + " – Offline AI Note Assistant " + Fore.CYAN + "by Sahaj33\n")


def load_text_from_file(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("File not found.")
    return path.read_text(encoding='utf-8')


def summarize_text(text, min_len, max_len):
    print(Fore.BLUE + "[+] Loading summarization model (offline)...")
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = summarizer(text, max_length=200, min_length=30, do_sample=False)
    return summary[0]['summary_text']


def run_features(choice, text, min_len, max_len):
    summary = None

    if '1' in choice:
        summary = summarize_text(text, min_len, max_len)
        print(Fore.YELLOW + "\n📄 Summary:\n")
        print(summary)

    if '2' in choice:
        if summary is None:
            summary = summarize_text(text)
        questions = generate_questions(summary)
        print(Fore.CYAN + "\n🧪 Generated Questions:\n")
        for q in questions:
            print(q["question"])
            print(f"(Answer: {q['answer']})\n")

    if '3' in choice:
        if summary is None:
            summary = summarize_text(text)
        export_summary_to_pdf(summary)


def main():
    while True:
        print_banner()

        print(Fore.CYAN + "\n📝 Customize Summary Length:")
        word_range = input("Enter min,max (or press Enter for default [30,200]) or type 0 to exit: ").strip()

        if word_range == '0':
            print(Fore.YELLOW + "👋 Exiting StudySage. See you again!\n")
            return

        try:
            min_len, max_len = map(int, word_range.split(','))
        except:
            min_len, max_len = 30, 200

        file_path = input(Fore.BLUE + "📂 Enter the path to your note file (.txt, .md, .pdf or .png/.jpg): ").strip()
        file_path = file_path.strip('"')  # Just in case path has quotes
        ext = Path(file_path).suffix.lower()

        text = ""

        try:
            if ext in [".png", ".jpg", ".jpeg"]:
                print(Fore.CYAN + "\n🌐 Available OCR languages: https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html")
                print(Fore.CYAN + "\n🌐 NOTE: Send better quality image for better results.")
                ocr_lang = input(Fore.BLUE + "🌐 Enter OCR language code (default is 'eng'): ").strip().lower() or 'eng'

                text = extract_text_from_image(file_path, lang=ocr_lang)
                if not text:
                    print(Fore.RED + "\n❌ OCR failed or unreadable. Try a clearer scan or check language.\n")
                    input("✅ Press Enter to return to the main menu...")
                    continue
                print(Fore.YELLOW + "\n🖼 Extracted Text from Image:\n")
                print(text)

                save = input(Fore.CYAN + "\n💾 Save OCR result to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = OUTPUT_DIR / f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    filename.write_text(text, encoding="utf-8")
                    print(Fore.GREEN + f"✅ Saved to {filename}")

            elif ext in [".txt", ".md"]:
                text = load_text_from_file(file_path)
            else:
                raise ValueError("Unsupported file type. Use .txt, .md, .png, .jpg, etc.")

        except Exception as e:
            print(Fore.RED + f"❌ Error: {e}")
            input("✅ Press Enter to return to the main menu...")
            continue

        print(Fore.GREEN + "\n🔧 Choose features to run:")
        print(Fore.MAGENTA + "  1" + Fore.WHITE + " - Generate Summary")
        print(Fore.MAGENTA + "  2" + Fore.WHITE + " - Generate Quiz Questions")
        print(Fore.MAGENTA + "  3" + Fore.WHITE + " - Export Summary as PDF")
        print(Fore.MAGENTA + "  1,2,3..." + Fore.WHITE + " - Combine multiple features")
        print(Fore.RED + "  0 - Exit")

        choice = input(Fore.CYAN + "\nYour choice: ").strip()

        if choice == '0':
            print(Fore.YELLOW + "👋 Exiting StudySage. See you again!\n")
            break

        run_features(choice, text, min_len, max_len)
        input(Fore.GREEN + "✅ Press Enter to return to the main menu...")

if __name__ == "__main__":
    main()
