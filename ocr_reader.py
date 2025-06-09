from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path, lang='eng'):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang).strip()
        
        # Auto-detect bad scan
        if not text or len(text) < 20 or all(c in '!@#$%^&*()_+=-' for c in text[:10]):
            return None  # Bad scan or empty
        return text
    except Exception as e:
        return None