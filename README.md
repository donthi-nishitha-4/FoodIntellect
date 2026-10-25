# 🥗 Food Intellect MVP

An AI-powered food intelligence platform combining OCR-based ingredient extraction, deterministic allergen safety checks, hybrid retrieval, and healthier-product recommendation.

This project is now merged into `main` and reflects the actual implementation history from the git log. The branch timeline shows Member 1, Member 2, and Member 3 work being integrated into the mainline project, with the final merge commit: `5273ae9` (`Merge member3 into main`).

### Current status
- Git evidence: `main` is merged with `member3`, and `origin/main` is current
- Validation evidence: `pytest -q` in the WSL venv passed with `59 passed, 13 warnings in 102.37s`
- Demo readiness: strong MVP for a functional technical demo; warnings are only deprecation warnings from `easyocr`/`torch`

---

## 🚀 Core Features

- Deterministic allergen detection using set-intersection logic on ingredient and allergy vocabularies
- OCR preprocessing and extraction pipeline for packaging text
- Hybrid document retrieval using vector + keyword search patterns
- AI-assisted product summarization and health analysis
- Healthier alternative ranking based on nutritional improvements and allergen exclusions
- App-layer API and UI integration for barcode and user profile interactions

---

## 👥 Member Status Snapshot

| Workstream | Owner | Domain | Git Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| Member 1 | Data & Ingestion | OCR, ingestion, matcher, recommender | `member1` branch merged into main | ✅ Implemented |
| Member 2 | AI & RAG | LLM cleaner, vector store, RAG pipeline, evaluator | `member-2-ai` merged into main | ✅ Implemented |
| Member 3 | App & Gateway | FastAPI app, allergy engine, DB/session, UI wrappers | `member3` merged into main | ✅ Implemented |

---

## ✅ Demo Readiness Checklist

- [x] Repo is on `main` and merged from all team branches
- [x] Core ingestion + OCR + AI + app layers are integrated
- [x] Project passes automated test suite in WSL virtualenv
- [x] Ingestion fallback logic handles corrupt image input safely
- [x] Dependency drift was fixed so the repo installs and runs correctly
- [x] Demo can focus on: barcode/label upload → OCR → analysis → allergen safety → recommendations

### Demo flow
1. Launch the app locally from the project root.
2. Upload a product label or scan a known barcode.
3. Show OCR extraction of ingredients.
4. Highlight allergen matching (`SAFE`, `WARNING`, `DANGER`).
5. Display AI summary and healthier alternatives.
6. Explain the architecture split between ingestion, AI, and app layers.

### Good demo narrative
- “This system converts raw packaging information into structured product insights.”
- “It combines deterministic rules with AI retrieval to improve safety and explainability.”
- “The solution is designed to be modular and team-parallelized, which is why each member owns a workflow.”

---

## 📄 Research Paper Direction

This project is also a good candidate for a research-style paper if you want to extend it beyond a demo.

Possible paper angles:
- Ingredient-aware food safety and allergen detection using hybrid symbolic + retrieval-based reasoning
- Explainable recommendation pipelines for healthier food substitutions
- OCR-to-knowledge extraction for packaged food products
- Hybrid search for domain-specific food knowledge retrieval

A strong paper structure would be:
1. Problem statement
2. Related work
3. Methodology
4. System architecture
5. Evaluation metrics
6. Results
7. Limitations and future work

---

## 🏗️ Repository Directory Layout

