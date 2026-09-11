"""
RAG Analysis Route Helper (Member 2 Workstream)

Helper logic for Member 3's FastAPI gateway to execute product RAG analysis cleanly.
"""
from schemas.contracts import ProductData, UserProfile, AnalysisResponse
from ai_engine.rag_pipeline import RAGPipeline
from ingestion.recommender import RecommenderEngine


def execute_full_analysis(
    product: ProductData,
    user_profile: UserProfile,
    allergy_check_result,
    catalog: list
) -> AnalysisResponse:
    """Helper routine executing recommendation ranking + RAG synthesis."""
    recommender = RecommenderEngine()
    recs = recommender.recommend_alternatives(product, catalog, user_profile)

    rag = RAGPipeline()
    return rag.analyze_product(product, allergy_check_result, recs)
