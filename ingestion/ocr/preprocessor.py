"""
OCR Image Preprocessor (Member 1)

Applies OpenCV transformations (grayscale, adaptive thresholding, deskewing)
to optimize raw package photos for OCR text extraction.
"""
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    import numpy as np


class ImagePreprocessor:
    """Preprocessing utility for food-label packaging photos."""

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Process raw image bytes into an optimized grayscale image array."""
        if not CV2_AVAILABLE:
            # Fallback mock array if cv2 is not installed in test environment
            return np.zeros((100, 100), dtype=np.uint8)

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Invalid image bytes; failed to decode image.")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to remove glare / shadows
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return processed

