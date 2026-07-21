from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.document_chat import (
    router as document_chat_router,
)
from app.api.documents import (
    router as documents_router,
)
from app.api.fraud_prediction import (
    router as fraud_prediction_router,
)
from app.api.reports import (
    router as reports_router,
)


api_router = APIRouter()


api_router.include_router(
    auth_router,
    tags=["Authentication"],
)

api_router.include_router(
    chat_router,
    tags=["AI Chat"],
)

api_router.include_router(
    document_chat_router,
    tags=["Document AI"],
)

api_router.include_router(
    documents_router,
    tags=["Documents"],
)

api_router.include_router(
    fraud_prediction_router,
    tags=["Fraud Machine Learning"],
)

api_router.include_router(
    reports_router,
    tags=["Reports"],
)