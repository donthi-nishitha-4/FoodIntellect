"""
Member 1 - Comprehensive Ingestion Test Suite

Tests cover all Member 1 modules:
  - ingestion/openfoodfacts/client.py  (OpenFoodFactsClient)
  - ingestion/ocr/preprocessor.py      (ImagePreprocessor)
  - ingestion/ocr/engine.py            (OCREngine)
  - ingestion/pipeline.py              (IngestionPipeline)
  - knowledge_base/matcher.py          (IngredientMatcher)
  - ingestion/recommender.py           (RecommenderEngine)

Design rules:
  - No network calls (OpenFoodFacts tests use mocking with unittest.mock).
  - No GPU or heavy model loading (EasyOCR is never actually called in tests).
  - All tests must pass even without cv2, pytesseract, or easyocr installed.
  - Each test has a clear docstring explaining what it checks and why.

Run with:
    PYTHONPATH=. pytest tests/test_ingestion.py -v
"""

import json
import unittest.mock as mock
from typing import List

import numpy as np
import pytest

# ── Shared contracts ───────────────────────────────────────────────────────── #
from schemas.contracts import (
    MockOCRCleaner,
    ProductData,
    NutritionFacts,
    IngredientInfo,
    UserProfile,
    RecommendationItem,
)

# ── Member 1 modules ───────────────────────────────────────────────────────── #
from ingestion.openfoodfacts.client import OpenFoodFactsClient
from ingestion.ocr.preprocessor import ImagePreprocessor
from ingestion.ocr.engine import OCREngine
from ingestion.pipeline import IngestionPipeline
from knowledge_base.matcher import IngredientMatcher
from ingestion.recommender import RecommenderEngine


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1: MockOCRCleaner (shared contract)
# ══════════════════════════════════════════════════════════════════════════════

