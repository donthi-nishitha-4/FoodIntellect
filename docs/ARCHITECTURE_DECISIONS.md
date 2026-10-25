# 🏛️ Architecture Decision Record (ADR): FoodIntellect MVP

This document records the key architectural decisions for the current FoodIntellect project state after branch integration and final validation.

---

## ADR-001: Consolidated mainline integration after member workstreams

### Context
The project originally developed in separate member branches, each focusing on a specific subsystem. Once the workstreams were validated individually, they needed to be merged into a common baseline.

### Decision
Use the repository main branch as the shared integration point for the final project state.

### Rationale
1. The merged repo now includes the ingestion, AI, and app layers together.
2. This provides one stable baseline for testing, demo, and review.
3. It avoids stale branch assumptions when documentation and validation are being maintained.

---

## ADR-002: Deterministic allergy safety remains rule-based

### Context
Food safety decisions need to be explainable and stable.

### Decision
Use a deterministic set-based allergy engine rather than relying purely on LLM-generated safety output.

### Rationale
1. Safety checks must be explainable and consistent.
2. Users need predictable results for product safety decisions.
3. The project keeps an AI layer for explanation and recommendations while preserving deterministic safety matching.

---

## ADR-003: Hybrid retrieval remains central to the AI design

### Context
Food-product queries require both semantic understanding and exact ingredient-level matching.

### Decision
Keep hybrid search in the system architecture so retrieval is grounded in both meaning and domain-specific vocabulary.

### Rationale
This is important for ingredient names, additives, and product-specific terms that simple keyword matching alone may miss.

---

## ADR-004: Current validation status accepts non-blocking warnings

### Context
The final repo validation produced deprecation warnings from third-party OCR libraries, but no failing tests.

### Decision
Treat these warnings as maintenance items rather than as blockers for project completion or demo readiness.

### Rationale
1. The project is functionally passing in the active WSL environment.
2. The warnings are from library deprecations, not application logic failures.
3. This keeps the project state realistic and demo-ready without opening unnecessary scope.

---

## ADR-005: WSL project environment is the canonical validation environment

### Context
The repo was initially validated from a Windows-based shell path, but the correct project environment is the WSL virtualenv.

### Decision
Use the WSL environment as the canonical execution and test context for this project.

### Rationale
This matches the actual repository setup and prevents shell-path issues or activation errors during validation and demo runs.
