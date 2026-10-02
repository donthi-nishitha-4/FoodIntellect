"""
RAG Pipeline Synthesizer (Member 2 Workstream)

Synthesizes ProductData + Vector Store Retrieval Context into a complete
AnalysisResponse object using Multi-Provider LLM Failover.
"""
from schemas.contracts import ProductData, AnalysisResponse, AllergyResult, RecommendationItem
from ai_engine.embeddings.vector_store import VectorStore
from ai_engine.prompts.product_summary import PRODUCT_SUMMARY_PROMPT
from ai_engine.prompts.ingredient_analysis import INGREDIENT_ANALYSIS_SYSTEM_PROMPT, INGREDIENT_ANALYSIS_HUMAN_PROMPT
from src.core.llm import failover_llm_call


class RAGPipeline:
    """RAG pipeline synthesizer."""

    def __init__(self):
        self.vector_store = VectorStore()

    def analyze_product(
        self,
        product: ProductData,
        allergy_check: AllergyResult,
        recommendations: list
    ) -> AnalysisResponse:
        """Execute RAG synthesis to generate complete AnalysisResponse."""
        # 1. Retrieve knowledge context for main ingredients
        query_text = " ".join(product.ingredients[:5]) if product.ingredients else product.product_name
        retrieved_docs = self.vector_store.hybrid_search(query_text, top_k=3)
        context_str = "\n".join([f"- {d['title']}: {d['content']}" for d in retrieved_docs])

        # 2. Synthesize analysis via LLM failover call using structured prompt template
        prompt = f"{INGREDIENT_ANALYSIS_SYSTEM_PROMPT}\n\n" + PRODUCT_SUMMARY_PROMPT.format(
            product_name=product.product_name,
            nutrition_text=f"Sugars: {product.nutrition.sugars_g or 0.0}g, Sat Fat: {product.nutrition.saturated_fat_g or 0.0}g",
            ingredients_text=", ".join(product.ingredients) if product.ingredients else "N/A",
            context_text=context_str
        )
        llm_response = failover_llm_call(prompt)
        summary = llm_response if llm_response else f"{product.product_name} summary: Contains processed ingredients. Limit intake of high sugar/saturated fat items."

        # Calculate basic health score (0-100) based on sugar/saturated fat
        sugars = product.nutrition.sugars_g or 0.0
        sat_fat = product.nutrition.saturated_fat_g or 0.0
        score = max(10, min(100, int(100 - (sugars * 1.2) - (sat_fat * 2.0))))

        return AnalysisResponse(
            product=product,
            allergy_check=allergy_check,
            recommendations=recommendations,
            summary=summary,
            health_score=score,
            key_takeaways=[
                f"Sugar content: {sugars}g per 100g",
                f"Saturated fat: {sat_fat}g per 100g",
                f"Allergen warning: {'Conflicting allergens found!' if not allergy_check.is_safe else 'No matching user allergens.'}"
            ],
            confidence_score=0.95
        )