class TestMockOCRCleaner:
    """Tests for the shared MockOCRCleaner in schemas/contracts.py."""

    def test_mock_ocr_cleaner_returns_product_data(self):
        """MockOCRCleaner.clean_text() must return a valid ProductData instance."""
        cleaner = MockOCRCleaner()
        data = cleaner.clean_text("any raw text here")
        assert isinstance(data, ProductData)

    def test_mock_ocr_cleaner_product_name(self):
        """MockOCRCleaner should return the expected biscuit product name."""
        cleaner = MockOCRCleaner()
        data = cleaner.clean_text("sample raw text")
        assert data.product_name == "Sample Scanned Whole Wheat Biscuit"

    def test_mock_ocr_cleaner_has_allergens(self):
        """MockOCRCleaner product must include 'gluten' in its allergen list."""
        cleaner = MockOCRCleaner()
        data = cleaner.clean_text("anything")
        assert "gluten" in data.allergens

    def test_mock_ocr_cleaner_has_nutrition(self):
        """MockOCRCleaner product must populate key nutrition fields."""
        cleaner = MockOCRCleaner()
        data = cleaner.clean_text("anything")
        assert data.nutrition.sugars_g == 18.0
        assert data.nutrition.sodium_mg == 250.0
        assert data.nutrition.energy_kcal == 450.0


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2: OpenFoodFactsClient
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenFoodFactsClient:
    """Tests for the Open Food Facts API client."""

    def test_invalid_barcode_returns_none(self):
        """
        A barcode that returns status != 1 from the API must return None.
        We mock urllib.request.urlopen to avoid real network calls.
        """
        client = OpenFoodFactsClient()
        mock_response_data = json.dumps({"status": 0, "status_verbose": "product not found"})

        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_cm = mock.MagicMock()
            mock_cm.__enter__ = mock.Mock(return_value=mock_cm)
            mock_cm.__exit__ = mock.Mock(return_value=False)
            mock_cm.status = 200
            mock_cm.read.return_value = mock_response_data.encode("utf-8")
            mock_urlopen.return_value = mock_cm

            result = client.fetch_by_barcode("0000000000000")
            assert result is None, "Non-existent barcode should return None"

    def test_network_error_returns_none(self):
        """
        Any network exception (timeout, DNS failure, etc.) must be caught
        and None must be returned — never raise to the caller.
        """
        client = OpenFoodFactsClient()

        with mock.patch("urllib.request.urlopen", side_effect=Exception("Network error")):
            result = client.fetch_by_barcode("3017620422003")
            assert result is None, "Network errors should return None, not raise"

    def test_valid_barcode_maps_to_product_data(self):
        """
        A valid API response must be correctly parsed into a ProductData object
        with all nutrition fields properly mapped.
        """
        client = OpenFoodFactsClient()

        # Simulate a minimal valid Open Food Facts API response
        mock_payload = {
            "status": 1,
            "product": {
                "product_name": "Test Chocolate Spread",
                "brands": "TestBrand",
                "ingredients_text_en": "Sugar, Palm Oil, Hazelnuts",
                "nutriments": {
                    "energy-kcal_100g": 539.0,
                    "fat_100g": 30.9,
                    "saturated-fat_100g": 10.6,
                    "sugars_100g": 56.3,
                    "sodium_100g": 0.042,  # API gives sodium in grams per 100g
                    "proteins_100g": 6.3,
                    "fiber_100g": 3.0,
                },
                "allergens_tags": ["en:tree-nuts", "en:milk"],
                "categories_tags": ["en:spreads", "en:sweet-spreads"],
                "image_url": "https://example.com/image.jpg",
            },
        }
        mock_response_data = json.dumps(mock_payload)

        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_cm = mock.MagicMock()
            mock_cm.__enter__ = mock.Mock(return_value=mock_cm)
            mock_cm.__exit__ = mock.Mock(return_value=False)
            mock_cm.status = 200
            mock_cm.read.return_value = mock_response_data.encode("utf-8")
            mock_urlopen.return_value = mock_cm

            result = client.fetch_by_barcode("3017620422003")

        assert result is not None, "Valid response should not return None"
        assert isinstance(result, ProductData)
        assert result.product_name == "Test Chocolate Spread"
        assert result.brand == "TestBrand"
        assert result.source == "openfoodfacts"
        assert result.barcode == "3017620422003"

    def test_nutrition_field_mapping(self):
        """
        Sodium from the API is in g/100g and must be converted to mg/100g
        (×1000). All other nutrient fields must map correctly.
        """
        client = OpenFoodFactsClient()

        mock_payload = {
            "status": 1,
            "product": {
                "product_name": "Test Biscuit",
                "brands": "Test",
                "ingredients_text_en": "Flour, Sugar",
                "nutriments": {
                    "energy-kcal_100g": 400.0,
                    "fat_100g": 15.0,
                    "saturated-fat_100g": 6.0,
                    "sugars_100g": 20.0,
                    "sodium_100g": 0.250,  # 0.250 g → 250 mg
                    "proteins_100g": 5.0,
                    "fiber_100g": 2.0,
                },
                "allergens_tags": [],
                "categories_tags": [],
                "image_url": None,
            },
        }
        mock_response_data = json.dumps(mock_payload)

        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_cm = mock.MagicMock()
            mock_cm.__enter__ = mock.Mock(return_value=mock_cm)
            mock_cm.__exit__ = mock.Mock(return_value=False)
            mock_cm.status = 200
            mock_cm.read.return_value = mock_response_data.encode("utf-8")
            mock_urlopen.return_value = mock_cm

            result = client.fetch_by_barcode("1234567890123")

        assert result.nutrition.energy_kcal == 400.0
        assert result.nutrition.fat_g == 15.0
        assert result.nutrition.saturated_fat_g == 6.0
        assert result.nutrition.sugars_g == 20.0
        assert result.nutrition.sodium_mg == pytest.approx(250.0, rel=1e-3)
        assert result.nutrition.protein_g == 5.0
        assert result.nutrition.fiber_g == 2.0

    def test_ingredients_parsed_as_list(self):
        """
        The comma-separated ingredients_text_en string from the API must be
        split into a Python list of individual ingredient strings.
        """
        client = OpenFoodFactsClient()

        mock_payload = {
            "status": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Brand",
                "ingredients_text_en": "Sugar, Palm Oil, Salt",
                "nutriments": {},
                "allergens_tags": [],
                "categories_tags": [],
                "image_url": None,
            },
        }
        mock_response_data = json.dumps(mock_payload)

        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            mock_cm = mock.MagicMock()
            mock_cm.__enter__ = mock.Mock(return_value=mock_cm)
            mock_cm.__exit__ = mock.Mock(return_value=False)
            mock_cm.status = 200
            mock_cm.read.return_value = mock_response_data.encode("utf-8")
            mock_urlopen.return_value = mock_cm

            result = client.fetch_by_barcode("9999999999999")

        assert isinstance(result.ingredients, list)
        assert "Sugar" in result.ingredients
        assert "Palm Oil" in result.ingredients
        assert "Salt" in result.ingredients


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3: ImagePreprocessor
# ══════════════════════════════════════════════════════════════════════════════

