"""
RAG Pipeline Synthesizer (Member 2 — Phase 3)

Orchestrates the full retrieval-augmented generation workflow:

  1. Retrieve relevant food-science evidence from VectorStore (DB or fallback).
  2. Format context using structured prompt templates.
  3. Call LLM failover chain (Gemini → Groq → OpenRouter) for synthesis.
  4. Parse and build a complete AnalysisResponse (summary, health_score,
     key_takeaways, confidence_score).
  5. Fall back to a deterministic rule-based summary if LLM is unavailable.

The health_score formula (deterministic, not LLM-dependent):
    score = 100 - (sugars_g * 1.2) - (saturated_fat_g * 2.0) - (sodium_mg * 0.02)
    clamped to [10, 100]

This module is fully testable without a live LLM by mocking
`ai_engine.rag_pipeline.failover_llm_call`.
"""

from __future__ import annotations

from typing import List

from schemas.contracts import (
    AnalysisResponse,
    AllergyResult,
    ProductData,
    RecommendationItem,
)
from ai_engine.embeddings.vector_store import VectorStore
from ai_engine.prompts.ingredient_analysis import (
    INGREDIENT_ANALYSIS_SYSTEM_PROMPT,
    INGREDIENT_ANALYSIS_HUMAN_PROMPT,
)
from ai_engine.prompts.product_summary import PRODUCT_SUMMARY_PROMPT

try:
    from src.core.llm import failover_llm_call
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    def failover_llm_call(prompt: str) -> str:  # type: ignore[misc]
        return ""


# ──────────────────────────── Health score formula ────────────────────────────

def _compute_health_score(product: ProductData) -> int:
    """
    Deterministic health score: 0–100.

    Formula:
        score = 100 - (sugars_g * 1.2) - (saturated_fat_g * 2.0) - (sodium_mg * 0.02)
    Clamped to [10, 100].

    Penalises high-sugar, high-saturated-fat, high-sodium products more heavily.
    """
    sugars = product.nutrition.sugars_g or 0.0
    sat_fat = product.nutrition.saturated_fat_g or 0.0
    sodium = product.nutrition.sodium_mg or 0.0
    raw_score = 100.0 - (sugars * 1.2) - (sat_fat * 2.0) - (sodium * 0.02)
    return max(10, min(100, int(raw_score)))


def _build_key_takeaways(product: ProductData, allergy_check: AllergyResult) -> List[str]:
    """
    Build factual, rule-based bullet-point takeaways regardless of LLM availability.
    """
    takeaways: List[str] = []
    n = product.nutrition

    # Sugar
    if n.sugars_g is not None:
        if n.sugars_g > 22.5:
            takeaways.append(f"⚠ High sugar content: {n.sugars_g:.1f}g per 100g (>22.5g threshold)")
        elif n.sugars_g > 10:
            takeaways.append(f"◔ Moderate sugar: {n.sugars_g:.1f}g per 100g")
        else:
            takeaways.append(f"✓ Low sugar: {n.sugars_g:.1f}g per 100g")

    # Saturated fat
    if n.saturated_fat_g is not None:
        if n.saturated_fat_g > 5.0:
            takeaways.append(f"⚠ High saturated fat: {n.saturated_fat_g:.1f}g per 100g (>5g threshold)")
        elif n.saturated_fat_g > 1.5:
            takeaways.append(f"◔ Moderate saturated fat: {n.saturated_fat_g:.1f}g per 100g")
        else:
            takeaways.append(f"✓ Low saturated fat: {n.saturated_fat_g:.1f}g per 100g")

    # Sodium
    if n.sodium_mg is not None:
        if n.sodium_mg > 600:
            takeaways.append(f"⚠ High sodium: {n.sodium_mg:.0f}mg per 100g (>600mg threshold)")
        elif n.sodium_mg > 120:
            takeaways.append(f"◔ Moderate sodium: {n.sodium_mg:.0f}mg per 100g")
        else:
            takeaways.append(f"✓ Low sodium: {n.sodium_mg:.0f}mg per 100g")

    # Allergen warning
    if not allergy_check.is_safe:
        allergen_list = ", ".join(allergy_check.matched_allergens)
        takeaways.append(f"🚨 Allergen conflict detected: {allergen_list}")
    else:
        takeaways.append("✓ No matching allergens for this user profile")

    # Fibre bonus
    if n.fiber_g is not None and n.fiber_g >= 6.0:
        takeaways.append(f"✓ High dietary fibre: {n.fiber_g:.1f}g per 100g")

    return takeaways if takeaways else ["Nutritional information not fully available for this product."]


