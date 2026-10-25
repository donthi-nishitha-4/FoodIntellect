# Git Workflow & Branching Allocation

This project is now using the main branch as the stable integration baseline after the member workstreams were merged and validated.

---

## 1. Current branch strategy

The repository currently reflects these active branches:

```text
main
├── member1
├── member-2-ai
└── member3
```

### Current repo state
- `main` is the integrated project baseline
- `member1` contains the ingestion and OCR workstream
- `member-2-ai` contains the AI and retrieval workstream
- `member3` contains the app and safety logic workstream

---

## 2. Merge and integration workflow

The actual project flow was:
- merge member1 into main
- merge member-2-ai into main
- merge member3 into main

This is the current repository reality and should be treated as the reference workflow for future documentation and team updates.

---

## 3. Working rules

- Keep the main branch stable for integration and validation.
- Use member branches for subsystem-specific work.
- Merge only after the relevant tests pass in the project environment.
- Document changes and validation status in the member log files.

---

## 4. Example local branch workflow

```bash
cd /home/d_nishitha/AIPMS/FoodIntellect

git checkout member1
# or

git checkout member-2-ai
# or

git checkout member3
```

### Integration example
```bash
git checkout main
git merge member3
```