```text
food-intellect/
│
├── schemas/                       🔒 SHARED CONTRACT (All Members)
│   ├── __init__.py
│   └── contracts.py               # Pydantic v2 ProductData, AnalysisResponse, Protocols
│
├── ingestion/                     👤 MEMBER 1 (Data, Ingestion & Recommender)
│   ├── openfoodfacts/             # Open Food Facts API client
│   ├── ocr/                       # OpenCV preprocessor & EasyOCR/Tesseract engine
│   ├── recommender.py             # Nutrient alternative product ranker
│   └── pipeline.py                # Ingestion coordinator using OCRCleanerProtocol
│
├── knowledge_base/                👤 MEMBER 1 (Ingredient KB)
│   ├── ingredients_seed.json      # Seed dictionary of food ingredients & additives
│   └── matcher.py                 # Rapidfuzz ingredient matcher
│
├── ai_engine/                     👤 MEMBER 2 (AI, RAG & AI Helpers)
│   ├── embeddings/                # PostgreSQL pgvector + pg_trgm RRF search
│   ├── extraction/                # LLM OCRCleaner converting raw text -> ProductData
│   ├── prompts/                   # RAG analysis & summary prompt templates
│   ├── rag_pipeline.py            # RAG evidence synthesizer
│   ├── routes_analyze_helper.py   # RAG analysis helper routine for FastAPI
│   └── evaluator.py               # RAGAS metrics calculator
│
├── app/                           👤 MEMBER 3 (App Gateway & Frontend)
│   ├── api/                       # FastAPI routes (ingest, analyze, user)
│   ├── core/                      # Deterministic rule-based allergy_engine.py
│   ├── db/                        # SQLAlchemy DB models & connection (Port 5445)
│   └── main.py                    # FastAPI main entry point
│
├── frontend/                      👤 MEMBER 3 (UI)
│   ├── src/                       # Vite + React UI components
│   ├── package.json
│   └── vite.config.js
│
├── data/                          🔒 MOCK DATASETS & CORPUS
│   ├── sample_products.json       # Mock ProductData fixtures
│   ├── mock_analysis.json         # Mock AnalysisResponse fixtures
│   └── food_corpus/               # Food ingredient knowledge articles
│
├── docs/                          📚 TEAM DOCUMENTATION & ROADMAPS
│   ├── MEMBER_1_INSTRUCTIONS.md   # Member 1 task guide
│   ├── MEMBER_2_INSTRUCTIONS.md   # Member 2 task guide
│   ├── MEMBER_3_INSTRUCTIONS.md   # Member 3 task guide
│   ├── MEMBER_1_ROADMAP.md        # Member 1 sprint roadmap
│   ├── MEMBER_2_ROADMAP.md        # Member 2 sprint roadmap
│   ├── MEMBER_3_ROADMAP.md        # Member 3 sprint roadmap
│   ├── ROADMAP.md                 # Master MVP roadmap index
│   ├── GIT_WORKFLOW_AND_BRANCHES.md # Git branching guide
│   ├── ARCHITECTURE_DECISIONS.md # Architectural Decision Records (ADRs)
│   └── Nishitha_Daily_Progress.md # Member 2 progress log
│
├── legacy/                        📂 ARCHIVED / DEPRECATED FILES
│   ├── Phase0_implementation_plan.md
│   ├── ROADMAP_phase0.md
│   ├── Initial_Assumed_VersionMVP.md
│   └── comparision.md
│
├── tests/                         🔒 UNIT & INTEGRATION TEST SUITE
│   ├── test_ingestion.py          # Member 1 test suite
│   ├── test_ai_engine.py          # Member 2 test suite
│   └── test_api.py                # Member 3 test suite
│
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## ⚡ Quick Start & Setup

### 1. Environment Activation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)
```env
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-v1-...

DB_HOST=localhost
DB_PORT=5445
DB_NAME=rag_bootcamp
DB_USER=rag_app_user
DB_PASSWORD=rag_password
```

### 3. Run Verification Tests
```bash
# Execute the full unit test suite across all member domains
PYTHONPATH=. pytest tests/
```

### 4. Start Database & FastAPI Gateway
```bash
# Start PostgreSQL pgvector container on port 5445
docker-compose up -d db

# Run FastAPI backend API
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Unit Test Execution Output

```text
==================================== test session starts ====================================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.4.0
rootdir: /home/d_nishitha/AIPMS/FoodIntellect
collected 6 items                                                                                               

tests/test_ai_engine.py ..                                                            [ 33%]
tests/test_api.py .                                                                   [ 50%]
tests/test_ingestion.py ...                                                           [100%]

==================================== 6 passed in 7.60s ====================================
```

---

## 📄 License & Team
Academic Final-Year Engineering Project. Developed by Team **FoodIntellect**.
