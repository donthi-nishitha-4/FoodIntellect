from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.session import engine, Base

from app.api.routes_ingest import router as ingest_router
from app.api.routes_analyze import router as analyze_router
from app.api.routes_user import router as user_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Food Intellect API",
    description="AI Powered Food Intelligence and Alternatives Recommendation Platform",
    version="1.0"
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# Templates
templates = Jinja2Templates(
    directory="app/templates"
)


# API routes
app.include_router(
    ingest_router,
    prefix="/api"
)

app.include_router(
    analyze_router,
    prefix="/api"
)

app.include_router(
    user_router,
    prefix="/api"
)


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@app.get("/result")
def result_page(request: Request):

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request
        }
    )


@app.get("/profile")
def profile_page(request: Request):

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request
        }
    )


@app.get("/history")
def history_page(request: Request):

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request
        }
    )