"""
Member 1 - Independent Ingestion Test Suite
"""
from schemas.contracts import MockOCRCleaner, ProductData
from ingestion.openfoodfacts.client import OpenFoodFactsClient
from ingestion.pipeline import IngestionPipeline
from knowledge_base.matcher import IngredientMatcher
from ingestion.recommender import RecommenderEngine


def test_mock_ocr_cleaner():
    cleaner = MockOCRCleaner()
    data = cleaner.clean_text("sample raw text")
    assert isinstance(data, ProductData)
    assert data.product_name == "Sample Scanned Whole Wheat Biscuit"
    assert "gluten" in data.allergens


def test_ingredient_matcher():
    matcher = IngredientMatcher()
    match = matcher.match_ingredient("soya lecithin")
    assert match is not None
    assert match["name"] == "Soy Lecithin"


def test_recommender_engine():
    recommender = RecommenderEngine()
    # Test alternative ranking logic
    pass
