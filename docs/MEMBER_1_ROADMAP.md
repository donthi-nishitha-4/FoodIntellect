# Member 1 — Individual MVP Roadmap

> **Domain:** Data Ingestion, OCR Pipeline, Knowledge Base & Healthier Alternative Recommender  
> **Workload Share:** 33%  
> **Git Branch:** `member-1-ingestion`  
> **Primary Output:** `ProductData` models, ingredient normalization, and nutrient alternative ranking.

---

## 🎯 Strategic Objective
Build a robust, reliable data acquisition pipeline that seamlessly converts barcode inputs and packaging label photos into structured `ProductData`, normalizes ingredients using a curated Knowledge Base, and ranks healthier food alternatives.

---

## 🗓️ Phase-by-Phase Execution Plan

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Sprint 1: OFF Barcode Client & Seed Knowledge Base          │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 2: OpenCV Preprocessing & Raw Text OCR Engine        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 3: Ingredient Matcher & Healthier Recommender Engine  │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 4: System Integration, Performance & Evaluation      │
 └─────────────────────────────────────────────────────────────┘
```

---

### Phase 1 (Sprint 1, Days 1–3): Open Food Facts Client & Seed KB
- [x] Set up `ingestion/openfoodfacts/client.py` using `urllib.request`.
- [x] Map Open Food Facts JSON response fields (`nutriments`, `ingredients_text_en`, `allergens_tags`) to `schemas/contracts.py` Pydantic `ProductData`.
- [x] Create initial `knowledge_base/ingredients_seed.json` with 20–50 common food additives, preservatives, sweeteners, and allergens.
- **Acceptance Criteria:** `pytest tests/test_ingestion.py` passes for barcode lookup `3017620422003` (Nutella).

---

### Phase 2 (Sprint 2, Days 4–7): OpenCV Image Preprocessing & OCR Engine
- [ ] Build `ingestion/ocr/preprocessor.py` using OpenCV:
  - Grayscale conversion (`cv2.COLOR_BGR2GRAY`).
  - Adaptive thresholding (`cv2.adaptiveThreshold`).
  - Noise reduction and deskewing for curved/shiny packaged labels.
- [ ] Build `ingestion/ocr/engine.py` wrapping EasyOCR / PaddleOCR (PyTesseract fallback).
- [ ] Connect `ingestion/pipeline.py` using `OCRCleanerProtocol` and `MockOCRCleaner`.
- **Acceptance Criteria:** Successfully extracts raw ingredient text from 10 sample packaged label photos.

---

### Phase 3 (Sprint 3, Days 8–10): Fuzzy Ingredient Matcher & Healthier Recommender
- [ ] Implement `knowledge_base/matcher.py` using `rapidfuzz` string ratio matching against `ingredients_seed.json`.
- [ ] Build `ingestion/recommender.py`:
  - Filter candidate products in the same category.
  - Exclude candidates matching user profile allergens ($A \cap B = \emptyset$).
  - Rank alternatives by sugar and saturated fat delta percentage (`nutrient_improvements`).
- **Acceptance Criteria:** `RecommenderEngine` successfully ranks low-sugar alternative candidates when given high-sugar input products.

---

### Phase 4 (Sprint 4, Days 11–14): Academic Evaluation & Integration
- [ ] Collect 30 packaged label image samples for quantitative OCR evaluation.
- [ ] Calculate Character Error Rate (CER) and Word Error Rate (WER) metrics.
- [ ] Conduct end-to-end integration testing with Member 3's FastAPI gateway.
- **Deliverables for Project Presentation:** OCR Accuracy Tables (CER/WER), Ingredient Normalization F1-score report, and Recommender ranking demonstration.

---

## 🛠️ Key File Ownership
- `ingestion/openfoodfacts/client.py`
- `ingestion/ocr/preprocessor.py`
- `ingestion/ocr/engine.py`
- `ingestion/recommender.py`
- `ingestion/pipeline.py`
- `knowledge_base/ingredients_seed.json`
- `knowledge_base/matcher.py`
- `tests/test_ingestion.py`
