"""
Recommender Engine (Member 1)

Suggests healthier alternative products from a candidate catalog by:

  1. Category filter    — only recommend products sharing at least one category
                         tag with the target product (e.g., "Biscuits" → "Biscuits").
  2. Allergen filter    — exclude any candidate that contains a user allergen
                         (strict: intersection must be empty — A ∩ B = ∅).
  3. Nutrient scoring   — rank remaining candidates by combined nutritional
                         improvement across three axes:
                           • Sugar reduction   (highest weight: 50%)
                           • Saturated fat     (medium weight: 30%)
                           • Sodium reduction  (lowest weight: 20%)
  4. Sort and return    — candidates sorted from best to worst improvement.

Produces `RecommendationItem` Pydantic objects (from schemas/contracts.py),
ready to be embedded directly into an `AnalysisResponse`.
"""

from typing import List, Dict, Optional
from schemas.contracts import ProductData, UserProfile, RecommendationItem


# ── Scoring weights for nutrient improvement dimensions ────────────────────── #
_WEIGHT_SUGAR = 0.50     # Sugar is the primary concern for most packaged foods
_WEIGHT_SAT_FAT = 0.30   # Saturated fat is the second most important dimension
_WEIGHT_SODIUM = 0.20    # Sodium is also tracked but at lower priority


