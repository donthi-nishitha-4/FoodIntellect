"""
Analyze Route — Member 3 Gateway (Integrated with Member 2 RAG Engine)

POST /api/analyze/
  - Accepts ProductRequest (product name, ingredients, allergens, nutrition)
  - Runs deterministic AllergyEngine safety check (Member 3)
  - Calls execute_full_analysis() → RAGPipeline → LLM synthesis (Member 2)
  - Saves result to AnalysisHistory (SQLite)
  - Returns AnalysisResponse JSON
"""
# pyrefly: ignore[missing-import]
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import json

# pyrefly: ignore[missing-import]
from sqlalchemy.orm import Session

from schemas.contracts import (
    ProductData,
    NutritionFacts,
    UserProfile,
)
from app.core.allergy_engine import AllergyEngine
from app.db.session import get_db
from app.db.models import AnalysisHistory
from ai_engine.routes_analyze_helper import execute_full_analysis

router = APIRouter(
    prefix="/analyze",
    tags=["Analysis"]
)

_allergy_engine = AllergyEngine()


class ProductRequest(BaseModel):
    product_name: str
    ingredients: List[str] = []
    allergens: List[str] = []
    nutrition: dict = {}
    user_id: Optional[str] = None
    user_allergies: List[str] = []


def _build_product_data(req: ProductRequest) -> ProductData:
    """Convert incoming ProductRequest → shared ProductData contract."""
    n = req.nutrition

    def _f(key, *alt):
        for k in [key] + list(alt):
            if k in n and n[k] is not None:
                try:
                    return float(n[k])
                except (TypeError, ValueError):
                    pass
        return None

    nutrition = NutritionFacts(
        energy_kcal=_f("energy_kcal"),
        fat_g=_f("fat_g", "fat"),
        saturated_fat_g=_f("saturated_fat_g", "saturated_fat", "sat_fat"),
        sugars_g=_f("sugars_g", "sugars", "total_sugars"),
        sodium_mg=_f("sodium_mg", "sodium"),
        protein_g=_f("protein_g", "protein"),
        fiber_g=_f("fiber_g", "fiber"),
    )

    return ProductData(
        product_id=f"web_{abs(hash(req.product_name)) % 100000}",
        product_name=req.product_name,
        ingredients=req.ingredients,
        allergens=req.allergens,
        nutrition=nutrition,
        source="manual",
    )


