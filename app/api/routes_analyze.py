"""
FastAPI Analysis Gateway Routes (Member 3 Workstream)

Endpoints for analyzing products, running deterministic allergy checks,
and returning RAG synthesis answers.
"""
from fastapi import APIRouter
from schemas.contracts import ProductData, UserProfile, AnalysisResponse
from app.core.allergy_engine import AllergyEngine
from ai_engine.routes_analyze_helper import execute_full_analysis

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

allergy_engine = AllergyEngine()


@router.post("/", response_model=AnalysisResponse)
async def analyze_product(product: ProductData, user_profile: UserProfile):
    """Execute safety evaluation, alternative recommendation, and RAG synthesis."""
    # 1. Deterministic Rule-Based Allergy Evaluation (A ∩ B ≠ ∅)
    allergy_check = allergy_engine.evaluate_safety(product, user_profile)

    # 2. Delegate to Member 2's AI helper for recommendation & RAG synthesis
    result = execute_full_analysis(
        product=product,
        user_profile=user_profile,
        allergy_check_result=allergy_check,
        catalog=[product]  # Candidate catalog can be fetched from DB
    )
    return result