class RecommenderEngine:
    """
    Content-based recommendation engine for healthier food alternatives.

    Usage:
        engine = RecommenderEngine()
        recommendations = engine.recommend_alternatives(
            target_product=nutella,
            candidate_catalog=[product_a, product_b, product_c],
            user_profile=user,
        )
        # Returns a sorted list of RecommendationItem objects
    """

    def recommend_alternatives(
        self,
        target_product: ProductData,
        candidate_catalog: List[ProductData],
        user_profile: UserProfile,
        max_results: int = 5,
    ) -> List[RecommendationItem]:
        """
        Find and rank healthier, allergen-compatible alternatives to a target product.

        Args:
            target_product:    The product the user is currently evaluating.
            candidate_catalog: List of all available alternative products to consider.
            user_profile:      User's allergen list and dietary preferences.
            max_results:       Maximum number of recommendations to return (default 5).

        Returns:
            Sorted list of RecommendationItem objects, best improvement first.
            Returns an empty list if no suitable alternatives are found.
        """
        # Normalise the user's allergen set to lowercase for case-insensitive matching
        user_allergies: set = {a.lower().strip() for a in user_profile.allergies}

        # Normalise the target product's category tags for comparison
        target_categories: set = self._normalise_tags(target_product.categories)

        # Extract target nutrition values — use sentinel 0 if missing
        target_sugar: float = target_product.nutrition.sugars_g or 0.0
        target_sat_fat: float = target_product.nutrition.saturated_fat_g or 0.0
        target_sodium: float = target_product.nutrition.sodium_mg or 0.0

        # Build a list of (score, RecommendationItem) pairs
        scored_candidates: List[tuple] = []

        for candidate in candidate_catalog:
            # ── Skip the target product itself ─────────────────────────── #
            if candidate.product_id == target_product.product_id:
                continue

            # ── Filter 1: Category overlap ─────────────────────────────── #
            # At least one category tag must match between target and candidate.
            # If either product has no categories at all, skip this filter
            # so we don't accidentally exclude everything.
            candidate_categories = self._normalise_tags(candidate.categories)
            if target_categories and candidate_categories:
                if not target_categories.intersection(candidate_categories):
                    continue  # Different food category — not a relevant alternative

            # ── Filter 2: Allergen safety (strict: A ∩ B = ∅) ─────────── #
            candidate_allergens: set = {
                a.lower().strip() for a in candidate.allergens
            }
            if user_allergies.intersection(candidate_allergens):
                continue  # Candidate triggers a user allergen — excluded

            # ── Score: Nutrient improvement ────────────────────────────── #
            cand_sugar: float = candidate.nutrition.sugars_g or 0.0
            cand_sat_fat: float = candidate.nutrition.saturated_fat_g or 0.0
            cand_sodium: float = candidate.nutrition.sodium_mg or 0.0

            # Compute per-nutrient percentage improvements
            # A positive value means the candidate is better (lower).
            # A negative value means the candidate is worse (higher).
            sugar_delta_pct = self._pct_improvement(target_sugar, cand_sugar)
            sat_fat_delta_pct = self._pct_improvement(target_sat_fat, cand_sat_fat)
            sodium_delta_pct = self._pct_improvement(target_sodium, cand_sodium)

            # Weighted composite score
            composite_score = (
                _WEIGHT_SUGAR * sugar_delta_pct
                + _WEIGHT_SAT_FAT * sat_fat_delta_pct
                + _WEIGHT_SODIUM * sodium_delta_pct
            )

            # Only recommend candidates that are actually healthier in aggregate
            if composite_score <= 0:
                continue

            # ── Build nutrient_improvements summary dict ───────────────── #
            improvements: Dict[str, str] = {}

            if sugar_delta_pct > 0:
                improvements["sugars"] = f"-{int(sugar_delta_pct)}%"
            elif sugar_delta_pct < 0:
                improvements["sugars"] = f"+{int(abs(sugar_delta_pct))}% (higher)"

            if sat_fat_delta_pct > 0:
                improvements["saturated_fat"] = f"-{int(sat_fat_delta_pct)}%"
            elif sat_fat_delta_pct < 0:
                improvements["saturated_fat"] = f"+{int(abs(sat_fat_delta_pct))}% (higher)"

            if sodium_delta_pct > 0:
                improvements["sodium"] = f"-{int(sodium_delta_pct)}%"
            elif sodium_delta_pct < 0:
                improvements["sodium"] = f"+{int(abs(sodium_delta_pct))}% (higher)"

            # ── Build human-readable reason string ─────────────────────── #
            reason = self._build_reason(
                sugar_delta_pct, sat_fat_delta_pct, sodium_delta_pct, composite_score
            )

            item = RecommendationItem(
                product_id=candidate.product_id,
                product_name=candidate.product_name,
                brand=candidate.brand,
                reason=reason,
                nutrient_improvements=improvements,
            )
            scored_candidates.append((composite_score, item))

        # Sort by composite score descending (best first)
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Return up to max_results items
        return [item for _, item in scored_candidates[:max_results]]

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _pct_improvement(target_value: float, candidate_value: float) -> float:
        """
        Calculate how much better (positive) or worse (negative) the candidate
        is compared to the target for a given nutrient.

        A result of  40.0 means the candidate has 40% less of this nutrient.
        A result of -20.0 means the candidate has 20% more of this nutrient.

        Args:
            target_value:    Nutrient amount in the target (reference) product.
            candidate_value: Nutrient amount in the candidate product.

        Returns:
            Float percentage improvement. Returns 0.0 if target_value is 0
            (to avoid division by zero).
        """
        if target_value == 0:
            return 0.0
        return ((target_value - candidate_value) / target_value) * 100.0

    @staticmethod
    def _normalise_tags(tags: List[str]) -> set:
        """
        Normalise a list of category/allergen tags to lowercase stripped strings.

        Open Food Facts uses tags like "en:biscuits" — we strip the language
        prefix so "en:biscuits" and "biscuits" match each other.

        Args:
            tags: Raw list of tag strings.

        Returns:
            Set of normalised (lowercase, no prefix) tag strings.
        """
        normalised = set()
        for tag in tags:
            cleaned = tag.lower().strip()
            # Strip language prefix (e.g., "en:" or "fr:")
            if ":" in cleaned:
                cleaned = cleaned.split(":", 1)[1]
            if cleaned:
                normalised.add(cleaned)
        return normalised

    @staticmethod
    def _build_reason(
        sugar_pct: float,
        sat_fat_pct: float,
        sodium_pct: float,
        composite_score: float,
    ) -> str:
        """
        Build a human-readable explanation of why the candidate is recommended.

        Args:
            sugar_pct:       Sugar improvement percentage.
            sat_fat_pct:     Saturated fat improvement percentage.
            sodium_pct:      Sodium improvement percentage.
            composite_score: Weighted composite improvement score.

        Returns:
            A clear, user-friendly reason string.
        """
        parts = []

        if sugar_pct > 0:
            parts.append(f"{int(sugar_pct)}% less sugar")
        if sat_fat_pct > 0:
            parts.append(f"{int(sat_fat_pct)}% less saturated fat")
        if sodium_pct > 0:
            parts.append(f"{int(sodium_pct)}% less sodium")

        if parts:
            improvements_str = ", ".join(parts)
            return (
                f"Healthier alternative: {improvements_str} per 100g, "
                f"with no conflicting allergens for your profile."
            )
        return "Similar nutritional profile with no conflicting allergens."
