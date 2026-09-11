"""
Member 3 - API & Allergy Engine Test Suite
"""
from schemas.contracts import ProductData, UserProfile
from app.core.allergy_engine import AllergyEngine


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
