# Member 3 — Gateway, Allergy Engine & Frontend Instructions

> **Subsystem Ownership:** `app/`  
> **Git Branch:** `member3`  
> **Project status:** Integrated into the current mainline repository and validated in the final project run.  
> **Target Output:** FastAPI gateway, deterministic allergy safety engine, and app-layer service integration.

---

## 1. Workload Description & Responsibilities

1. **FastAPI application and gateway layer**
   - Keep the app entrypoint, routing, and user-facing flows aligned with the current merged repo state.
   - Ensure the API layer communicates correctly with the ingestion and AI components.

2. **Deterministic allergy safety engine**
   - Maintain strict allergen matching against user-selected preferences.
   - Keep the safety output deterministic and explainable for demo and validation scenarios.

3. **Application integration**
   - Ensure the app layer remains compatible with the current ingestion and AI outputs.
   - Keep the user flow simple for product scanning, upload, and analysis presentation.

---

## 2. Shared Contract Rules

- Keep route and model contracts aligned with the merged project repo.
- Do not rely on stale branch assumptions from older versions of the project.
- Maintain a smooth app flow from user input to output analysis and recommendations.

---

## 3. Daily Execution Command

```bash
cd /home/d_nishitha/AIPMS/FoodIntellect
source venv/bin/activate
pytest tests/test_api.py -q
uvicorn app.main:app --reload --port 8000
```

### Current validation status
- The current repo validation passed successfully in the WSL environment.
- The warnings are from library deprecations and not from app logic failures.
