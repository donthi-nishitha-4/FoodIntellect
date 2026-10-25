# Member 2 — AI Engine, RAG & AI Helpers Instructions

> **Subsystem Ownership:** `ai_engine/`  
> **Git Branch:** `member-2-ai`  
> **Project status:** Integrated into the current repo and validated in the final project merge state.  
> **Target Output:** AI extraction, retrieval, synthesis, and evaluation workflows.

---

## 1. Workload Description & Responsibilities

1. **AI extraction and cleaning**
   - Ensure OCR output is normalized into structured product data expected by the application.
   - Keep the AI cleaning layer compatible with the shared contracts used across the project.

2. **Hybrid retrieval and semantic search**
   - Maintain retrieval logic using a hybrid dense + keyword approach.
   - Keep search outputs grounded and aligned with the food domain context.

3. **RAG synthesis and analysis**
   - Produce grounded final summaries and structured product evaluations.
   - Ensure analysis answers remain explainable and evidence-based.

4. **Evaluation and validation**
   - Keep evaluation metrics and validation checks aligned with the current merged project state.
   - Treat deprecation warnings as maintenance issues, not functional failures.

---

## 2. Shared Contract Rules

- Keep the AI logic aligned with the project’s merged contracts and current repo behavior.
- Validate with the repo-level test environment rather than older, stale branch assumptions.
- Do not treat deprecation warnings as runtime defects unless they block the current workflow.

---

## 3. Daily Execution Command

```bash
cd /home/d_nishitha/AIPMS/FoodIntellect
source venv/bin/activate
pytest tests/test_ai_engine.py -q
```

### Current validation status
- The current repo validation passed successfully in the WSL project environment.
- The warnings are non-blocking deprecations from OCR-related third-party libraries.
