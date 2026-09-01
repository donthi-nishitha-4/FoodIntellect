# src/utils/config.py
from pathlib import Path
from pydantic_settings import BaseSettings
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    FOOD_CORPUS_DIR: Path = DATA_DIR / "food_corpus"
    RESULTS_DIR: Path = PROJECT_ROOT / "experiments" / "results"
    RETRIEVAL_DISTANCE_THRESHOLD: float = 0.5

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5445))
    DB_USER: str = os.getenv("DB_USER", "rag_app_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "rag_password")
    DB_NAME: str = os.getenv("DB_NAME", "rag_bootcamp")
    
    # ==================== LLM PROVIDERS ====================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    CEREBRAS_API_KEY: Optional[str] = os.getenv("CEREBRAS_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # ==================== SECURITY ====================
    MAX_LATENCY_MS: int = 5000

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True

settings = Settings()
