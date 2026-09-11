"""
Ingredient Knowledge Base Matcher (Member 1)

Fuzzy matches raw ingredient strings against curated knowledge base entries.
"""
from typing import Optional, Dict, Any, List
import json
from pathlib import Path
try:
    from rapidfuzz import process, fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


class IngredientMatcher:
    """Fuzzy ingredient matcher utility."""


    def __init__(self, seed_file_path: Optional[str] = None):
        if seed_file_path is None:
            seed_file_path = str(Path(__file__).parent / "ingredients_seed.json")

        self.seed_data: List[Dict[str, Any]] = []
        try:
            with open(seed_file_path, "r", encoding="utf-8") as f:
                self.seed_data = json.load(f)
        except Exception:
            self.seed_data = []

        self.index: Dict[str, Dict[str, Any]] = {}
        for item in self.seed_data:
            self.index[item["name"].lower()] = item
            for alias in item.get("aliases", []):
                self.index[alias.lower()] = item

    def match_ingredient(self, raw_ingredient: str, score_cutoff: float = 80.0) -> Optional[Dict[str, Any]]:
        """Match raw ingredient name against index using rapidfuzz with fallback."""
        query = raw_ingredient.strip().lower()
        if query in self.index:
            return self.index[query]

        choices = list(self.index.keys())
        if not choices:
            return None

        if not RAPIDFUZZ_AVAILABLE:
            for k in choices:
                if query in k or k in query:
                    return self.index[k]
            return None

        result = process.extractOne(query, choices, scorer=fuzz.WRatio)
        if result and result[1] >= score_cutoff:
            matched_key = result[0]
            return self.index[matched_key]

        return None

