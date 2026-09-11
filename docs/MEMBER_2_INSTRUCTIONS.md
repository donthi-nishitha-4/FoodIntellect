# Member 2 — AI Engine, RAG & AI Helpers Instructions

> **Subsystem Ownership:** `ai_engine/`  
> **Git Branch:** `member-2-ai`  
> **Target Output:** `LLMOCRCleaner`, `AnalysisResponse` synthesis, and RAG search helpers.

---

## 1. Workload Description & Responsibilities

1. **LLM OCR Text Structuring (`ai_engine/extraction/ocr_cleaner.py`)**:
   - Implement `LLMOCRCleaner` conforming to `OCRCleanerProtocol`.
   - Convert raw unformatted OCR string blobs into structured `ProductData` JSON using Pydantic schema enforcement.

2. **Embeddings & PostgreSQL Hybrid Search (`ai_engine/embeddings/vector_store.py`)**:
   - Implement `VectorStore` connecting to PostgreSQL `pgvector` on port `5445`.
   - Combine dense cosine distance and sparse trigram `pg_trgm` search using Reciprocal Rank Fusion (RRF):
     $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

3. **Multi-Provider LLM Failover & RAG Pipeline (`ai_engine/rag_pipeline.py`)**:
   - Utilize `src/core/llm.py` failover wrapper (Gemini 3.6 Flash → Groq Llama 3.3 → OpenRouter).
   - Synthesize evidence context into `AnalysisResponse` summary, health scores (0-100), and key takeaways.

4. **RAG Analysis Helper & Evaluation (`ai_engine/routes_analyze_helper.py`, `evaluator.py`)**:
   - Provide clean helper routine for Member 3's FastAPI gateway.
   - Run RAGAS metrics (Faithfulness, Answer Correctness, Context Recall).

---

## 2. Shared Contract Rules

- **Do NOT modify `schemas/contracts.py` directly without team PR review.**
- Produce valid `AnalysisResponse` models.
- Develop using raw OCR text fixtures and `data/sample_products.json` so you do not depend on OpenCV/Tesseract hardware installation.

---

## 3. Daily Execution Command

```bash
# Run Member 2 test suite
PYTHONPATH=. pytest tests/test_ai_engine.py
```