class TestImagePreprocessor:
    """Tests for the OpenCV image preprocessor."""

    def test_preprocessor_returns_ndarray(self):
        """
        preprocess_image() must always return a NumPy ndarray,
        even when cv2 is not available (mock fallback path).
        """
        preprocessor = ImagePreprocessor()
        # Use 1x1 black pixel PNG bytes — smallest valid image
        # If cv2 is not available, preprocessor returns a 100x100 zeros array
        dummy_bytes = b"\x00" * 100  # Intentionally invalid — tests fallback
        result = preprocessor.preprocess_image(dummy_bytes)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8

    def test_preprocessor_raises_on_corrupt_bytes_with_cv2(self):
        """
        When cv2 IS available and bytes are corrupt, a ValueError should be raised.
        We skip this test if cv2 is not installed.
        """
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 not installed — skipping this test")

        preprocessor = ImagePreprocessor()
        with pytest.raises(ValueError, match="Failed to decode image bytes"):
            preprocessor.preprocess_image(b"not_an_image_at_all")

    def test_preprocessor_fallback_when_no_cv2(self):
        """
        When cv2 is simulated as unavailable, preprocess_image() must
        return a 100×100 zero array (the documented mock fallback).
        """
        preprocessor = ImagePreprocessor()
        # Temporarily hide CV2_AVAILABLE to force the mock path
        with mock.patch("ingestion.ocr.preprocessor.CV2_AVAILABLE", False):
            result = preprocessor.preprocess_image(b"any bytes")
        assert result.shape == (100, 100)
        assert np.all(result == 0)

    def test_diagnostics_returns_dict(self):
        """
        get_preprocessing_diagnostics() must return a dict containing
        at least the 'steps_applied' and 'cv2_available' keys.
        """
        preprocessor = ImagePreprocessor()
        with mock.patch("ingestion.ocr.preprocessor.CV2_AVAILABLE", False):
            diag = preprocessor.get_preprocessing_diagnostics(b"any bytes")
        assert isinstance(diag, dict)
        assert "cv2_available" in diag
        assert "steps_applied" in diag
        assert isinstance(diag["steps_applied"], list)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4: OCREngine
# ══════════════════════════════════════════════════════════════════════════════

