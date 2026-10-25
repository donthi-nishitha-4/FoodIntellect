# Member 3 — Individual MVP Roadmap

> **Domain:** FastAPI Application Gateway, Deterministic Allergy Safety Engine, Database ORM & Vite+React Frontend  
> **Workload Share:** 33%  
> **Git Branch:** `member3` → merged into `main`  
> **Primary Output:** Working application gateway REST API and interactive user interface.  
> **Status as of Git History:** Final integration into `main` is complete; the app layer and allergy logic are part of the current project baseline.

---

## 🎯 Strategic Objective
Build an application gateway and frontend user interface that connects Member 1's ingestion pipeline and Member 2's AI engine, enforces zero false-negative deterministic allergy safety checks ($A \cap B \neq \emptyset$), and provides a smooth user experience for barcode scanning and photo uploads.

---

## 🗓️ Phase-by-Phase Execution Plan

```text
 ┌─────────────────────────────────────────────────────────────┐
 │ Sprint 1: FastAPI Gateway Setup & Deterministic Allergy Engine│
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 2: Database Layer & REST Endpoints Assembly          │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 3: Vite + React Frontend & Component Card Suite      │
 └──────────────────────────────┬──────────────────────────────┘
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │ Sprint 4: Full System Integration, Testing & User Flow Demo │
 └─────────────────────────────────────────────────────────────┘
```

---

### Phase 1 (Sprint 1, Days 1–3): FastAPI Gateway & Deterministic Allergy Engine
- [x] Set up FastAPI main application server (`app/main.py`) with CORS middleware.
- [x] Build `app/core/allergy_engine.py`:
  - Strict rule-based set-intersection matching ($A \cap B \neq \emptyset$).
  - Synonym taxonomy expansion (`peanuts`, `tree_nuts`, `milk`, `gluten`, `soy`, `eggs`, `fish`, `shellfish`).
  - Generate `AllergyResult` output (`SAFE`, `WARNING`, `DANGER`).
- **Acceptance Criteria:** `pytest tests/test_api.py` verifies zero false-negative allergen detection.

---

### Phase 2 (Sprint 2, Days 4–7): Database Layer & REST API Endpoints
- [ ] Implement SQLAlchemy database models (`app/db/models.py`) for storing scan logs and user profiles on PostgreSQL (Port 5445).
- [ ] Complete REST API routes:
  - `routes_ingest.py`: Barcode lookup (`/api/ingest/barcode/{barcode}`) and label photo upload (`/api/ingest/ocr`).
  - `routes_user.py`: Profile allergy settings (`/api/user/`).
  - `routes_analyze.py`: Analysis gateway connecting `AllergyEngine` and Member 2's `routes_analyze_helper.py`.
- **Acceptance Criteria:** OpenAPI Swagger documentation (`/docs`) interactive test calls return valid Pydantic responses.

---

### Phase 3 (Sprint 3, Days 8–10): Vite + React Frontend Development
- [ ] Initialize Vite + React project in `frontend/` (TailwindCSS / modern glassmorphism styling).
- [ ] Build key UI components:
  - **Header & Navigation**: Title, profile switcher, dietary preference tags.
  - **Input Panel**: Barcode scanner text input + drag-and-drop packaging photo upload dropzone.
  - **Safety Banner**: High-visibility color-coded allergen warning badges (`DANGER` red, `WARNING` yellow, `SAFE` green).
  - **Product Analysis View**: Health score gauge (0–100), nutrient breakdown cards, AI summary, and alternative recommendation cards.
- **Acceptance Criteria:** React frontend seamlessly displays mock analysis data from `data/mock_analysis.json`.

---

### Phase 4 (Sprint 4, Days 11–14): Full System Integration & Presentation Setup
- [ ] Wire React frontend directly to live FastAPI backend REST endpoints.
- [ ] Conduct end-to-end user flow testing:
  1. User selects allergens (e.g. `peanuts`, `gluten`).
  2. User scans barcode `3017620422003` (Nutella).
  3. System triggers red `DANGER` alert for Hazelnuts/Milk, displays RAG summary, and highlights healthier alternatives.
- **Deliverables for Project Presentation:** Live End-to-End System Demo, User Journey Slides, and REST API Documentation.

---

## 🛠️ Key File Ownership
- `app/main.py`
- `app/api/routes_ingest.py`
- `app/api/routes_analyze.py`
- `app/api/routes_user.py`
- `app/core/allergy_engine.py`
- `app/db/models.py`
- `app/db/connection.py`
- `frontend/` (Vite + React UI)
- `tests/test_api.py`
