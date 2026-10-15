"""
Ingredient Knowledge Base Matcher (Member 1)

Fuzzy-matches raw ingredient name strings (from OCR or Open Food Facts)
against the curated seed dictionary in `ingredients_seed.json`.

Matching strategy (in priority order):
  1. Exact match          — look up normalised (lowercase/stripped) name directly.
  2. Alias match          — check all known aliases for the same name.
  3. Rapidfuzz WRatio     — token-aware fuzzy ratio with configurable cutoff.
  4. Substring fallback   — simple substring check when rapidfuzz is absent.

The main public methods return typed `IngredientInfo` Pydantic objects
(from `schemas/contracts.py`) so the rest of the pipeline can use them
without needing to know the internal dict structure.
"""

from typing import Optional, Dict, Any, List
import json
from pathlib import Path

# Import the shared contract so we return typed objects, not raw dicts
from schemas.contracts import IngredientInfo

# Guard: rapidfuzz is optional; fall back to substring matching if missing
try:
    # pyrefly: ignore [missing-import]
    from rapidfuzz import process, fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


class IngredientMatcher:
    """
    Fuzzy ingredient matcher that looks up raw label strings in the
    curated `ingredients_seed.json` knowledge base.

    Usage:
        matcher = IngredientMatcher()

        # Match a single raw ingredient string
        info: Optional[IngredientInfo] = matcher.match_and_enrich("soya lecithin")

        # Enrich a full product ingredient list at once
        enriched: List[IngredientInfo] = matcher.enrich_product_ingredients(
            ["Wheat Flour", "Sugar", "Palm Oil", "Soya Lecithin"]
        )
    """

    # Minimum fuzzy score (0–100) for a match to be accepted.
    DEFAULT_SCORE_CUTOFF: float = 80.0

    def __init__(self, seed_file_path: Optional[str] = None):
        """
        Load the ingredient knowledge base from the JSON seed file.

        Args:
            seed_file_path: Absolute or relative path to the JSON seed file.
                            Defaults to `knowledge_base/ingredients_seed.json`
                            relative to this file's location.
        """
        if seed_file_path is None:
            # Resolve relative to this source file's parent directory
            seed_file_path = str(Path(__file__).parent / "ingredients_seed.json")

        # Raw list of ingredient dicts loaded from JSON
        self._seed_data: List[Dict[str, Any]] = []

        try:
            with open(seed_file_path, "r", encoding="utf-8") as f:
                self._seed_data = json.load(f)
        except FileNotFoundError:
            # Graceful degradation — matcher returns None for every query
            self._seed_data = []
        except json.JSONDecodeError as e:
            self._seed_data = []

        # ── Build a fast O(1) lookup index ────────────────────────────── #
        # Maps every known name AND alias (all lowercase) -> raw entry dict
        self._index: Dict[str, Dict[str, Any]] = {}
        for entry in self._seed_data:
            canonical_name = entry.get("name", "").lower().strip()
            if canonical_name:
                self._index[canonical_name] = entry

            for alias in entry.get("aliases", []):
                alias_lower = alias.lower().strip()
                if alias_lower:
                    self._index[alias_lower] = entry

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def match_and_enrich(
        self,
        raw_ingredient: str,
        score_cutoff: float = DEFAULT_SCORE_CUTOFF,
    ) -> Optional[IngredientInfo]:
        """
        Match one raw ingredient string and return a typed IngredientInfo.

        Args:
            raw_ingredient: Raw string from OCR or API (e.g. "soya lecithin").
            score_cutoff:   Minimum fuzzy score threshold (default 80 / 100).

        Returns:
            IngredientInfo Pydantic model if a match is found, else None.

        Examples:
            matcher.match_and_enrich("soya lecithin")
            # → IngredientInfo(name="Soy Lecithin", function="Emulsifier", ...)

            matcher.match_and_enrich("xyz_unknown_chemical")
            # → None
        """
        raw_dict = self._match_raw(raw_ingredient, score_cutoff)
        if raw_dict is None:
            return None
        return self._dict_to_ingredient_info(raw_dict)

    def enrich_product_ingredients(
        self,
        raw_ingredients: List[str],
        score_cutoff: float = DEFAULT_SCORE_CUTOFF,
    ) -> List[IngredientInfo]:
        """
        Enrich an entire product ingredient list in one call.

        This is the main integration point with the ingestion pipeline:
        it takes the plain string list from `ProductData.ingredients`
        and returns a richer `ProductData.structured_ingredients` list.

        Ingredients that cannot be matched are silently skipped (not included
        in the output list), so the result may be shorter than the input.

        Args:
            raw_ingredients: List of raw ingredient strings (from OCR or API).
            score_cutoff:    Minimum fuzzy match score (default 80).

        Returns:
            List of matched and enriched IngredientInfo objects.

        Example:
            enriched = matcher.enrich_product_ingredients(
                ["Sugar", "Palm Oil", "Soya Lecithin", "Unknown Additive XYZ"]
            )
            # len(enriched) == 3  (XYZ has no match → skipped)
        """
        enriched: List[IngredientInfo] = []
        for raw in raw_ingredients:
            info = self.match_and_enrich(raw, score_cutoff)
            if info is not None:
                enriched.append(info)
        return enriched

    def match_ingredient(
        self,
        raw_ingredient: str,
        score_cutoff: float = DEFAULT_SCORE_CUTOFF,
    ) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility method — returns the raw dict instead of IngredientInfo.

        Kept so that existing `tests/test_ingestion.py` tests continue to pass
        without modification. New code should use `match_and_enrich()` instead.

        Args:
            raw_ingredient: Raw ingredient string.
            score_cutoff:   Minimum fuzzy score.

        Returns:
            Raw dict from the seed JSON, or None.
        """
        return self._match_raw(raw_ingredient, score_cutoff)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _match_raw(
        self,
        raw_ingredient: str,
        score_cutoff: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Core matching logic — returns raw dict or None.

        Steps:
          1. Exact / alias lookup (O(1) dict lookup)
          2. Rapidfuzz WRatio fuzzy match against all index keys
          3. Substring fallback (when rapidfuzz is not installed)
        """
        if not raw_ingredient or not raw_ingredient.strip():
            return None

        query = raw_ingredient.strip().lower()

        # Step 1 — Exact or alias match (fastest path)
        if query in self._index:
            return self._index[query]

        choices = list(self._index.keys())
        if not choices:
            return None

        # Step 2 — Rapidfuzz fuzzy match
        if RAPIDFUZZ_AVAILABLE:
            result = process.extractOne(
                query,
                choices,
                scorer=fuzz.WRatio,
                score_cutoff=score_cutoff,
            )
            if result is not None:
                matched_key = result[0]
                return self._index[matched_key]
            return None

        # Step 3 — Substring fallback (no rapidfuzz installed)
        for key in choices:
            if query in key or key in query:
                return self._index[key]
        return None

    @staticmethod
    def _dict_to_ingredient_info(entry: Dict[str, Any]) -> IngredientInfo:
        """
        Convert a raw seed-JSON dict into a typed IngredientInfo Pydantic model.

        This centralises the mapping so we only have to maintain it in one place.

        Args:
            entry: Dict from the knowledge base with keys: name, function,
                   category, allergen_flag, safety_rating, description.

        Returns:
            Validated IngredientInfo instance.
        """
        return IngredientInfo(
            name=entry.get("name", "Unknown Ingredient"),
            function=entry.get("function"),
            category=entry.get("category"),
            allergen_flag=bool(entry.get("allergen_flag", False)),
            safety_rating=entry.get("safety_rating", "Safe"),
            description=entry.get("description"),
        )