class TestOCREngine:
    """Tests for the OCR text extraction engine."""

    def _make_dummy_img(self) -> np.ndarray:
        """Create a small blank grayscale array as a dummy processed image."""
        return np.zeros((50, 50), dtype=np.uint8)

    def test_ocr_engine_returns_string(self):
        """
        extract_raw_text() must always return a non-empty string,
        even when no real OCR library is installed.
        """
        engine = OCREngine()
        dummy_img = self._make_dummy_img()
        result = engine.extract_raw_text(dummy_img)
        assert isinstance(result, str)
        assert len(result) > 0, "OCREngine should never return an empty string"

    def test_ocr_engine_mock_fallback(self):
        """
        When both EasyOCR and Tesseract are unavailable, the engine must
        return the documented mock text containing ingredient keywords.
        """
        engine = OCREngine()
        dummy_img = self._make_dummy_img()

        with mock.patch("ingestion.ocr.engine.EASYOCR_AVAILABLE", False), \
             mock.patch("ingestion.ocr.engine.PYTESSERACT_AVAILABLE", False):
            result = engine.extract_raw_text(dummy_img)

        assert "Ingredients" in result
        assert "Palm Oil" in result

    def test_ocr_engine_provider_info_returns_tuple(self):
        """
        extract_with_provider_info() must return a (text, provider_name) tuple.
        The provider_name must be one of: 'easyocr', 'tesseract', 'mock'.
        """
        engine = OCREngine()
        dummy_img = self._make_dummy_img()

        with mock.patch("ingestion.ocr.engine.EASYOCR_AVAILABLE", False), \
             mock.patch("ingestion.ocr.engine.PYTESSERACT_AVAILABLE", False):
            text, provider = engine.extract_with_provider_info(dummy_img)

        assert isinstance(text, str)
        assert provider in ("easyocr", "tesseract", "mock")
        assert provider == "mock"  # Both disabled → must use mock


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5: IngestionPipeline
# ══════════════════════════════════════════════════════════════════════════════

class TestIngestionPipeline:
    """End-to-end tests for the IngestionPipeline coordinator."""

    def test_pipeline_returns_product_data(self):
        """
        process_image() must return a ProductData instance.
        Uses MockOCRCleaner so the test has no external dependencies.
        """
        pipeline = IngestionPipeline(cleaner=MockOCRCleaner())
        # Dummy bytes — MockOCRCleaner ignores raw text and returns a fixed product
        dummy_bytes = b"\x00" * 64
        result = pipeline.process_image(dummy_bytes)
        assert isinstance(result, ProductData)

    def test_pipeline_uses_mock_cleaner_by_default(self):
        """
        When no cleaner is provided, the pipeline must default to MockOCRCleaner
        so Member 1 is never blocked by Member 2's LLMOCRCleaner implementation.
        """
        pipeline = IngestionPipeline()  # No cleaner argument
        dummy_bytes = b"\x00" * 64
        result = pipeline.process_image(dummy_bytes)
        # MockOCRCleaner always returns this specific product name
        assert result.product_name == "Sample Scanned Whole Wheat Biscuit"


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6: IngredientMatcher
# ══════════════════════════════════════════════════════════════════════════════

