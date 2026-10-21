import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Food Intellect"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./food_intellect.db"
)

UPLOAD_FOLDER = "uploads"