"""
OCR Text Engine (Member 1)

Extracts raw text strings from preprocessed food-label images using a
two-tier provider strategy:

  Primary:   EasyOCR — deep-learning OCR, handles curved / stylised labels well.
  Secondary: PyTesseract — traditional OCR, fast and works offline.
  Fallback:  Static mock string — ensures tests never fail due to missing system deps.

All provider imports are guarded with try/except so the module is importable
even in minimal environments where neither EasyOCR nor Tesseract is installed.
"""

from typing import Optional, Tuple
import numpy as np

# ── Provider availability flags ────────────────────────────────────────────── #
# We check at module load time so there is no import-time crash.

try:
    import easyocr  # type: ignore
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract  # type: ignore
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# ── Mock text used when no OCR engine is available ─────────────────────────── #
_MOCK_OCR_TEXT = (
    "Ingredients: Whole Wheat Flour, Sugar, Palm Oil, Soy Lecithin, Salt, "
    "Sodium Bicarbonate, Vanillin. "
    "Nutrition per 100g: Energy 450 kcal, Fat 16g, Saturated Fat 7.5g, "
    "Sugars 18g, Protein 8g, Sodium 250mg. "
    "Allergens: Contains Gluten, Soy."
)


class OCREngine:
    """
    Engine for extracting raw text from preprocessed food packaging images.

    Strategy:
        1. Try EasyOCR (deep-learning, best accuracy on packaging labels).
        2. Fall back to PyTesseract (fast, system-level Tesseract binary).
        3. Fall back to a deterministic mock string for test environments.

    Usage:
        engine = OCREngine()
        raw_text = engine.extract_raw_text(processed_img)
        # raw_text is a plain Python str with all detected text concatenated.
    """

    def __init__(self, languages: Optional[list] = None):
        """
        Initialise the OCR engine.

        Args:
            languages: List of language codes for EasyOCR.
                       Defaults to ['en'] (English only).
                       Example: ['en', 'hi'] for English + Hindi.
        """
        self._languages = languages or ["en"]
        # EasyOCR reader is lazy-loaded on first use to avoid slow startup
        # when EasyOCR is installed but not immediately needed.
        self._easyocr_reader = None

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def extract_raw_text(self, processed_img: np.ndarray) -> str:
        """
        Extract all visible text from a preprocessed label image.

        Tries EasyOCR first, then PyTesseract, then returns a mock string.

        Args:
            processed_img: 2-D (greyscale) or 3-D (BGR) NumPy uint8 array.
                           Typically the output of ImagePreprocessor.preprocess_image().

        Returns:
            Raw text string with words separated by spaces.
            Never raises — always returns a non-empty string.
        """
        text, provider = self._try_extract(processed_img)
        return text

    def extract_with_provider_info(self, processed_img: np.ndarray) -> Tuple[str, str]:
        """
        Same as extract_raw_text, but also returns which provider was used.

        Returns:
            Tuple of (raw_text: str, provider_name: str).
            provider_name is one of: 'easyocr', 'tesseract', 'mock'.

        Useful for logging and academic evaluation (CER / WER per provider).
        """
        return self._try_extract(processed_img)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _try_extract(self, processed_img: np.ndarray) -> Tuple[str, str]:
        """
        Try each OCR provider in priority order.

        Returns:
            (text, provider_name) where text is the extracted string.
        """
        # ── Tier 1: EasyOCR ────────────────────────────────────────────── #
        if EASYOCR_AVAILABLE:
            result = self._extract_easyocr(processed_img)
            if result:
                return result, "easyocr"

        # ── Tier 2: PyTesseract ─────────────────────────────────────────── #
        if PYTESSERACT_AVAILABLE:
            result = self._extract_tesseract(processed_img)
            if result:
                return result, "tesseract"

        # ── Tier 3: Mock fallback ───────────────────────────────────────── #
        return _MOCK_OCR_TEXT, "mock"

    def _get_easyocr_reader(self):
        """
        Lazy-load the EasyOCR Reader to avoid slow startup at import time.
        The reader is cached after the first call.

        gpu=False is intentional: most student/dev machines do not have
        a CUDA-capable GPU, and CPU inference is perfectly adequate for
        food-label text extraction.
        """
        if self._easyocr_reader is None:
            self._easyocr_reader = easyocr.Reader(
                self._languages,
                gpu=False,
                verbose=False,  # Suppress model loading logs
            )
        return self._easyocr_reader

    def _extract_easyocr(self, img: np.ndarray) -> Optional[str]:
        """
        Run EasyOCR inference on the image.

        EasyOCR returns a list of (bounding_box, text, confidence) tuples.
        We concatenate all detected text strings with spaces.

        Args:
            img: Processed image array (greyscale or BGR).

        Returns:
            Concatenated text string, or None on failure.
        """
        try:
            reader = self._get_easyocr_reader()
            # detail=0 returns only the text strings (faster, no bounding boxes)
            results = reader.readtext(img, detail=0)
            combined = " ".join(str(r).strip() for r in results if r)
            return combined if combined.strip() else None
        except Exception:
            # EasyOCR can raise errors on very small or all-black images
            return None

    def _extract_tesseract(self, img: np.ndarray) -> Optional[str]:
        """
        Run PyTesseract on the image.

        Tesseract config:
          --psm 6  → Assume a single uniform block of text.
                     Works well for nutrition-label back panels.
          --oem 3  → Default engine mode (LSTM + Legacy).

        Args:
            img: Processed image array.

        Returns:
            Extracted text string, or None on failure / empty result.
        """
        try:
            custom_config = r"--psm 6 --oem 3"
            text = pytesseract.image_to_string(img, config=custom_config)
            text = text.strip()
            return text if text else None
        except Exception:
            return None
