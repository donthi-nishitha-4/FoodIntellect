"""
FoodIntellect - Shared Contracts (Strict Shared Protocol)

This module defines the shared data models, interfaces, and protocols
communicated across Member 1 (Data & Ingestion), Member 2 (AI & RAG),
and Member 3 (App Gateway & Frontend).

RULE: Any modifications to this file should be reviewed and agreed upon by all team members.
"""
from typing import List, Optional, Dict, Protocol, Literal
from pydantic import BaseModel, Field, ConfigDict


class NutritionFacts(BaseModel):
    """Nutritional breakdown per 100g/100ml of product."""
    model_config = ConfigDict(extra="ignore")

    energy_kcal: Optional[float] = Field(default=None, description="Energy in kcal per 100g")
    fat_g: Optional[float] = Field(default=None, description="Total fat in grams per 100g")
    saturated_fat_g: Optional[float] = Field(default=None, description="Saturated fat in grams per 100g")
    sugars_g: Optional[float] = Field(default=None, description="Total sugars in grams per 100g")
    sodium_mg: Optional[float] = Field(default=None, description="Sodium in milligrams per 100g")
    protein_g: Optional[float] = Field(default=None, description="Protein in grams per 100g")
    fiber_g: Optional[float] = Field(default=None, description="Dietary fiber in grams per 100g")


class IngredientInfo(BaseModel):
    """Detailed ingredient attribute representation."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Standardized name of the ingredient")
    function: Optional[str] = Field(default=None, description="Functional role e.g. Emulsifier, Preservative, Sweetener")
    category: Optional[str] = Field(default=None, description="Ingredient category e.g. Additive, Whole Food, Oil")
    allergen_flag: bool = Field(default=False, description="True if known major allergen")
    safety_rating: Optional[str] = Field(default="Safe", description="Safety flag e.g. Safe, Caution, High Sugar")
    description: Optional[str] = Field(default=None, description="Brief explanation of the ingredient")


class ProductData(BaseModel):
    """Complete product representation produced by Ingestion (M1/M2) and consumed by RAG (M2) & API (M3)."""
    model_config = ConfigDict(extra="ignore")

    product_id: str = Field(..., description="Unique product ID or barcode string")
    product_name: str = Field(..., description="Commercial product name")
    brand: Optional[str] = Field(default="Unknown Brand", description="Brand or manufacturer name")
    barcode: Optional[str] = Field(default=None, description="EAN/UPC barcode number")
    ingredients: List[str] = Field(default_factory=list, description="Raw list of ingredient names")
    structured_ingredients: List[IngredientInfo] = Field(default_factory=list, description="Enriched ingredient list")
    nutrition: NutritionFacts = Field(default_factory=NutritionFacts, description="Nutrition breakdown")
    allergens: List[str] = Field(default_factory=list, description="Extracted allergen tags e.g. peanuts, soy, gluten")
    categories: List[str] = Field(default_factory=list, description="Product food categories")
    image_url: Optional[str] = Field(default=None, description="URL or local path to product image")
    source: Literal["openfoodfacts", "ocr", "manual", "mock"] = Field(default="mock", description="Data source provider")


class UserProfile(BaseModel):
    """User preferences, allergies, and health goals."""
    model_config = ConfigDict(extra="ignore")

    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(default="Guest User", description="Display name of user")
    allergies: List[str] = Field(default_factory=list, description="User allergen list e.g. ['peanuts', 'gluten', 'dairy']")
    dietary_preferences: List[str] = Field(default_factory=list, description="Dietary tags e.g. ['vegan', 'low_sugar']")
    max_sugar_per_100g: Optional[float] = Field(default=None, description="Maximum sugar threshold preference")


class AllergyResult(BaseModel):
    """Deterministic allergy check evaluation output."""
    model_config = ConfigDict(extra="ignore")

    user_id: str = Field(..., description="User ID evaluated against")
    product_id: str = Field(..., description="Product ID evaluated")
    is_safe: bool = Field(..., description="True if no user allergens match product ingredients")
    matched_allergens: List[str] = Field(default_factory=list, description="List of conflicting allergens detected")
    warning_level: Literal["SAFE", "WARNING", "DANGER"] = Field(default="SAFE", description="Alert severity level")
    explanation: str = Field(default="", description="Detailed human-readable explanation")


class RecommendationItem(BaseModel):
    """Suggested healthier or allergy-compatible product alternative."""
    model_config = ConfigDict(extra="ignore")

    product_id: str = Field(..., description="Alternative product ID")
    product_name: str = Field(..., description="Alternative product title")
    brand: Optional[str] = Field(default=None, description="Brand name")
    reason: str = Field(..., description="Explanation of why this alternative is recommended")
    nutrient_improvements: Dict[str, str] = Field(default_factory=dict, description="e.g. {'sugars': '-40%', 'saturated_fat': '-25%'}")


class AnalysisResponse(BaseModel):
    """Full AI-synthesized analysis response returned to the Frontend UI."""
    model_config = ConfigDict(extra="ignore")

    product: ProductData = Field(..., description="Target product details")
    allergy_check: AllergyResult = Field(..., description="Safety evaluation result")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="Alternative products")
    summary: str = Field(..., description="AI-generated executive summary of product healthiness")
    health_score: int = Field(default=50, ge=0, le=100, description="Calculated health score between 0 and 100")
    key_takeaways: List[str] = Field(default_factory=list, description="Bullet points highlighting key pros/cons")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0, description="RAG answer confidence score")


class OCRCleanerProtocol(Protocol):
    """Interface contract for OCR text cleaning implementations."""

    def clean_text(self, raw_text: str) -> ProductData:
        """Parse raw OCR text into structured ProductData model."""
        ...


class MockOCRCleaner:
    """Deterministic mock implementation of OCRCleanerProtocol for Member 1 testing."""

    def clean_text(self, raw_text: str) -> ProductData:
        return ProductData(
            product_id="mock_ocr_001",
            product_name="Sample Scanned Whole Wheat Biscuit",
            brand="Nature Health",
            ingredients=["Whole Wheat Flour", "Sugar", "Palm Oil", "Soy Lecithin", "Salt"],
            structured_ingredients=[
                IngredientInfo(name="Whole Wheat Flour", function="Base Grain", category="Whole Grain", allergen_flag=True, safety_rating="Safe", description="Rich in dietary fiber"),
                IngredientInfo(name="Sugar", function="Sweetener", category="Simple Sugar", allergen_flag=False, safety_rating="Caution", description="Added sweetener"),
                IngredientInfo(name="Palm Oil", function="Fat/Shortening", category="Oil", allergen_flag=False, safety_rating="Caution", description="High saturated fat content"),
                IngredientInfo(name="Soy Lecithin", function="Emulsifier", category="Additive", allergen_flag=True, safety_rating="Safe", description="Common soy-derived emulsifier"),
            ],
            nutrition=NutritionFacts(
                energy_kcal=450.0,
                fat_g=16.0,
                saturated_fat_g=7.5,
                sugars_g=18.0,
                sodium_mg=250.0,
                protein_g=8.0,
                fiber_g=6.0,
            ),
            allergens=["gluten", "soy"],
            categories=["Biscuits", "Snacks"],
            source="ocr",
        )
