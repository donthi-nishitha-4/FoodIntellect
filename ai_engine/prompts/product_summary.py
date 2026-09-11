"""
Product Summary Prompts (Member 2)

System & Human prompt templates for overall product health summary generation.
"""

PRODUCT_SUMMARY_PROMPT = """Given the product details and retrieved evidence below, summarize the health quality of the food item in 3 concise paragraphs.

PRODUCT: {product_name}
NUTRITION: {nutrition_text}
INGREDIENTS: {ingredients_text}
EVIDENCE CONTEXT: {context_text}

Provide:
1. Executive Summary
2. Key Health Pros & Cons
3. Overall Rating Recommendation
"""
