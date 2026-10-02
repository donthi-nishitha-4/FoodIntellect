"""
Member 2 - Independent AI Engine Test Suite
"""
from schemas.contracts import ProductData, UserProfile, AllergyResult
from ai_engine.extraction.ocr_cleaner import LLMOCRCleaner
from ai_engine.embeddings.vector_store import VectorStore
from ai_engine.rag_pipeline import RAGPipeline
from ai_engine.routes_analyze_helper import execute_full_analysis
from ai_engine.evaluator import RAGEvaluator


def test_ocr_cleaner():
    cleaner = LLMOCRCleaner()
    raw_blob = "INGREDIENTS: Wheat Flour, Sugar, Palm Oil, Salt. CONTAINS: GLUTEN."
    product = cleaner.clean_text(raw_blob)
    assert isinstance(product, ProductData)
    assert product.product_name is not None
    assert len(product.ingredients) > 0


def test_vector_store_fallback():
    vs = VectorStore()
    results = vs.hybrid_search("palm oil")
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "content" in results[0]


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
    assert res.summary is not None


def test_execute_full_analysis_helper():
    product = ProductData(
        product_id="prod_100",
        product_name="Granola Bar",
        ingredients=["Oats", "Honey", "Almonds"]
    )
    user = UserProfile(user_id="usr_001", name="Alice", allergies=["peanuts"])
    allergy_check = AllergyResult(
        user_id=user.user_id,
        product_id=product.product_id,
        is_safe=True,
        warning_level="SAFE"
    )
    analysis = execute_full_analysis(product, user, allergy_check, [])
    assert analysis.product.product_id == "prod_100"
    assert len(analysis.key_takeaways) > 0


def test_evaluator_metrics():
    evaluator = RAGEvaluator()
    cer = evaluator.calculate_cer("hello world", "helo world")
    wer = evaluator.calculate_wer("hello world", "hello world")
    assert 0.0 <= cer <= 1.0
    assert wer == 0.0

    scores = evaluator.evaluate_response("palm oil", "Palm oil contains saturated fat.", "Palm oil high sat fat.")
    assert "faithfulness" in scores
    assert scores["faithfulness"] > 0.0

