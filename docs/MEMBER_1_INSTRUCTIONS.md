# Member 1 — Data, Ingestion & Recommender Instructions

> **Subsystem Ownership:** `ingestion/`, `knowledge_base/`  
> **Git Branch:** `member-1-ingestion`  
> **Target Output:** `ProductData` models and nutrient alternative recommendations.

---

## 1. Workload Description & Responsibilities

1. **Open Food Facts API (`ingestion/openfoodfacts/client.py`)**:
   - Fetch product metadata by EAN/UPC barcode string.
   - Parse ingredients list, nutrition facts (energy, fat, sugars, sodium, protein, fiber), allergens, and category tags.

2. **OCR Package Preprocessing & Extraction (`ingestion/ocr/`)**:
   - OpenCV image preprocessing (`preprocessor.py`): Grayscale conversion, adaptive Gaussian thresholding, deskewing.
   - OCR Text Extraction (`engine.py`): EasyOCR / PaddleOCR text string extraction (PyTesseract fallback).

3. **Ingredient Knowledge Base (`knowledge_base/`)**:
   - Maintain `ingredients_seed.json` (curated seed list of food ingredients, functional additive roles, safety flags, and aliases).
   - Implement `matcher.py` using `rapidfuzz` string matching to normalize raw scanned ingredient strings.

4. **Healthier Alternative Recommender (`ingestion/recommender.py`)**:
   - Filter candidate food products in the same category.
   - Exclude products matching user's allergen profile ($A \cap B = \emptyset$).
   - Rank alternatives with lower sugar and saturated fat deltas.

---

## 2. Shared Contract Rules

- **Do NOT modify `schemas/contracts.py` directly without team PR review.**
- Consume and return `ProductData` and `RecommendationItem` Pydantic models.
- Depend strictly on `OCRCleanerProtocol` in `ingestion/pipeline.py`. Use `MockOCRCleaner` for unit testing so you are never blocked by Member 2.

---

## 3. Daily Execution Command

```bash
# Run Member 1 test suite
PYTHONPATH=. pytest tests/test_ingestion.py
```
