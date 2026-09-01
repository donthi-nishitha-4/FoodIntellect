# 🏛️ Architecture Decision Record (ADR): FoodIntellect MVP

This document records the key architectural and design decisions made for the **FoodIntellect** project.

---

## ADR-001: Standalone Project Directory vs. Feature Branching

### Context
The initial RAG codebase (`AIPMS / NStructions`) was developed for enterprise construction contract retrieval. FoodIntellect requires a completely different domain corpus (food ingredients, nutrition facts, allergens, and label OCR). A 3-member team will be developing distinct subsystems in parallel.

### Decision
Create a **clean, standalone project workspace** (`/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect`) rather than keeping FoodIntellect as a feature branch inside the old construction repo.

### Rationale
1. **Git Isolation**: Each team member can create clean feature branches off `main` (`feature/ocr-pipeline`, `feature/food-rag`, `feature/recommender`) without branch management confusion or commit history pollution from old construction work.
2. **Clean Project Footprint**: Excludes tens of megabytes of irrelevant construction PDFs, Excel taxonomies, and obsolete chunkers.

---

## ADR-002: Deterministic Allergy Engine vs. LLM-Based Detection

### Context
Allergies pose critical health and safety risks. Using non-deterministic LLMs for allergen identification risks hallucinating safety warnings or missing lethal allergens (e.g. peanuts, dairy).

### Decision
Enforce a **strict, rule-based deterministic matching engine** ($A \cap B \neq \emptyset$) in Python for all allergy detection. The LLM is used **strictly for explanation**, not for detection decisions.

### Rationale
1. **Safety Guarantee**: Rule-based string matching and allergen taxonomy sets guarantee zero non-deterministic false negatives.
2. **Academic & Industry Standard**: Demonstrates software engineering maturity during project reviews.

---

## ADR-003: Hybrid Retrieval with Reciprocal Rank Fusion (RRF)

### Context
Food searches require both exact keyword matching (e.g. brand names like "Oreo", specific E-numbers like "E211") and semantic retrieval (e.g. "preservatives preventing mold growth").

### Decision
Use **Hybrid Search**: Combine PostgreSQL `pgvector` dense cosine distance with PostgreSQL `pg_trgm` sparse trigram similarity using Reciprocal Rank Fusion (RRF):
$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

### Rationale
Dense vector search alone struggles on specific chemical names or E-numbers, while trigram search alone misses semantic intent. Hybrid RRF combines the strengths of both.

---

## ADR-004: Multi-Provider LLM Failover Architecture

### Context
External LLM APIs (Groq, OpenRouter, Google Gemini) can experience rate limits, model deprecation, network latency, or downtime during live project demonstrations.

### Decision
Implement a **Sequential LLM Failover Wrapper** in `src/core/llm.py`:
$$\text{Primary (Gemini-3.6-Flash)} \longrightarrow \text{Fallback 1 (Groq Llama-3.3-70b)} \longrightarrow \text{Fallback 2 (OpenRouter)}$$

### Rationale
Ensures high availability ($>99.9\%$) during evaluation tests and live user demonstrations without single-point-of-failure API dependency.

---

## ADR-005: Port Mapping & Windows Exclusion Compatibility

### Context
Windows Hyper-V automatically reserves specific TCP port ranges (e.g., 5341–5440), causing bind errors when starting PostgreSQL Docker services on standard secondary ports like 5433 or 5435.

### Decision
Map the Docker PostgreSQL container to host port **`5445`**.

### Rationale
Port 5445 falls outside Hyper-V's excluded port range and guarantees reliable socket binding across Windows host environments.
