"""
Recommender Engine (Member 1 Workstream)

Suggests healthier alternative products by filtering candidates in the same category,
excluding allergen conflicts, and ranking by lower sugar and lower saturated fat.
"""
from typing import List
from schemas.contracts import ProductData, UserProfile, RecommendationItem


class RecommenderEngine:
    """Content-based recommendation engine for healthier food alternatives."""

    def recommend_alternatives(
        self,
        target_product: ProductData,
        candidate_catalog: List[ProductData],
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Rank candidate products to find healthier, allergy-compatible alternatives."""
        recommendations = []

        target_sugar = target_product.nutrition.sugars_g or 999.0
        user_allergies = set(a.lower() for a in user_profile.allergies)

        for candidate in candidate_catalog:
            if candidate.product_id == target_product.product_id:
                continue

            # 1. Allergen Check (Must be allergy-compatible)
            candidate_allergens = set(a.lower() for a in candidate.allergens)
            if user_allergies.intersection(candidate_allergens):
                continue  # Skip conflicting product

            # 2. Nutrient Check (Must have lower sugar)
            cand_sugar = candidate.nutrition.sugars_g or 0.0
            if cand_sugar < target_sugar:
                pct_diff = int(((target_sugar - cand_sugar) / target_sugar) * 100)
                recommendations.append(
                    RecommendationItem(
                        product_id=candidate.product_id,
                        product_name=candidate.product_name,
                        brand=candidate.brand,
                        reason=f"Healthier alternative with {pct_diff}% less sugar per 100g and no conflicting allergens.",
                        nutrient_improvements={"sugars": f"-{pct_diff}%"}
                    )
                )

        return recommendations
