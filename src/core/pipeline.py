import sys
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.core.database.connection import retrieve_similar, retrieve_hybrid
from .llm import query_llm

TOP_K = 10
FINAL_K = 3

# ---- SETUP EMBEDDING & RERANKING MODELS ----
try:
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    print("[INFO] FoodIntellect Embed & Rerank Models loaded successfully.")
except Exception as e:
    print(f"[ERROR] Model load failed: {e}")
    sys.exit(1)

def ask_food_rag(query, tenant_id="foodintellect", search_type="hybrid"):
    """
    Core FoodIntellect RAG pipeline.
    Returns: query, retrieved_chunks, context, answer, chunk_ids, sources
    """
    if not query or not isinstance(query, str) or not query.strip():
        return {
            "query": query,
            "retrieved_chunks": [],
            "context": "",
            "answer": "[ERROR] Invalid or empty query",
            "chunk_ids": [],
            "sources": []
        }
        
    query = query.strip()
    
    try:
        query_embedding = embed_model.encode([query])[0].tolist()

        if search_type == "hybrid":
            results = retrieve_hybrid(query, query_embedding, tenant_id=tenant_id, k=TOP_K)
        else:
            results = retrieve_similar(query_embedding, tenant_id=tenant_id, k=TOP_K)
        
        if not results:
            return {
                "query": query,
                "retrieved_chunks": [],
                "context": "",
                "answer": "I could not find relevant food or ingredient information in the knowledge base.",
                "chunk_ids": [],
                "sources": []
            }
            
        top_docs = [r[1] for r in results]
        chunk_ids = [str(r[0]) for r in results]
        
    except Exception as e:
        return {
            "query": query,
            "retrieved_chunks": [],
            "context": "",
            "answer": f"[ERROR] Retrieval failed: {e}",
            "chunk_ids": [],
            "sources": []
        }

    # Cross-Encoder Reranking
    try:
        pairs = [(query, doc) for doc in top_docs]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(scores, top_docs, chunk_ids), reverse=True)
        final_docs = [doc for _, doc, _ in ranked[:FINAL_K]]
        final_chunk_ids = [cid for _, _, cid in ranked[:FINAL_K]]
    except Exception as e:
        final_docs = top_docs[:FINAL_K]
        final_chunk_ids = chunk_ids[:FINAL_K]
        
    combined_context = "\n\n---\n\n".join(final_docs)
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are FoodIntellect, an expert AI assistant specializing in food ingredients, nutrition, "
                "preservatives, and dietary health. Answer the user's question accurately using ONLY the provided context. "
                "If the information is missing from the context, state clearly that it is not covered in the knowledge base."
            )
        },
        {"role": "user", "content": f"Food Knowledge Context:\n{combined_context}\n\nQuestion: {query}"}
    ]
    
    answer, provider = query_llm(messages)
    
    return {
        "query": query,
        "retrieved_chunks": final_docs,
        "context": combined_context,
        "answer": answer,
        "provider": provider,
        "chunk_ids": final_chunk_ids,
        "sources": [{"chunk_id": cid, "text": doc} for cid, doc in zip(final_chunk_ids, final_docs)]
    }