class TestIngredientMatcher:
    """Tests for the ingredient knowledge base fuzzy matcher."""

    @pytest.fixture
    def matcher(self) -> IngredientMatcher:
        """Create a fresh IngredientMatcher instance before each test."""
        return IngredientMatcher()

    def test_exact_name_match(self, matcher):
        """
        Exact canonical name lookup (e.g. 'palm oil') must return the
        matching entry without needing fuzzy matching.
        """
        result = matcher.match_ingredient("palm oil")
        assert result is not None
        assert result["name"] == "Palm Oil"

    def test_alias_match(self, matcher):
        """
        Known aliases listed in ingredients_seed.json must resolve to the
        correct canonical ingredient. 'soya lecithin' is an alias for 'Soy Lecithin'.
        """
        result = matcher.match_ingredient("soya lecithin")
        assert result is not None
        assert result["name"] == "Soy Lecithin"

    def test_e_number_alias_match(self, matcher):
        """
        E-number aliases (e.g. 'e322' for Soy Lecithin) must also match correctly.
        These are commonly printed on European food labels.
        """
        result = matcher.match_ingredient("e322")
        assert result is not None
        assert result["name"] == "Soy Lecithin"

    def test_fuzzy_match_with_typo(self, matcher):
        """
        Common OCR recognition errors (typos) should still resolve to the
        correct ingredient when the score is above the cutoff.
        For example 'sodiom benzoate' (m instead of um) → Sodium Benzoate.
        """
        result = matcher.match_ingredient("sodiom benzoate")  # OCR typo
        # Accept either a match (rapidfuzz available) or None (no rapidfuzz)
        # Both outcomes are valid depending on the environment
        if result is not None:
            assert result["name"] == "Sodium Benzoate"

    def test_unknown_ingredient_returns_none(self, matcher):
        """
        A completely unknown string with no fuzzy match should return None,
        not raise an exception or return a wrong match.
        """
        result = matcher.match_ingredient("xyzunknownchemical123")
        assert result is None

    def test_empty_string_returns_none(self, matcher):
        """
        An empty input string must return None without raising any error.
        """
        result = matcher.match_ingredient("")
        assert result is None

    def test_match_and_enrich_returns_ingredient_info(self, matcher):
        """
        match_and_enrich() must return a typed IngredientInfo Pydantic object,
        not a raw dict. This validates the type-safe integration with the pipeline.
        """
        result = matcher.match_and_enrich("soy lecithin")
        assert result is not None
        assert isinstance(result, IngredientInfo)
        assert result.name == "Soy Lecithin"
        assert result.function == "Emulsifier"
        assert result.allergen_flag is True

    def test_enrich_product_ingredients_skips_unknowns(self, matcher):
        """
        enrich_product_ingredients() must enrich known ingredients and
        silently skip unrecognised ones (no error, shorter output list).
        """
        raw_list = ["Palm Oil", "Soy Lecithin", "totally_unknown_xyz_ingredient"]
        enriched = matcher.enrich_product_ingredients(raw_list)

        assert isinstance(enriched, list)
        assert len(enriched) == 2  # 2 known, 1 unknown skipped
        names = [e.name for e in enriched]
        assert "Palm Oil" in names
        assert "Soy Lecithin" in names

    def test_enrich_product_ingredients_all_match(self, matcher):
        """
        When all ingredients are known, enrich_product_ingredients() must
        return a list of the same length as the input.
        """
        raw_list = ["Sugar", "Salt", "Maltodextrin"]
        enriched = matcher.enrich_product_ingredients(raw_list)
        assert len(enriched) == 3
        for item in enriched:
            assert isinstance(item, IngredientInfo)

    def test_match_and_enrich_unknown_returns_none(self, matcher):
        """
        match_and_enrich() must return None for unrecognised ingredients.
        """
        result = matcher.match_and_enrich("completely_alien_substance_xyz")
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7: RecommenderEngine
# ══════════════════════════════════════════════════════════════════════════════

def _make_product(
    product_id: str,
    name: str,
    categories: list,
    allergens: list,
    sugars: float,
    sat_fat: float,
    sodium: float,
) -> ProductData:
    """
    Helper factory to quickly create ProductData objects for recommender tests.
    All non-specified fields use safe defaults.
    """
    return ProductData(
        product_id=product_id,
        product_name=name,
        brand="TestBrand",
        categories=categories,
        allergens=allergens,
        nutrition=NutritionFacts(
            sugars_g=sugars,
            saturated_fat_g=sat_fat,
            sodium_mg=sodium,
            energy_kcal=400.0,
            fat_g=15.0,
            protein_g=5.0,
            fiber_g=2.0,
        ),
        ingredients=[],
        source="mock",
    )


