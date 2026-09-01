import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database.connection import init_pgvector

if __name__ == "__main__":
    if init_pgvector():
        print("[SUCCESS] FoodIntellect DB initialized with pgvector and pg_trgm support.")
    else:
        print("[ERROR] DB init failed.")
