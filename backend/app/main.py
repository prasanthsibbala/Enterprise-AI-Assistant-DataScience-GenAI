from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.auth import (
    router as auth_router,
)
from app.api.chat import (
    router as chat_router,
)
from app.api.documents import (
    router as documents_router,
)
from app.api.document_chat import router as document_chat_router
from app.api.reports import (
    router as reports_router,
)
from app.api.fraud import router as fraud_router
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import models before create_all.
from app.models import User  # noqa: F401


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise AI Assistant with "
        "document RAG, Gemini, ChromaDB, "
        "fraud prediction, model metrics, GenAI explanations, and JWT authentication."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://enterprise-ai-assistant-data-scienc.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    documents_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    chat_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    document_chat_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    reports_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    fraud_router,
    prefix=settings.api_v1_prefix,
)


@app.get(
    "/",
    tags=["Application"],
)
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get(
    f"{settings.api_v1_prefix}/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.environment,
    }