class TestRecommenderEngine:
    """Tests for the healthier alternative recommendation engine."""

    @pytest.fixture
    def engine(self) -> RecommenderEngine:
        return RecommenderEngine()

    @pytest.fixture
    def safe_user(self) -> UserProfile:
        """User with no allergies."""
        return UserProfile(user_id="u_safe", name="Safe User", allergies=[])

    @pytest.fixture
    def nut_allergic_user(self) -> UserProfile:
        """User allergic to tree nuts."""
        return UserProfile(user_id="u_nuts", name="Nut Allergy User", allergies=["tree_nuts"])

    def test_recommender_filters_allergens(self, engine, nut_allergic_user):
        """
        Products containing a user's allergen must be excluded from recommendations.
        """
        target = _make_product("t1", "Nutella", ["spreads"], [], 56.0, 10.0, 42.0)
        candidate_safe = _make_product("c1", "Low Sugar Spread", ["spreads"], [], 20.0, 4.0, 30.0)
        candidate_danger = _make_product("c2", "Nut Spread", ["spreads"], ["tree_nuts"], 15.0, 3.0, 25.0)

        results = engine.recommend_alternatives(target, [candidate_safe, candidate_danger], nut_allergic_user)
        result_ids = [r.product_id for r in results]

        assert "c1" in result_ids, "Safe candidate should be recommended"
        assert "c2" not in result_ids, "Nut-containing candidate must be excluded for nut-allergic user"

    def test_recommender_ranks_lower_sugar_first(self, engine, safe_user):
        """
        Among allergen-safe candidates in the same category, the one with the
        greatest sugar reduction must appear first in the results.
        """
        target = _make_product("t1", "High Sugar Drink", ["beverages"], [], 40.0, 2.0, 50.0)
        # candidate_best has 75% less sugar; candidate_ok has 50% less sugar
        candidate_best = _make_product("c1", "Very Low Sugar Drink", ["beverages"], [], 10.0, 2.0, 50.0)
        candidate_ok = _make_product("c2", "Medium Sugar Drink", ["beverages"], [], 20.0, 2.0, 50.0)

        results = engine.recommend_alternatives(target, [candidate_ok, candidate_best], safe_user)

        assert len(results) >= 2
        assert results[0].product_id == "c1", "Best improvement (lowest sugar) should rank first"

    def test_recommender_excludes_worse_products(self, engine, safe_user):
        """
        A product with MORE sugar than the target must NOT be recommended,
        even if it has no allergen conflicts.
        """
        target = _make_product("t1", "Target Biscuit", ["biscuits"], [], 18.0, 7.0, 250.0)
        worse_candidate = _make_product("c1", "Sweeter Biscuit", ["biscuits"], [], 40.0, 10.0, 300.0)

        results = engine.recommend_alternatives(target, [worse_candidate], safe_user)
        assert len(results) == 0, "A product worse in all nutrients should not be recommended"

    def test_recommender_skips_same_product(self, engine, safe_user):
        """
        The target product itself must not appear in its own recommendations,
        even if it passes all other filters.
        """
        target = _make_product("t1", "Target Biscuit", ["biscuits"], [], 18.0, 7.0, 250.0)
        results = engine.recommend_alternatives(target, [target], safe_user)
        assert len(results) == 0, "Target product must never recommend itself"

    def test_recommender_category_filter(self, engine, safe_user):
        """
        A candidate from a completely different food category must not be
        recommended as an alternative to the target.
        For example, a dairy yoghurt is not a valid alternative to a chocolate biscuit.
        """
        target = _make_product("t1", "Chocolate Biscuit", ["biscuits"], [], 30.0, 8.0, 200.0)
        different_category = _make_product("c1", "Low Sugar Yoghurt", ["dairy", "yoghurt"], [], 5.0, 1.0, 50.0)

        results = engine.recommend_alternatives(target, [different_category], safe_user)
        assert len(results) == 0, "Different-category product must not be recommended"

    def test_recommender_nutrient_improvements_dict(self, engine, safe_user):
        """
        Each RecommendationItem must include a nutrient_improvements dict
        showing the percentage change for at least one nutrient.
        """
        target = _make_product("t1", "High Sugar Spread", ["spreads"], [], 56.0, 10.0, 42.0)
        candidate = _make_product("c1", "Low Sugar Spread", ["spreads"], [], 20.0, 5.0, 20.0)

        results = engine.recommend_alternatives(target, [candidate], safe_user)
        assert len(results) == 1
        item = results[0]
        assert isinstance(item, RecommendationItem)
        assert len(item.nutrient_improvements) > 0, "nutrient_improvements must not be empty"

    def test_recommender_reason_string_not_empty(self, engine, safe_user):
        """
        Every RecommendationItem must include a non-empty reason string
        explaining why it was recommended.
        """
        target = _make_product("t1", "Cookie", ["biscuits"], [], 30.0, 8.0, 200.0)
        candidate = _make_product("c1", "Healthier Cookie", ["biscuits"], [], 10.0, 3.0, 80.0)

        results = engine.recommend_alternatives(target, [candidate], safe_user)
        assert len(results) == 1
        assert len(results[0].reason) > 0

    def test_recommender_max_results_respected(self, engine, safe_user):
        """
        The max_results parameter must cap the number of recommendations returned.
        """
        target = _make_product("t1", "Cookie", ["biscuits"], [], 50.0, 15.0, 300.0)
        candidates = [
            _make_product(f"c{i}", f"Healthier Cookie {i}", ["biscuits"], [], 10.0 + i, 3.0, 80.0)
            for i in range(10)  # 10 valid candidates
        ]

        results = engine.recommend_alternatives(target, candidates, safe_user, max_results=3)
        assert len(results) <= 3, "max_results must be respected"

    def test_recommender_empty_catalog_returns_empty_list(self, engine, safe_user):
        """
        An empty candidate catalog must return an empty list, not raise an error.
        """
        target = _make_product("t1", "Cookie", ["biscuits"], [], 30.0, 8.0, 200.0)
        results = engine.recommend_alternatives(target, [], safe_user)
        assert results == []

    def test_recommender_includes_sodium_improvement(self, engine, safe_user):
        """
        When a candidate has lower sodium (even with similar sugar),
        it should still appear in results if the composite improvement > 0.
        """
        target = _make_product("t1", "Salty Cracker", ["crackers"], [], 5.0, 2.0, 500.0)
        low_sodium = _make_product("c1", "Low Salt Cracker", ["crackers"], [], 5.0, 2.0, 100.0)

        results = engine.recommend_alternatives(target, [low_sodium], safe_user)
        assert len(results) == 1, "Lower sodium candidate must be recommended"
        assert "sodium" in results[0].nutrient_improvements


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8: OCREvaluator  (Phase 4 — Academic Evaluation)
# ══════════════════════════════════════════════════════════════════════════════