@router.post("/")
def analyze_product(
    product_req: ProductRequest,
    db: Session = Depends(get_db)
):
    """
    Full AI-powered product analysis endpoint.

    1. Build ProductData from request
    2. Run AllergyEngine (deterministic safety check)
    3. Call execute_full_analysis() → RAGPipeline + LLM synthesis
    4. Save to DB history
    5. Return structured analysis response
    """
    product = _build_product_data(product_req)

    # Step 1: Deterministic allergy check
    user_allergies = product_req.user_allergies or []
    user = UserProfile(
        user_id=product_req.user_id or "anonymous",
        name="User",
        allergies=user_allergies,
    )
    allergy_result = _allergy_engine.evaluate_safety(product, user)

    # Step 2: Full RAG analysis (Member 2 AI engine)
    try:
        analysis_response = execute_full_analysis(
            product=product,
            user_profile=user,
            allergy_check_result=allergy_result,
            catalog=[],  # No catalog in web context; recommender skips gracefully
        )

        # Build ingredient analysis list for frontend
        ingredient_analysis = []
        for ing in product.ingredients:
            lowered = ing.lower()
            if "sugar" in lowered or "syrup" in lowered or "sweetener" in lowered:
                category, explanation = "Sweetener", "Adds sweetness; high sugar intake is linked to obesity and metabolic issues."
            elif "flour" in lowered or "wheat" in lowered or "oat" in lowered or "rice" in lowered:
                category, explanation = "Grain", "Provides carbohydrate energy; whole grain versions offer higher fibre."
            elif "oil" in lowered or "fat" in lowered or "butter" in lowered:
                category, explanation = "Fat", "Contributes to texture and shelf life; saturated fats should be limited."
            elif "salt" in lowered or "sodium" in lowered:
                category, explanation = "Seasoning", "Enhances flavour; high sodium is associated with hypertension."
            elif "lecithin" in lowered or "emulsif" in lowered:
                category, explanation = "Emulsifier", "Keeps ingredients blended; generally considered safe at approved levels."
            elif "milk" in lowered or "whey" in lowered or "casein" in lowered or "cream" in lowered:
                category, explanation = "Dairy", "Provides protein and calcium; major allergen for lactose-intolerant individuals."
            elif "cocoa" in lowered or "chocolate" in lowered:
                category, explanation = "Flavoring", "Adds rich flavour; dark cocoa contains antioxidant flavonoids."
            elif "protein" in lowered or "pea protein" in lowered:
                category, explanation = "Protein Source", "Supports satiety and muscle maintenance."
            elif "preservative" in lowered or "benzoate" in lowered or "sorbate" in lowered:
                category, explanation = "Preservative", "Extends shelf life; some synthetic preservatives require monitoring at high doses."
            elif "colour" in lowered or "color" in lowered or "dye" in lowered:
                category, explanation = "Food Coloring", "Provides visual appeal; some artificial colorants are linked to hyperactivity in children."
            else:
                category, explanation = "Ingredient", "Common ingredient used for flavour, texture, or stability."
            ingredient_analysis.append({
                "ingredient": ing,
                "category": category,
                "explanation": explanation,
            })

        # Allergy warning for frontend
        allergy_warning = None
        if not allergy_result.is_safe:
            allergy_warning = {
                "level": allergy_result.warning_level,
                "matched": allergy_result.matched_allergens,
                "message": allergy_result.explanation,
            }

        analysis_dict = {
            "product_name": analysis_response.product.product_name,
            "health_score": analysis_response.health_score,
            "overall_assessment": analysis_response.summary or "Analysis complete.",
            "key_takeaways": analysis_response.key_takeaways,
            "ingredient_analysis": ingredient_analysis,
            "allergens": product.allergens,
            "allergy_warning": allergy_warning,
            "confidence_score": analysis_response.confidence_score,
            "health_summary": (
                f"Health Score: {analysis_response.health_score}/100. "
                + (analysis_response.summary or "")
            ),
            "recommendation": {
                "type": "healthier alternative",
                "message": (
                    analysis_response.key_takeaways[-1]
                    if analysis_response.key_takeaways
                    else "Compare labels for a lower-sodium or higher-fibre alternative."
                ),
            },
            "pipeline": "rag_llm",
        }

    except Exception as exc:
        # Graceful fallback: deterministic rule-based summary
        sugars = product.nutrition.sugars_g or 0
        sat_fat = product.nutrition.saturated_fat_g or 0
        sodium = product.nutrition.sodium_mg or 0
        health_score = max(0, min(100, int(100 - sugars * 1.2 - sat_fat * 2.0 - sodium * 0.02)))

        analysis_dict = {
            "product_name": product.product_name,
            "health_score": health_score,
            "overall_assessment": "Analysis via deterministic engine (LLM unavailable).",
            "key_takeaways": [],
            "ingredient_analysis": [{"ingredient": i, "category": "Ingredient", "explanation": ""} for i in product.ingredients],
            "allergens": product.allergens,
            "allergy_warning": None,
            "confidence_score": 0.5,
            "health_summary": f"Health Score: {health_score}/100",
            "recommendation": {"type": "healthier alternative", "message": "Compare labels for lower sugar and sodium alternatives."},
            "pipeline": "deterministic_fallback",
            "fallback_reason": str(exc),
        }

    # Save to DB history
    try:
        history_entry = AnalysisHistory(
            user_id=int(product_req.user_id) if (product_req.user_id and product_req.user_id.isdigit()) else 0,
            product_name=product.product_name,
            barcode=None,
            ingredients=json.dumps(product.ingredients),
            analysis=json.dumps(analysis_dict),
        )
        db.add(history_entry)
        db.commit()
    except Exception:
        pass  # History save is best-effort; never block the response

    return {
        "success": True,
        "analysis": analysis_dict,
    }