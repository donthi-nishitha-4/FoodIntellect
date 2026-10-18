"""
LLM OCR Cleaner (Member 2 — Phase 1)

Converts raw, unformatted OCR text string blobs into structured ProductData
conforming to the OCRCleanerProtocol interface contract.

Design:
  1. Build a structured JSON extraction prompt using ingredient_analysis templates.
  2. Call multi-provider LLM failover (Gemini → Groq → OpenRouter).
  3. Parse the JSON response safely; strip markdown code fences if present.
  4. Map parsed fields to ProductData and NutritionFacts Pydantic models.
  5. Fall back to a deterministic mock ProductData on any failure (so the
     pipeline never crashes if the LLM is unavailable).

This module is fully testable without a running LLM by mocking
`ai_engine.extraction.ocr_cleaner.failover_llm_call`.
"""

import json
import re
from typing import Optional

from schemas.contracts import (
    ProductData,
    NutritionFacts,
    IngredientInfo,
    OCRCleanerProtocol,
)

# LLM failover — imported lazily so the module loads even if openai is missing
try:
    from src.core.llm import failover_llm_call
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    def failover_llm_call(prompt: str) -> str:  # type: ignore[misc]
        return "[ERROR] LLM module not available"


# ─────────────────────────── JSON extraction prompt ──────────────────────────

_OCR_EXTRACTION_PROMPT = """\
You are a food-label extraction specialist.
Extract structured product information from the raw OCR text below.
Return ONLY a valid JSON object — no markdown, no commentary, no code fences.

RAW OCR TEXT:
{raw_text}

Return this exact JSON schema (use null for any field that cannot be determined):
{{
  "product_name": "string or null",
  "brand": "string or null",
  "ingredients": ["list", "of", "ingredient", "strings"],
  "allergens": ["list", "of", "allergen", "strings"],
  "categories": ["list", "of", "category", "strings"],
  "nutrition": {{
    "energy_kcal": null_or_float,
    "fat_g": null_or_float,
    "saturated_fat_g": null_or_float,
    "sugars_g": null_or_float,
    "sodium_mg": null_or_float,
    "protein_g": null_or_float,
    "fiber_g": null_or_float
  }}
}}
"""

# Fallback ProductData returned when LLM or parsing fails
_FALLBACK_PRODUCT = ProductData(
    product_id="llm_fallback_001",
    product_name="Scanned Food Product",
    brand="Unknown Brand",
    ingredients=["Wheat Flour", "Sugar", "Vegetable Oil", "Salt"],
    allergens=["gluten"],
    categories=["Packaged Food"],
    source="ocr",
)


# ─────────────────────────────── Implementation ───────────────────────────────

class LLMOCRCleaner:
    """
    LLM-backed implementation of OCRCleanerProtocol.

    Parses raw OCR text into structured ProductData using a multi-provider
    LLM failover chain (Gemini → Groq → OpenRouter).

    If the LLM is unavailable or returns unparseable output, a safe fallback
    ProductData is returned so the ingestion pipeline never crashes.
    """

    def clean_text(self, raw_text: str) -> ProductData:
        """
        Parse raw messy OCR text into structured ProductData.

        Args:
            raw_text: Unformatted OCR output string from the ingestion pipeline.

        Returns:
            ProductData instance populated from LLM extraction,
            or a deterministic fallback if the LLM call fails.
        """
        if not raw_text or not raw_text.strip():
            return _FALLBACK_PRODUCT

        prompt = _OCR_EXTRACTION_PROMPT.format(raw_text=raw_text.strip())

        # ── Step 1: Call LLM ──────────────────────────────────────────────────
        try:
            response_str = failover_llm_call(prompt)
        except Exception as exc:
            print(f"[WARN] LLMOCRCleaner: LLM call raised {exc!r}. Using fallback.")
            return _FALLBACK_PRODUCT

        if not response_str or "[ERROR]" in response_str:
            print("[WARN] LLMOCRCleaner: LLM returned empty/error response. Using fallback.")
            return _FALLBACK_PRODUCT

        # ── Step 2: Extract JSON from response ────────────────────────────────
        parsed = _safe_parse_json(response_str)
        if parsed is None:
            print("[WARN] LLMOCRCleaner: JSON parsing failed. Using fallback.")
            return _FALLBACK_PRODUCT

        # ── Step 3: Map to Pydantic models ────────────────────────────────────
        return _build_product_data(parsed)


# ──────────────────────────── Private helpers ────────────────────────────────

def _safe_parse_json(text: str) -> Optional[dict]:
    """
    Extract and parse a JSON object from an LLM response string.

    Handles:
    - Bare JSON (ideal case).
    - JSON wrapped in markdown code fences (```json ... ```).
    - Extraneous leading/trailing text before/after the JSON object.
    """
    # 1. Try to parse the response directly
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences and retry
    stripped = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    stripped = re.sub(r"```$", "", stripped, flags=re.MULTILINE).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 3. Find first { ... } block in the response (greedy)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _safe_float(val) -> Optional[float]:
    """Safely coerce a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _build_product_data(parsed: dict) -> ProductData:
    """
    Build a ProductData instance from a parsed JSON dict.

    Missing or malformed fields are filled with safe defaults to prevent
    Pydantic validation errors.
    """
    raw_nutrition = parsed.get("nutrition") or {}

    nutrition = NutritionFacts(
        energy_kcal=_safe_float(raw_nutrition.get("energy_kcal")),
        fat_g=_safe_float(raw_nutrition.get("fat_g")),
        saturated_fat_g=_safe_float(raw_nutrition.get("saturated_fat_g")),
        sugars_g=_safe_float(raw_nutrition.get("sugars_g")),
        sodium_mg=_safe_float(raw_nutrition.get("sodium_mg")),
        protein_g=_safe_float(raw_nutrition.get("protein_g")),
        fiber_g=_safe_float(raw_nutrition.get("fiber_g")),
    )

    ingredients_raw = parsed.get("ingredients") or []
    ingredients = [str(i) for i in ingredients_raw if i]

    allergens_raw = parsed.get("allergens") or []
    allergens = [str(a).lower() for a in allergens_raw if a]

    categories_raw = parsed.get("categories") or []
    categories = [str(c) for c in categories_raw if c]

    return ProductData(
        product_id="llm_cleaned_001",
        product_name=str(parsed.get("product_name") or "Extracted Food Product"),
        brand=str(parsed.get("brand") or "Unknown Brand"),
        ingredients=ingredients if ingredients else ["Unknown Ingredients"],
        allergens=allergens,
        categories=categories,
        nutrition=nutrition,
        source="ocr",
    )