def _build_fallback_summary(product: ProductData, context_str: str, health_score: int) -> str:
    """
    Deterministic summary used when LLM is unavailable or returns an error.
    Uses PRODUCT_SUMMARY_PROMPT template values but composes inline.
    """
    ingredients_text = ", ".join(product.ingredients[:8]) if product.ingredients else "Unknown"
    n = product.nutrition
    nutrition_text = (
        f"Energy {n.energy_kcal or '?'} kcal, "
        f"Sugar {n.sugars_g or '?'}g, "
        f"Saturated fat {n.saturated_fat_g or '?'}g, "
        f"Sodium {n.sodium_mg or '?'}mg per 100g"
    )
    score_band = (
        "good nutritional quality" if health_score >= 70
        else "moderate nutritional quality" if health_score >= 45
        else "poor nutritional quality (high in sugar/fat/sodium)"
    )
    return (
        f"{product.product_name} is a packaged food product of {score_band} "
        f"(health score: {health_score}/100). "
        f"Main ingredients include {ingredients_text}. "
        f"Nutritional profile per 100g: {nutrition_text}. "
        f"{'Review the allergen warnings before consuming.' if product.allergens else ''}"
    ).strip()


# ──────────────────────────── RAGPipeline class ───────────────────────────────

class RAGPipeline:
    """
    RAG pipeline synthesizer (Member 2 core deliverable).

    Retrieves food-science evidence from VectorStore, formats it using the
    structured prompt templates, calls the LLM failover chain, and returns
    a complete AnalysisResponse.
    """

    def __init__(self):
        self.vector_store = VectorStore()

    def analyze_product(
        self,
        product: ProductData,
        allergy_check: AllergyResult,
        recommendations: List[RecommendationItem],
    ) -> AnalysisResponse:
        """
        Execute RAG synthesis to generate a complete AnalysisResponse.

        Args:
            product:          Target product (from M1 ingestion pipeline).
            allergy_check:    Deterministic allergen safety result (from M3 engine).
            recommendations:  Ranked alternative products (from M1 recommender).

        Returns:
            AnalysisResponse with summary, health_score, key_takeaways,
            and confidence_score.
        """
        # ── Step 1: Retrieve evidence context ─────────────────────────────────
        query_text = " ".join(product.ingredients[:6]) or product.product_name
        retrieved_docs = self.vector_store.hybrid_search(query_text, top_k=4)
        context_str = "\n".join([
            f"[{doc['title']}]: {doc['content']}"
            for doc in retrieved_docs
        ])

        # ── Step 2: Compute deterministic health score ────────────────────────
        health_score = _compute_health_score(product)

        # ── Step 3: Build key takeaways (always deterministic) ────────────────
        key_takeaways = _build_key_takeaways(product, allergy_check)

        # ── Step 4: Synthesize summary via LLM ───────────────────────────────
        summary = self._synthesize_summary(product, context_str, health_score)

        # ── Step 5: Determine confidence score ───────────────────────────────
        # Higher confidence when LLM summary contains product name (not fallback)
        confidence = 0.92 if product.product_name.lower() in summary.lower() else 0.75

        return AnalysisResponse(
            product=product,
            allergy_check=allergy_check,
            recommendations=recommendations,
            summary=summary,
            health_score=health_score,
            key_takeaways=key_takeaways,
            confidence_score=min(1.0, confidence),
        )

    def _synthesize_summary(
        self, product: ProductData, context_str: str, health_score: int
    ) -> str:
        """
        Build the LLM synthesis prompt and call the failover chain.
        Falls back to a deterministic rule-based summary on any failure.
        """
        if not LLM_AVAILABLE:
            return _build_fallback_summary(product, context_str, health_score)

        # Build prompt using product_summary template
        ingredients_text = ", ".join(product.ingredients) if product.ingredients else "Not specified"
        n = product.nutrition
        nutrition_text = (
            f"Energy: {n.energy_kcal or '?'} kcal/100g | "
            f"Sugars: {n.sugars_g or '?'}g | "
            f"Saturated fat: {n.saturated_fat_g or '?'}g | "
            f"Sodium: {n.sodium_mg or '?'}mg | "
            f"Protein: {n.protein_g or '?'}g | "
            f"Fibre: {n.fiber_g or '?'}g"
        )

        prompt = PRODUCT_SUMMARY_PROMPT.format(
            product_name=product.product_name,
            nutrition_text=nutrition_text,
            ingredients_text=ingredients_text,
            context_text=context_str if context_str else "No specific evidence retrieved.",
        )

        # Prepend the system persona from ingredient_analysis prompts
        full_prompt = (
            f"{INGREDIENT_ANALYSIS_SYSTEM_PROMPT}\n\n"
            f"Health Score Calculated: {health_score}/100\n\n"
            f"{prompt}"
        )

        try:
            llm_response = failover_llm_call(full_prompt)
        except Exception as exc:
            print(f"[WARN] RAGPipeline: LLM call raised {exc!r}. Using fallback summary.")
            return _build_fallback_summary(product, context_str, health_score)

        if not llm_response or "[ERROR]" in llm_response or len(llm_response.strip()) < 20:
            return _build_fallback_summary(product, context_str, health_score)

        return llm_response.strip()
