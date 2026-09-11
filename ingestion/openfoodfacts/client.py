"""
Open Food Facts API Client (Member 1)

Retrieves external product metadata by barcode from Open Food Facts API v2.
"""
from typing import Optional
import urllib.request
import json
from schemas.contracts import ProductData, NutritionFacts, IngredientInfo


class OpenFoodFactsClient:
    """Client for fetching product details by barcode."""

    BASE_URL = "https://world.openfoodfacts.org/api/v2/product"

    def fetch_by_barcode(self, barcode: str) -> Optional[ProductData]:
        """
        Fetch product details by barcode string.
        Returns ProductData instance or None if not found/error.
        """
        url = f"{self.BASE_URL}/{barcode}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FoodIntellect/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status != 200:
                    return None
                payload = json.loads(resp.read().decode("utf-8"))

            if payload.get("status") != 1 or "product" not in payload:
                return None

            p = payload["product"]
            nutriments = p.get("nutriments", {})
            ingredients_text = p.get("ingredients_text_en") or p.get("ingredients_text") or ""
            ing_list = [i.strip() for i in ingredients_text.split(",") if i.strip()]

            nutrition = NutritionFacts(
                energy_kcal=nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal"),
                fat_g=nutriments.get("fat_100g") or nutriments.get("fat"),
                saturated_fat_g=nutriments.get("saturated-fat_100g"),
                sugars_g=nutriments.get("sugars_100g") or nutriments.get("sugars"),
                sodium_mg=(nutriments.get("sodium_100g") or 0) * 1000 if nutriments.get("sodium_100g") else None,
                protein_g=nutriments.get("proteins_100g"),
                fiber_g=nutriments.get("fiber_100g"),
            )

            return ProductData(
                product_id=barcode,
                product_name=p.get("product_name", "Unknown Product"),
                brand=p.get("brands", "Unknown Brand"),
                barcode=barcode,
                ingredients=ing_list,
                nutrition=nutrition,
                allergens=p.get("allergens_tags", []),
                categories=p.get("categories_tags", []),
                image_url=p.get("image_url"),
                source="openfoodfacts",
            )
        except Exception:
            return None
