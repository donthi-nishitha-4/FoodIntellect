# Member 2 — Individual MVP Roadmap

> **Domain:** LLM OCR Structuring, PostgreSQL Hybrid Search, RAG Pipeline & AI Analysis Helpers  
> **Workload Share:** 33%  
> **Git Branch:** `member-2-ai`  
> **Primary Output:** `LLMOCRCleaner`, `AnalysisResponse` RAG synthesis, and RAGAS evaluation suite.

---

## 🎯 Strategic Objective
Build a high-performance, resilient AI engine that parses raw OCR text into valid Pydantic models using LLM structured output, retrieves relevant ingredient evidence using PostgreSQL `pgvector` RRF hybrid search, and synthesizes grounded, failover-protected `AnalysisResponse` summaries.

---

## 🗓️ Phase-by-Phase Execution Plan

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Sprint 1: LLM Failover & LLM OCR Structuring Cleaner        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 2: PostgreSQL pgvector + pg_trgm Hybrid RRF Search   │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 3: RAG Pipeline Synthesis & FastAPI Helper Routine   │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 4: RAGAS Quantitative Evaluation Suite & Tuning      │
 └─────────────────────────────────────────────────────────────┘
```

---

### Phase 1 (Sprint 1, Sept 14, 2026): LLM Failover & OCR Text Structuring
- [x] Integrate multi-provider LLM failover wrapper (`src/core/llm.py`: Gemini 3.6 Flash → Groq Llama-3.3 → OpenRouter).
- [x] Build `ai_engine/extraction/ocr_cleaner.py` implementing `OCRCleanerProtocol`.
- [x] Enforce strict JSON output parsing to extract structured `ProductData` from noisy OCR string blobs.
- **Acceptance Criteria:** `LLMOCRCleaner` successfully converts messy OCR text into valid `ProductData` instance without throwing JSON parsing exceptions.

---

### Phase 2 (Sprint 2, Sept 21, 2026): PostgreSQL pgvector + pg_trgm Hybrid RRF Search
- [x] Connect `ai_engine/embeddings/vector_store.py` to PostgreSQL container on port `5445`.
- [x] Implement Reciprocal Rank Fusion (RRF) combining dense cosine vector distance and sparse trigram keyword search:
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
- [x] Seed food corpus vector embeddings into `rag_documents` table using `sentence-transformers` (`all-MiniLM-L6-v2`).
- **Acceptance Criteria:** `VectorStore.hybrid_search("palm oil")` returns top 3 relevant evidence chunks within <150ms.

---

### Phase 3 (Sprint 3, Sept 27, 2026): Grounded RAG Synthesizer & FastAPI Route Helpers
- [x] Create system and human prompts in `ai_engine/prompts/` (`ingredient_analysis.py`, `product_summary.py`).
- [x] Build `ai_engine/rag_pipeline.py`: Synthesize `ProductData` + retrieved evidence context into complete `AnalysisResponse` object (summary, health score 0–100, key takeaways).
- [x] Build `ai_engine/routes_analyze_helper.py`: Export clean helper function `execute_full_analysis(...)` for Member 3's gateway.
- **Acceptance Criteria:** `pytest tests/test_ai_engine.py` passes end-to-end with valid `AnalysisResponse` output.

---

### Phase 4 (Sprint 4, Oct 02, 2026): RAGAS Quantitative Evaluation Suite
- [x] Build `ai_engine/evaluator.py` running RAGAS & CER/WER metrics:
  - **Faithfulness**: Verifies zero hallucination relative to retrieved context.
  - **Answer Correctness & Relevance**: Measures quality of health recommendations.
- [x] Conduct LLM failover load test (simulating Gemini rate limits to verify seamless Groq failover).
- **Deliverables for Project Presentation:** RAGAS Evaluation Scorecards, Vector Retrieval Latency Benchmarks, and Failover Resilience Log Demos.

---
### PHASE 5: collaboration tasks Member 2 can provide to assist Member 1 and Member 3
#### How Member 2 Can Assist Member 1 (Data & Ingestion Lead)
- **Unstructured Text Standardization Helper**

- Provide a batch routine using LLMOCRCleaner to convert raw OpenFoodFacts unstructured text fields (like ingredients_text string blobs) into standardized IngredientInfo objects for Member 1’s database.
- **AI Semantic Tagging & Safety Categorization**

- Provide an LLM helper function (ai_engine/extraction/ingredient_tagger.py) to automatically classify un-categorized ingredients into categories (Emulsifier, Preservative, Sweetener, Artificial Color) and assign safety flags (Safe, Caution, High Sugar).
- **Corpus Embedding Maintenance Script**

- Keep scripts/ingest_food_corpus.py updated so whenever Member 1 adds new raw food knowledge files into data/food_corpus/, they can be embedded into PostgreSQL rag_documents with one command.

#### How Member 2 Can Assist Member 3 (FastAPI Gateway & Frontend Lead)
-**Ready-to-Mount FastAPI APIRouter (app/routers/analyze.py)**
- Create a pre-configured FastAPI APIRouter module for /api/v1/analyze and /api/v1/ocr/clean with complete request validation and error handling, allowing Member 3 to mount it in main.py with zero boilerplate.
- **LLM Provider Health & Failover Status Check Helper**

- Build a lightweight health monitoring helper (check_llm_providers_status()) checking Gemini, Groq, and OpenRouter availability. Member 3 can expose this on /api/v1/health/llm to display active provider badges on the UI dashboard.
- **Streaming AI Response Generator (Server-Sent Events)**

- Provide a streaming synthesizer helper (stream_analysis_response(...)) so Member 3 can implement typewriter-style streaming summaries on the React/Web UI.
- **Frontend Mock Fixtures**
- Provide deterministic mock factory functions (get_sample_analysis_response()) so Member 3 can construct and style UI cards and charts without needing backend database services running.

## 🛠️ Key File Ownership
- `ai_engine/extraction/ocr_cleaner.py`
- `ai_engine/embeddings/vector_store.py`
- `ai_engine/prompts/ingredient_analysis.py`
- `ai_engine/prompts/product_summary.py`
- `ai_engine/rag_pipeline.py`
- `ai_engine/routes_analyze_helper.py`
- `ai_engine/evaluator.py`
- `src/core/llm.py`
- `tests/test_ai_engine.py`
