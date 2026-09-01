# 🗺️ FoodIntellect MVP Roadmap

An enterprise-grade, multi-modal Food Intelligence system combining **Label OCR**, **Deterministic Allergy Matching**, **Hybrid RAG Knowledge Retrieval**, and **Nutritional Recommendation Engines**.

---

## 🎯 Architecture Overview

```text
               FOODINTELLECT MVP PIPELINE
                           │
                 ┌─────────┴─────────┐
                 ↓                   ↓
          Search Product        Upload Label
                 │                   │
                 │                  OCR (OpenCV + Tesseract)
                 │                   │
                 └─────────┬─────────┘
                           ↓
                  Structured Product Data
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
          Ingredients   Nutrition    Allergens
              │            │            │
              └────────────┼────────────┘
                           ↓
                  Food Knowledge Base
                           ↓
                    FOODINTELLECT RAG
              (pgvector + pg_trgm + RRF)
                           ↓
                  Food Explanation
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
          User Profile  Allergy Rule   Nutrition
                           Engine      Comparison
              │            │            │
              └────────────┼────────────┘
                           ↓
                  Alternative Ranking
                           ↓
                Grounded Recommendation
                           ↓
                      AI Chatbot
```

---

## 🗓️ 16-Phase Execution Roadmap

### Phase 0 — Standalone Repository Setup & Core Extraction
* **Goal**: Establish a clean repository, map reusable assets from AIPMS, and set up Docker environment.
* **Deliverable**: Independent `FoodIntellect` project directory with PostgreSQL `pgvector` container on port 5445.

### Phase 1 — Food Knowledge Base Corpus
* **Goal**: Build seed corpus of 50–100 food products and 100–200 ingredient/additive knowledge files.
* **Deliverable**: `data/food_corpus/` populated with structured text files covering emulsifiers, preservatives, sweeteners, and allergens.

### Phase 2 — Adapt Existing RAG Baseline
* **Goal**: Swap construction domain prompts with food domain prompts and ingest vector embeddings into PostgreSQL.
* **Deliverable**: `scripts/ingest_food_corpus.py` loading `all-MiniLM-L6-v2` dense vectors + `pg_trgm` sparse trigram index.

### Phase 3 — RAG Baseline Evaluation
* **Goal**: Benchmark retrieval relevance, context recall, and LLM answer correctness against 30–50 food Q&A benchmarks.
* **Deliverable**: Baseline evaluation metrics report for Review 1.

### Phase 4 — Product Database & Search API
* **Goal**: Build relational schema for `products` and `user_profiles` and implement search by product name/brand.
* **Deliverable**: FastAPI `/api/v1/search` endpoint returning product metadata, nutrition facts, and ingredient lists.

### Phase 5 — OCR Prototype (Computer Vision)
* **Goal**: Process label packaging photos using OpenCV preprocessing and Tesseract OCR.
* **Deliverable**: `src/ocr/` image pipeline (Resizing $\rightarrow$ Grayscale $\rightarrow$ Thresholding $\rightarrow$ Noise reduction $\rightarrow$ Text extraction).

### Phase 6 — OCR to Structured Information
* **Goal**: Parse raw OCR text into structured JSON representations of ingredients and nutrition facts.
* **Deliverable**: Automated parser extracting arrays of ingredients and key nutritional values (calories, sugar, fat, sodium).

### Phase 7 — Ingredient Name Normalization
* **Goal**: Map messy OCR terms (e.g. *"Skimmed Milk Powder"*) to canonical knowledge base terms (*"milk"*).
* **Deliverable**: Normalization pipeline using string lowercasing, regex cleanup, alias maps, and fuzzy string matching (`rapidfuzz`).

### Phase 8 — Deterministic Allergy Engine
* **Goal**: Enforce non-LLM, rule-based allergen matching ($A \cap B \neq \emptyset$).
* **Deliverable**: `src/services/allergy_engine.py` producing deterministic allergen collision alerts.

### Phase 9 — User Profile Service
* **Goal**: Store dietary restrictions (Vegetarian, Vegan), allergies (Milk, Peanut, Soy), and nutritional preferences (Low Sugar).
* **Deliverable**: `user_profiles` database table and profile management endpoints.

### Phase 10 — Nutrition Comparison Engine
* **Goal**: Perform quantitative comparative analysis between analyzed product and candidate alternatives.
* **Deliverable**: Comparative delta calculation (e.g. Sugar: -8g, Sodium: -150mg).

### Phase 11 — Alternative Recommendation System
* **Goal**: Rank alternative candidate products in the same category based on allergy compliance and nutritional score.
* **Deliverable**: `src/services/recommender.py` content-based ranking engine.

### Phase 12 — RAG-Powered Recommendation Explanations
* **Goal**: Synthesize natural language justifications by feeding deterministic recommendation deltas into RAG prompts.
* **Deliverable**: Grounded explanations ("Product B recommended because it has 8g less sugar and contains no milk").

### Phase 13 — Context-Aware AI Chatbot
* **Goal**: Integrate LangGraph state machine to answer food ingredient questions, explain allergy alerts, and justify recommendations.
* **Deliverable**: Interactive `/api/v1/chat` endpoint.

### Phase 14 — React Frontend
* **Goal**: Build simple, modern web interface.
* **Deliverable**: React/Vite web UI with Home, Search/Upload, Analysis, Alternatives, and Chatbot pages.

### Phase 15 — System Evaluation
* **Goal**: Conduct comprehensive quantitative benchmarks across all modules.
* **Deliverable**: Evaluation report covering OCR CER/WER, Allergy Precision/Recall, and RAGAS RAG metrics.

### Phase 16 — Final Refinement & Review Prep
* **Goal**: Freeze MVP, fix edge cases, polish UI, and prepare final dissertation documentation.
* **Deliverable**: Production-ready MVP deployment and review presentation slides.

---

## 👥 Team Work Division

| Member | Focus Area | Core Responsibilities |
| :--- | :--- | :--- |
| **Member 1** | CV & Data Lead | Food Dataset, OpenCV Preprocessing, Tesseract OCR, Text Parsing, Ingredient Normalization. |
| **Member 2** | RAG & NLP Lead | RAG Ingestion Pipeline, Vector Database, LangGraph Agent, RAGAS Evals, Food Chatbot. |
| **Member 3** | Fullstack & Recommender | PostgreSQL Schemas, Deterministic Allergy Engine, Nutrition Comparison, Recommender, FastAPI & React. |
