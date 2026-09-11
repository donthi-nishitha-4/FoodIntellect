# Member 3 — Gateway, Allergy Engine & Frontend Instructions

> **Subsystem Ownership:** `app/`, `frontend/`  
> **Git Branch:** `member-3-app`  
> **Target Output:** FastAPI Gateway, Deterministic Allergy Safety Engine, and Vite+React UI.

---

## 1. Workload Description & Responsibilities

1. **FastAPI Application Gateway (`app/main.py`, `app/api/`)**:
   - `routes_ingest.py`: Barcode lookup & photo upload endpoints.
   - `routes_analyze.py`: Analysis gateway delegating to Allergy Engine and Member 2's RAG helper.
   - `routes_user.py`: User allergen profile management endpoints.

2. **Deterministic Rule-Based Allergy Engine (`app/core/allergy_engine.py`)**:
   - Implement strict set-intersection matching ($A \cap B \neq \emptyset$) in Python against user profile allergies.
   - Expand allergen taxonomy synonyms (e.g. `casein` = `milk`, `whey` = `milk`, `hazelnut` = `tree_nuts`).
   - Output zero false-negative safety warnings (`SAFE`, `WARNING`, `DANGER`).

3. **Database Layer (`app/db/`)**:
   - SQLAlchemy database models for storing product scan logs and user profiles on PostgreSQL (Port 5445).

4. **Vite + React Frontend (`frontend/`)**:
   - Barcode scanner input / image upload dropzone.
   - Modern UI cards displaying health score, color-coded allergen badges, and nutrient improvements.

---

## 2. Shared Contract Rules

- **Do NOT modify `schemas/contracts.py` directly without team PR review.**
- Develop and test UI routes using static mock responses in `data/mock_analysis.json` so you do not wait for M1/M2 production code.

---

## 3. Daily Execution Command

```bash
# Run Member 3 test suite
PYTHONPATH=. pytest tests/test_api.py

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
