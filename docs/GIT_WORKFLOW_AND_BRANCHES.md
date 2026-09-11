# Git Workflow & Branching Allocation

To maintain a clean codebase and eliminate merge conflicts, all team members will follow this git workflow.

---

## 1. Branch Strategy

The `main` branch is locked and kept stable. Development takes place on workstream branches:

```text
main (🔒 STABLE)
│
├── member-1-ingestion    (👤 Member 1: ingestion/, knowledge_base/)
├── member-2-ai           (👤 Member 2: ai_engine/)
└── member-3-app          (👤 Member 3: app/, frontend/)
```

### Short-Lived Feature Branches
Within each workstream, members create short-lived feature branches:
- `member-1-ingestion` $\rightarrow$ `feature/off-client`, `feature/ocr-preprocessor`
- `member-2-ai` $\rightarrow$ `feature/vector-store`, `feature/llm-cleaner`
- `member-3-app` $\rightarrow$ `feature/allergy-engine`, `feature/react-ui`

---

## 2. Shared Contract Rule (`schemas/contracts.py`)

`schemas/contracts.py` is the single source of truth for all data models.
- **Rule**: If a field needs to be added or changed in `ProductData` or `AnalysisResponse`, all 3 members must discuss and agree.
- A dedicated Pull Request must be submitted for contract changes before feature work begins.

---

## 3. How Teammates Set Up Their Local Branches

```bash
# Clone the repository
git clone <repo-url>
cd FoodIntellect

# Member 1 creates & switches to branch
git checkout -b member-1-ingestion

# Member 2 creates & switches to branch
git checkout -b member-2-ai

# Member 3 creates & switches to branch
git checkout -b member-3-app
```
