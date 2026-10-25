# Food Intellect — Master MVP Roadmap Index

> **Project:** Food Intellect  
> **Team:** 3 Members (33% / 33% / 33% Equal Workload Split)  
> **Architecture Strategy:** Independent Parallel Development via Shared Contracts (`schemas/contracts.py`)  
> **Current Status:** Functional MVP validated in WSL; merged to `main`; test evidence available from the latest repository validation run.

---

## 📌 Master Workstream & Individual Member Roadmaps

| Workstream | Team Member | Domain & Ownership | Detailed Roadmap Document | Current State |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | Data, Ingestion & Recommender | OCR pipeline, ingredient KB, recommender | 📖 [docs/MEMBER_1_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_1_ROADMAP.md) | ✅ Core work implemented |
| **Member 2** | AI Engine & RAG Lead | LLM cleaner, vector retrieval, RAG synthesis, evaluator | 📖 [docs/MEMBER_2_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_2_ROADMAP.md) | ✅ Core work implemented |
| **Member 3** | App Gateway & Frontend | FastAPI app, allergy engine, DB/session, UI integration | 📖 [docs/MEMBER_3_ROADMAP.md](file:///wsl.localhost/Ubuntu/home/d_nishitha/AIPMS/FoodIntellect/docs/MEMBER_3_ROADMAP.md) | ✅ Functional gateway and safety logic |

---

## ✅ Project Milestone Status

- [x] Shared contracts and parallel member workflow established
- [x] Member 1 ingestion and OCR pipeline implemented
- [x] Member 2 AI/RAG pipeline implemented
- [x] Member 3 app/gateway layer integrated and merged to `main`
- [x] Dependency issues resolved and validation passed in WSL
- [x] Demo-ready functional MVP exists
- [x] Research-paper direction is viable based on architecture and evaluation outputs

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
