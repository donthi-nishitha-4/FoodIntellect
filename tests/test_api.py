"""
Member 3 - API & Allergy Engine Test Suite
"""
from schemas.contracts import ProductData, UserProfile
from app.core.allergy_engine import AllergyEngine
from app.api.routes_analyze import analyze_product, ProductRequest


def test_allergy_engine_detection():
    engine = AllergyEngine()
    product = ProductData(
        product_id="p_001",
        product_name="Hazelnut Chocolate Spread",
        ingredients=["Sugar", "Palm Oil", "Hazelnuts", "Skimmed Milk Powder"],
        allergens=["tree_nuts", "milk"]
    )

    # Safe user profile
    safe_user = UserProfile(user_id="u_safe", allergies=["peanuts"])
    safe_res = engine.evaluate_safety(product, safe_user)
    assert safe_res.is_safe is True
    assert safe_res.warning_level == "SAFE"

    # Conflicting user profile
    danger_user = UserProfile(user_id="u_danger", allergies=["tree_nuts"])
    danger_res = engine.evaluate_safety(product, danger_user)
    assert danger_res.is_safe is False
    assert danger_res.warning_level == "DANGER"
    assert "tree_nuts" in danger_res.matched_allergens


def test_analyze_product_uses_input_values_not_hardcoded_mock():
    request_a = ProductRequest(
        product_name="Cocoa Crunch Cereal",
        ingredients=["Whole Grain Wheat", "Sugar", "Cocoa Powder", "Salt"],
        allergens=["gluten"],
        nutrition={"sugars_g": 18.0, "saturated_fat_g": 1.5, "sodium_mg": 180}
    )
    request_b = ProductRequest(
        product_name="Green Protein Shake",
        ingredients=["Pea Protein", "Stevia", "Water", "Cocoa"],
        allergens=[],
        nutrition={"sugars_g": 2.0, "saturated_fat_g": 0.4, "sodium_mg": 40}
    )

    response_a = analyze_product(request_a)
    response_b = analyze_product(request_b)

    assert response_a["analysis"]["product_name"] == "Cocoa Crunch Cereal"
    assert response_b["analysis"]["product_name"] == "Green Protein Shake"
    assert response_a["analysis"]["overall_assessment"] != response_b["analysis"]["overall_assessment"]
    assert "Moderate choice" not in response_a["analysis"]["overall_assessment"]
    assert "Moderate choice" not in response_b["analysis"]["overall_assessment"]
