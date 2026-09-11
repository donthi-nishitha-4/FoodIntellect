"""
OCR Text Engine (Member 1)

Extracts raw text string blobs from processed package photos.
"""
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
import numpy as np


class OCREngine:
    """Engine for extracting raw text from food packaging images."""

    def extract_raw_text(self, processed_img: np.ndarray) -> str:
        """Extract raw text string using PyTesseract with fallback handling."""
        if not PYTESSERACT_AVAILABLE:
            return "MOCK RAW OCR TEXT: Ingredients: Whole Wheat Flour, Sugar, Palm Oil, Soy Lecithin, Salt. Net Wt 200g."

        try:
            raw_text = pytesseract.image_to_string(processed_img)
            return raw_text.strip() if raw_text.strip() else "MOCK RAW OCR TEXT: Ingredients: Whole Wheat Flour, Sugar, Palm Oil, Soy Lecithin, Salt."
        except Exception as e:
            return f"MOCK RAW OCR TEXT: Ingredients: Whole Wheat Flour, Sugar, Palm Oil, Soy Lecithin, Salt. Error: {str(e)}"

