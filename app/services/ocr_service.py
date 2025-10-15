import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from app.config import settings
import os

class OCRService:
    def __init__(self):
        self.config = settings.TESSERACT_CONFIG
        self.languages = settings.OCR_LANGUAGES
    
    def extract_from_image(self, image_path: str) -> str:
        """Extract text from a single image"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(
                image,
                config=self.config,
                lang=self.languages
            )
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from scanned PDF using OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            # OCR each page
            all_text = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(
                    image,
                    config=self.config,
                    lang=self.languages
                )
                all_text.append(f"--- Page {i+1} ---\n{text}")
            
            return "\n\n".join(all_text)
        except Exception as e:
            raise Exception(f"PDF OCR failed: {str(e)}")
    
    def is_pdf_scanned(self, pdf_path: str) -> bool:
        """Check if PDF needs OCR (is scanned vs digital)"""
        import PyPDF2
        
        with open(pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            # Sample first few pages
            sample_pages = min(3, len(pdf.pages))
            
            for i in range(sample_pages):
                text = pdf.pages[i].extract_text()
                if len(text.strip()) > 100:  # Has decent amount of text
                    return False
            
            return True  # Likely scanned