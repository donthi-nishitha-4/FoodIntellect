# Implementation Plan - FoodIntellect Step 1: Standalone Project Creation & RAG Baseline

This updated plan creates a **clean, standalone repository/folder `FoodIntellect`** separate from `AIPMS`. We extract *only* the reusable, enterprise-grade RAG core components from the old codebase, leaving behind all construction-domain data, obsolete chunkers, and experiment logs.

## User Review Required

> [!IMPORTANT]
> **Why a Standalone Project (`FoodIntellect/`) is Superior**:
> 1. **Team Independence**: A separate repository allows all 3 members to create feature branches (`feature/ocr-pipeline`, `feature/food-rag`, `feature/allergy-recommender`) cleanly off `main` without git clutter or commit history pollution from the old project.
> 2. **Clean Footprint**: We copy *only* the ~10 reusable core files (FastAPI, pgvector connection, hybrid search, reranker, failover LLM, LangGraph agent) and exclude all construction PDFs, Excel files, and legacy scripts.

## Proposed Changes

### 1. New Project Workspace: `/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect`

```text
AIPMS/
├── NStructions/          <-- Original Construction RAG Project (Untouched)
└── FoodIntellect/        <-- NEW Clean Standalone Project for your Team
```

---

### 2. Selective Extraction Matrix (What gets copied to `FoodIntellect/`)

#### [NEW] Reusable RAG Core Files
* `src/core/database/connection.py` (PostgreSQL + pgvector connection, hybrid retrieval, vector indices)
* `src/core/llm.py` (Multi-provider LLM failover wrapper: Groq $\rightarrow$ OpenRouter $\rightarrow$ Cerebras $\rightarrow$ Gemini)
* `src/core/pipeline.py` (Embedding, Cross-Encoder reranking, vector/hybrid/HyDE search)
* `src/agents/` (LangGraph state machine & query routing)
* `src/api/` (FastAPI setup & routes)
* `src/utils/config.py` (Environment & settings management)
* `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `.env.example`, `.gitignore`

#### [EXCLUDED] Construction Domain Files (Not copied)
* `data/` (All metro/construction PDFs, contract texts, and Excel sheets)
* `src/chunkers/` (GCC contract chunkers & correspondence splitters)
* Legacy scripts (`scripts/test_contract_confusion.py`, `scripts/hyde_experiment.py`, etc.)

---

### 3. Food Knowledge Base & Seed Corpus

#### [NEW] [FoodIntellect/data/food_corpus/](file://wsl$/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/data/food_corpus/)
Create 25 structured food ingredient and additive text documents covering:
* **Emulsifiers & Stabilizers**: Lecithin, Soy Lecithin, Xanthan Gum, Guar Gum, Pectin, Carrageenan, Gelatin.
* **Preservatives & Acidulants**: Sodium Benzoate, Potassium Sorbate, Citric Acid, Ascorbic Acid.
* **Sweeteners & Carbohydrates**: High Fructose Corn Syrup, Maltodextrin, Stevia, Aspartame, Erythritol.
* **Proteins & Dairy**: Milk Powder, Whey Protein Concentrate.
* **Fats & Oils**: Palm Oil.
* **Flavor Enhancers & Colors**: Monosodium Glutamate (MSG), Caffeine, Curcumin, Tartrazine, Carmine, Titanium Dioxide.

---

### 4. Ingestion & Testing Subsystem

#### [NEW] `FoodIntellect/scripts/ingest_food_corpus.py`
- Reads food corpus files, chunks them, embeds via `all-MiniLM-L6-v2`, and loads them into PostgreSQL pgvector under `tenant_id="foodintellect"`.

#### [NEW] `FoodIntellect/scripts/test_food_query.py`
- Executes sample food queries against the hybrid search + cross-encoder reranker + multi-provider LLM pipeline and prints verification results.

---

## Verification Plan

### Automated Verification
1. Initialize database: `python scripts/reinit_db.py` inside `FoodIntellect/`.
2. Ingest food dataset: `python scripts/ingest_food_corpus.py`.
3. Test 5 sample queries: `python scripts/test_food_query.py`:
   - *"What is lecithin and why is it used in food?"*
   - *"Is milk powder a common allergen?"*
   - *"What is the function of sodium benzoate?"*
   - *"What is maltodextrin?"*
   - *"What are the health considerations of high fructose corn syrup?"*

### Manual Verification
- Verify that the `FoodIntellect/` repository directory is completely isolated, clean, and functioning independently of `NStructions`.
