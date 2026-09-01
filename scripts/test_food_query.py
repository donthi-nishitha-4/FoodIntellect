import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import ask_food_rag

def run_test_queries():
    test_questions = [
        "What is lecithin and why is it used in food?",
        "Is milk powder a common allergen?",
        "What is the function of sodium benzoate?",
        "What is maltodextrin and does it affect blood sugar?",
        "What are the health considerations of high fructose corn syrup?"
    ]
    
    print("===============================================================", flush=True)
    print("       FOODINTELLECT MVP: RAG BASELINE VERIFICATION TEST       ", flush=True)
    print("===============================================================\n", flush=True)
    
    for idx, q in enumerate(test_questions, 1):
        print(f"---------------------------------------------------------------", flush=True)
        print(f" ❓ Question {idx}: {q}", flush=True)
        print(f"---------------------------------------------------------------", flush=True)
        res = ask_food_rag(q, tenant_id="foodintellect", search_type="hybrid")
        
        print(f"🤖 LLM Provider Used : {res.get('provider', 'N/A')}", flush=True)
        print(f"📦 Chunks Retrieved : {len(res.get('retrieved_chunks', []))}", flush=True)
        print(f"💡 LLM Answer       :\n{res.get('answer')}\n", flush=True)
        
    print("===============================================================", flush=True)
    print(" [SUCCESS] All 5 Food RAG Verification Queries Completed!", flush=True)
    print("===============================================================", flush=True)

if __name__ == "__main__":
    run_test_queries()
