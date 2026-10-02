# 1. Test OCR Text Cleaner
from ai_engine.extraction.ocr_cleaner import LLMOCRCleaner

cleaner = LLMOCRCleaner()
raw_ocr = "PRODUCT: Crunchy Biscuits. INGREDIENTS: Wheat Flour, Palm Oil, Sugar, Soy Lecithin."
product = cleaner.clean_text(raw_ocr)
print("Parsed Product Name:", product.product_name)
print("Extracted Ingredients:", product.ingredients)

# 2. Test Vector Store Hybrid Search
from ai_engine.embeddings.vector_store import VectorStore

vs = VectorStore()
evidence = vs.hybrid_search("palm oil saturated fat", top_k=2)
print("Retrieved Evidence Chunks:", evidence)

# 3. Test Full RAG Synthesis Pipeline
from schemas.contracts import ProductData, UserProfile, AllergyResult
from ai_engine.routes_analyze_helper import execute_full_analysis

prod = ProductData(
    product_id="p101",
    product_name="Dark Chocolate",
    ingredients=["Cocoa Mass", "Sugar", "Cocoa Butter"]
)
user = UserProfile(user_id="u001", allergies=["peanuts"])
allergy_check = AllergyResult(user_id="u001", product_id="p101", is_safe=True)

analysis = execute_full_analysis(prod, user, allergy_check, catalog=[])
print("Health Score:", analysis.health_score)
print("Summary:", analysis.summary)
print("Key Takeaways:", analysis.key_takeaways)

# 4. Test RAGEvaluator Metrics
from ai_engine.evaluator import RAGEvaluator

evaluator = RAGEvaluator()
print("CER Score:", evaluator.calculate_cer("Palm Oil", "Palm Ol"))
print("RAGAS Metrics:", evaluator.evaluate_response(
    query="palm oil",
    response=analysis.summary,
    context="Palm oil has saturated fats."
))
