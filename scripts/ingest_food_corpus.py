import os
import sys
import gc
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database.connection import init_pgvector, load_documents, build_vector_index

def ingest_food_corpus(data_dir=None):
    if data_dir is None:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'food_corpus'))
        
    if not os.path.exists(data_dir):
        print(f"[ERROR] Food corpus directory {data_dir} does not exist.")
        return False

    print("[INFO] Initializing FoodIntellect pgvector database schema...")
    if not init_pgvector():
        print("[ERROR] Database initialization failed.")
        return False
        
    print("[INFO] Loading embedding model: all-MiniLM-L6-v2...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    print(f"[INFO] Found {len(files)} food knowledge files in corpus.")
    
    all_docs = []
    file_names = []
    
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                all_docs.append(content)
                file_names.append(file_name)
                
    if not all_docs:
        print("[WARN] No documents found to ingest.")
        return False
        
    print(f"[INFO] Generating embeddings for {len(all_docs)} food documents...")
    embeddings = embed_model.encode(all_docs, show_progress_bar=False).tolist()
    
    print("[INFO] Ingesting documents into pgvector (tenant_id='foodintellect', entity_type='food_ingredient')...")
    success = load_documents(
        documents=all_docs,
        embeddings=embeddings,
        entity_type="food_ingredient",
        tenant_id="foodintellect"
    )
    
    if success:
        print("[INFO] Building ivfflat vector index...")
        build_vector_index()
        print(f"[SUCCESS] Ingested {len(all_docs)} food knowledge documents successfully!")
        return True
    else:
        print("[ERROR] Ingestion failed.")
        return False

if __name__ == "__main__":
    ingest_food_corpus()
