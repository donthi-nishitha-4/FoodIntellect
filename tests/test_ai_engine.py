"""
Member 2 - Independent AI Engine Test Suite
"""
from schemas.contracts import ProductData, UserProfile, AllergyResult
from ai_engine.extraction.ocr_cleaner import LLMOCRCleaner
from ai_engine.embeddings.vector_store import VectorStore
from ai_engine.rag_pipeline import RAGPipeline


def test_vector_store_fallback():
    vs = VectorStore()
    results = vs.hybrid_search("palm oil")
    assert isinstance(results, list)
    assert len(results) > 0


def test_rag_pipeline_synthesis():
    product = ProductData(
        product_id="test_001",
        product_name="Test Cookie",
        ingredients=["Wheat Flour", "Sugar", "Palm Oil"]
    )
    allergy_check = AllergyResult(
        user_id="usr_1",
        product_id="test_001",
        is_safe=True,
        matched_allergens=[],
        warning_level="SAFE"
    )
    rag = RAGPipeline()
    res = rag.analyze_product(product, allergy_check, [])
    assert res.health_score > 0
    assert "Test Cookie" in res.product.product_name
