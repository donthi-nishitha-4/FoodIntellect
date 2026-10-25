from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


router = APIRouter(
    prefix="/analyze",
    tags=["Analysis"]
)


class ProductRequest(BaseModel):

    product_name: str

    ingredients: List[str]

    allergens: List[str] = []

    nutrition: dict = {}


@router.post("/")
def analyze_product(
    product: ProductRequest
):

    # Mock AnalysisResponse

    analysis = {

        "product_name": product.product_name,

        "overall_assessment":
            "Moderate choice. Check sugar and saturated fat intake.",

        "ingredient_analysis": [

            {
                "ingredient": "Wheat Flour",

                "category": "Grain",

                "explanation":
                    "Provides carbohydrates and is commonly used in bakery products."
            },

            {
                "ingredient": "Sugar",

                "category": "Sweetener",

                "explanation":
                    "Adds sweetness. High consumption of added sugar should be limited."
            },

            {
                "ingredient": "Palm Oil",

                "category": "Fat",

                "explanation":
                    "Used to provide texture and stability."
            },

            {
                "ingredient": "Soy Lecithin",

                "category": "Emulsifier",

                "explanation":
                    "Helps ingredients mix together."
            }
        ],

        "allergens": product.allergens,

        "health_summary":
            "This product contains gluten and soy and has relatively high sugar.",

        "recommendation": {

            "type": "healthier alternative",

            "message":
                "Consider products with lower added sugar and higher whole-grain content."
        }
    }

    return {
        "success": True,
        "analysis": analysis
    }