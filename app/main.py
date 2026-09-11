"""
Food Intellect - FastAPI Application Entry Point (Member 3)

Main application server mounting API routers for Ingestion, Analysis, and User Profiles.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_ingest import router as ingest_router
from app.api.routes_analyze import router as analyze_router
from app.api.routes_user import router as user_router

app = FastAPI(
    title="Food Intellect API Gateway",
    description="AI-powered packaged food intelligence, allergen safety & recommendation platform.",
    version="1.0.0"
)

# CORS middleware enabling Vite + React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(analyze_router)
app.include_router(user_router)


@app.get("/")
def root():
    return {
        "app": "Food Intellect API Gateway",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