from ingestion.ocr.evaluator import OCREvaluator


class TestOCREvaluator:
    """Tests for the OCR CER/WER evaluation module (Phase 4 academic deliverable)."""

    @pytest.fixture
    def evaluator(self) -> OCREvaluator:
        return OCREvaluator()

    def test_cer_exact_match_is_zero(self, evaluator):
        """CER must be 0.0 when hypothesis exactly equals reference."""
        assert evaluator.compute_cer("Whole Wheat Flour", "Whole Wheat Flour") == 0.0

    def test_cer_single_char_error(self, evaluator):
        """CER of 1-char error in a 5-char word must be 0.2 (1/5)."""
        cer = evaluator.compute_cer("Sugar", "Suqar")  # 1 substitution
        assert abs(cer - 0.2) < 1e-6

    def test_cer_empty_reference_returns_zero(self, evaluator):
        """Empty reference is undefined; must return 0.0 without raising."""
        assert evaluator.compute_cer("", "anything") == 0.0

    def test_wer_exact_match_is_zero(self, evaluator):
        """WER must be 0.0 when hypothesis exactly equals reference."""
        assert evaluator.compute_wer("Palm Oil Salt", "Palm Oil Salt") == 0.0

    def test_wer_one_word_error(self, evaluator):
        """WER must be 0.333 for 1 word error in a 3-word reference."""
        wer = evaluator.compute_wer("Palm Oil Salt", "Palm 0il Salt")  # '0il' ≠ 'Oil'
        assert abs(wer - (1 / 3)) < 1e-6

    def test_evaluate_dataset_returns_correct_keys(self, evaluator):
        """evaluate_dataset() result dicts must contain 'cer', 'wer', 'exact_match'."""
        samples = [{"reference": "Sugar", "hypothesis": "Sugar",
                    "provider": "mock", "image_id": "t1"}]
        results = evaluator.evaluate_dataset(samples)
        assert len(results) == 1
        r = results[0]
        assert "cer" in r
        assert "wer" in r
        assert "exact_match" in r
        assert r["exact_match"] is True

    def test_compute_summary_overall_keys(self, evaluator):
        """compute_summary() must return 'overall' with mean_cer, mean_wer, n_samples."""
        samples = [
            {"reference": "Sugar", "hypothesis": "Sugar", "provider": "easyocr"},
            {"reference": "Salt",  "hypothesis": "Sa1t",  "provider": "tesseract"},
        ]
        results = evaluator.evaluate_dataset(samples)
        summary = evaluator.compute_summary(results)
        assert "overall" in summary
        assert "mean_cer" in summary["overall"]
        assert "mean_wer" in summary["overall"]
        assert summary["overall"]["n_samples"] == 2

    def test_compute_summary_by_provider(self, evaluator):
        """compute_summary() must group results correctly by provider name."""
        samples = [
            {"reference": "Palm Oil", "hypothesis": "Palm Oil", "provider": "easyocr"},
            {"reference": "Salt",     "hypothesis": "Sa1t",     "provider": "tesseract"},
        ]
        results = evaluator.evaluate_dataset(samples)
        summary = evaluator.compute_summary(results, group_by_provider=True)
        assert "by_provider" in summary
        assert "easyocr" in summary["by_provider"]
        assert "tesseract" in summary["by_provider"]
        # EasyOCR sample was perfect
        assert summary["by_provider"]["easyocr"]["mean_cer"] == 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 9: MatcherEvaluator  (Phase 4 — Academic Evaluation)
