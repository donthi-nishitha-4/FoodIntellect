"""Shared contracts package for FoodIntellect."""
from .contracts import (
    NutritionFacts,
    IngredientInfo,
    ProductData,
    AllergyResult,
    RecommendationItem,
    AnalysisResponse,
    UserProfile,
    OCRCleanerProtocol,
    MockOCRCleaner,
)

__all__ = [
    "NutritionFacts",
    "IngredientInfo",
    "ProductData",
    "AllergyResult",
    "RecommendationItem",
    "AnalysisResponse",
    "UserProfile",
    "OCRCleanerProtocol",
    "MockOCRCleaner",
]
