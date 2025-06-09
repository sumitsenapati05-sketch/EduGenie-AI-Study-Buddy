import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image

def extract_text_from_image(image_path, lang="eng"):
    return pytesseract.image_to_string(Image.open(image_path), lang=lang)
