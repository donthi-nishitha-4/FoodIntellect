"""
Ingestion Pipeline Coordinator (Member 1)

Coordinates image preprocessing, raw text extraction, and clean text structuring
via the OCRCleanerProtocol interface.
"""
from typing import Optional
from schemas.contracts import ProductData, OCRCleanerProtocol, MockOCRCleaner
from ingestion.ocr.preprocessor import ImagePreprocessor
from ingestion.ocr.engine import OCREngine


class IngestionPipeline:
    """Pipeline coordinator for processing image packaging inputs."""

    def __init__(self, cleaner: Optional[OCRCleanerProtocol] = None):
        self.preprocessor = ImagePreprocessor()
        self.ocr_engine = OCREngine()
        # Default to MockOCRCleaner during development to prevent blocking on Member 2
        self.cleaner: OCRCleanerProtocol = cleaner or MockOCRCleaner()

    def process_image(self, image_bytes: bytes) -> ProductData:
        """Process image bytes and return structured ProductData."""
        processed_img = self.preprocessor.preprocess_image(image_bytes)
        raw_text = self.ocr_engine.extract_raw_text(processed_img)
        structured_data = self.cleaner.clean_text(raw_text)
        return structured_data
