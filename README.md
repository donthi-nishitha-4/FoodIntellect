# 🥗 Food Intellect MVP

An AI-powered food intelligence platform combining **Label OCR**, **Deterministic Allergen Safety Engine**, **PostgreSQL Hybrid RAG Knowledge Retrieval**, and **Nutritional Recommendation Engines**.

Designed with a **33% / 33% / 33% equal workload distribution** across 3 team members, communicating through strict shared Pydantic contracts (`schemas/contracts.py`).

---

## 🚀 Key Features

- **Strict Shared Contracts (`schemas/contracts.py`)**: Centralized Pydantic v2 schemas (`ProductData`, `AnalysisResponse`, `OCRCleanerProtocol`) enabling zero-blocker parallel team development.
- **Deterministic Allergen Safety Engine**: Rule-based string matching and synonym taxonomy expansion ($A \cap B \neq \emptyset$) in Python guaranteeing zero false-negative safety warnings (`SAFE`, `WARNING`, `DANGER`).
- **PostgreSQL Hybrid Search**: Combines 384-dimensional dense vector cosine distance (`sentence-transformers`) with sparse trigram keyword search (`pg_trgm`) using Reciprocal Rank Fusion (RRF):
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
- **Multi-Provider LLM Failover Architecture**: Sequential fallback (`Gemini 3.6 Flash` $\longrightarrow$ `Groq Llama-3.3-70b` $\longrightarrow$ `OpenRouter`) guarantees >99.9% uptime.
- **Healthier Alternative Recommender**: Ranks candidate products in the same category by lower sugar and saturated fat deltas while filtering out conflicting allergens.
- **Computer Vision OCR**: OpenCV preprocessing (grayscale, adaptive thresholding, deskewing) + EasyOCR / Tesseract for packaging label text extraction.

---

## 👥 Team Workload & Domain Division (33% / 33% / 33%)

| Workstream | Owner | Domain & Subsystem Responsibilities | Branch | Roadmap Document |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | Data & Ingestion | Open Food Facts API, OpenCV Preprocessing, EasyOCR Engine, Ingredient KB Matcher, and Healthier Alternative Recommender (`ingestion/recommender.py`). | `member-1-ingestion` | 📖 [MEMBER_1_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_1_ROADMAP.md) |
| **Member 2** | AI & RAG Lead | LLM OCR Cleaner (`LLMOCRCleaner`), PostgreSQL `pgvector` + `pg_trgm` RRF Search, RAG Pipeline Synthesizer, FastAPI Route Helpers, and RAGAS Evaluator. | `member-2-ai` | 📖 [MEMBER_2_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_2_ROADMAP.md) |
| **Member 3** | App & Gateway | FastAPI Application Gateway (`app/main.py`, `app/api/`), Deterministic Allergy Safety Engine ($A \cap B \neq \emptyset$), SQLAlchemy DB Models, and Vite+React Frontend UI. | `member-3-app` | 📖 [MEMBER_3_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_3_ROADMAP.md) |

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
