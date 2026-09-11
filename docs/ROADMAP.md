# Food Intellect — Master MVP Roadmap Index

> **Project:** Food Intellect  
> **Team:** 3 Members (33% / 33% / 33% Equal Workload Split)  
> **Architecture Strategy:** Independent Parallel Development via Shared Contracts (`schemas/contracts.py`)

---

## 📌 Master Workstream & Individual Member Roadmaps

Click on any team member's roadmap to view their phase-by-phase sprint tasks, deliverables, and acceptance criteria:

| Workstream | Team Member | Domain & Ownership | Detailed Roadmap Document |
| :--- | :--- | :--- | :--- |
| **Member 1** | Data, Ingestion & Recommender | Open Food Facts API, OpenCV Preprocessing, EasyOCR Engine, Ingredient KB Matcher & Healthier Alternative Recommender | 📖 [docs/MEMBER_1_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_1_ROADMAP.md) |
| **Member 2** | AI Engine & RAG Lead | LLM OCR Text Cleaner, PostgreSQL `pgvector` + `pg_trgm` RRF Search, RAG Synthesis Pipeline & RAGAS Evaluator | 📖 [docs/MEMBER_2_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_2_ROADMAP.md) |
| **Member 3** | App Gateway & Frontend | FastAPI Application Gateway, Deterministic Allergy Safety Engine ($A \cap B \neq \emptyset$), SQLAlchemy DB Models & Vite+React UI | 📖 [docs/MEMBER_3_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_3_ROADMAP.md) |

---

## 🗓️ High-Level Project Milestone Timeline

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ WEEK 1: Shared Contracts, Mock Setup & Base Subsystem Components            │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ • M1: Open Food Facts API & Seed Ingredient KB                              │
 │ • M2: LLM OCR Cleaner & PostgreSQL Vector Store Connection                  │
 │ • M3: FastAPI Gateway & Deterministic Allergy Engine (A ∩ B ≠ ∅)            │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │ WEEK 2: Core Subsystem Pipeline Implementation                             │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ • M1: OpenCV Label Preprocessing, OCR Text Engine & Healthier Recommender  │
 │ • M2: Grounded RAG Synthesis Pipeline & Multi-Provider LLM Failover          │
 │ • M3: SQLAlchemy Database Models & Vite + React UI Component Cards          │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │ WEEK 3: End-to-End System Integration & UI Wiring                          │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ • M1, M2 & M3: Connect Ingestion + AI RAG Engine into FastAPI Gateway & UI  │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │ WEEK 4: Academic Evaluation Metrics, Testing & Final Presentation            │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ • OCR CER/WER Benchmarks, RAGAS Scores (Faithfulness/Relevance), Live Demo │
 └─────────────────────────────────────────────────────────────────────────────┘
```
