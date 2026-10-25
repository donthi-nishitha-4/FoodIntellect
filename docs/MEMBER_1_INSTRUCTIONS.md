# Member 1 — Data, Ingestion & Recommender Instructions

> **Subsystem Ownership:** `ingestion/`, `knowledge_base/`  
> **Git Branch:** `member1`  
> **Project status:** This work is integrated into the current mainline repo and validated in the WSL project environment.  
> **Target Output:** Product ingestion, OCR preprocessing, ingredient matching, and healthier recommendation logic.

---

## 1. Workload Description & Responsibilities

1. **Open Food Facts ingestion and product mapping**
   - Parse product metadata, ingredient lists, nutrition facts, allergens, categories, and brand data.
   - Keep ingestion logic aligned with the current shared product contracts.

2. **OCR preprocessing and extraction**
   - Maintain robust image preprocessing and OCR extraction flow.
   - Ensure malformed image bytes fail safely at the direct function level while recovering gracefully in the pipeline.

3. **Ingredient knowledge base and matching**
   - Maintain curated ingredient and alias mapping used for normalization and recognition.
   - Keep ingredient matching logic compatible with downstream AI and safety evaluation.

4. **Healthier product recommendations**
   - Filter alternatives by category and allergen safety.
   - Rank candidate products according to meaningful nutrient improvements.

---

## 2. Shared Contract Rules

- Keep shared models and contracts aligned with the current repository state.
- Use the repo’s current product schemas rather than stale assumptions from older branch docs.
- Do not break the ingestion-to-analysis handoff expected by the main project pipeline.

---

## 3. Daily Execution Command

```bash
cd /home/d_nishitha/AIPMS/FoodIntellect
source venv/bin/activate
pytest tests/test_ingestion.py -q
```

### Current validation status
- The repo-level validation in the project WSL environment passed successfully.
- Warnings are deprecation warnings from OCR-related libraries and do not block execution.