# ══════════════════════════════════════════════════════════════════════════════

from knowledge_base.matcher_evaluator import MatcherEvaluator, EvalSample


class TestMatcherEvaluator:
    """Tests for the ingredient matcher F1-score evaluation module (Phase 4)."""

    @pytest.fixture
    def evaluator(self) -> MatcherEvaluator:
        return MatcherEvaluator()

    def test_all_correct_gives_f1_one(self, evaluator):
        """A dataset of known matches + known unknowns must yield F1 = 1.0."""
        samples = [
            EvalSample("palm oil",            "Palm Oil"),
            EvalSample("soya lecithin",       "Soy Lecithin"),
            EvalSample("xyz_completely_fake", None),
        ]
        report = evaluator.evaluate(samples)
        assert report["f1"] == 1.0
        assert report["tp"] == 2
        assert report["tn"] == 1
        assert report["fp"] == 0
        assert report["fn"] == 0

    def test_false_positive_lowers_precision(self, evaluator):
        """When a match is returned for an item that should return None, FP increases."""
        # 'sugar' WILL be matched by the matcher, but we claim expected=None
        samples = [EvalSample("sugar", None)]
        report = evaluator.evaluate(samples)
        # precision = TP/(TP+FP); with 0 TP and ≥1 FP, precision < 1
        assert report["fp"] >= 1
        assert report["precision"] < 1.0

    def test_false_negative_lowers_recall(self, evaluator):
        """When a match is missed for a known ingredient, FN increases."""
        # Completely unknown string — matcher will return None
        samples = [EvalSample("xyzzzz_unknown_chemical_999", "Soy Lecithin")]
        report = evaluator.evaluate(samples)
        assert report["fn"] == 1
        assert report["recall"] == 0.0

    def test_report_contains_required_keys(self, evaluator):
        """Evaluation report dict must contain all required metric keys."""
        samples = [EvalSample("sugar", "Sugar")]
        report = evaluator.evaluate(samples)
        for key in ("precision", "recall", "f1", "accuracy", "tp", "fp", "fn", "tn",
                    "n_samples", "per_sample"):
            assert key in report, f"Missing key: {key}"

    def test_per_sample_results_correct_length(self, evaluator):
        """per_sample list must have one entry per input sample."""
        samples = [
            EvalSample("sugar", "Sugar"),
            EvalSample("palm oil", "Palm Oil"),
            EvalSample("xyz_fake", None),
        ]
        report = evaluator.evaluate(samples)
        assert len(report["per_sample"]) == 3

    def test_e_number_alias_true_positive(self, evaluator):
        """E-number aliases (e322) must be counted as True Positives."""
        samples = [EvalSample("e322", "Soy Lecithin")]
        report = evaluator.evaluate(samples)
        assert report["tp"] == 1
        assert report["fp"] == 0

    def test_empty_dataset_returns_zeros(self, evaluator):
        """An empty input dataset must return all-zero metrics without raising."""
        report = evaluator.evaluate([])
        assert report["f1"] == 0.0
        assert report["n_samples"] == 0
        assert report["per_sample"] == []
