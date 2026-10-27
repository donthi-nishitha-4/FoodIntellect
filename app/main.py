# pyrefly: ignore[missing-import]
from fastapi import FastAPI, Request
# pyrefly: ignore[missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore[missing-import]
from fastapi.templating import Jinja2Templates

from app.db.session import engine, Base

from app.api.routes_ingest import router as ingest_router
from app.api.routes_analyze import router as analyze_router
from app.api.routes_user import router as user_router
# pyrefly: ignore[missing-import]
from app.api.routes_chat import router as chat_router


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

app.include_router(chat_router, prefix="/api")
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
        request=request,
        name="index.html",
        context={}
    )


@app.get("/result")
def result_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={}
    )


@app.get("/profile")
def profile_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={}
    )


@app.get("/history")
def history_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={}
    )
