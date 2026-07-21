from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.core.config import settings
from app.dependencies.auth import CurrentUser
from app.schemas.rag import (
    DocumentQuestionRequest,
    DocumentQuestionResponse,
    SourceItem,
)
from app.services.rag_service import rag_service

router = APIRouter()


@router.post(
    "/chat/document",
    response_model=DocumentQuestionResponse,
    status_code=status.HTTP_200_OK,
)
def chat_with_document(
    request: DocumentQuestionRequest,
    current_user: CurrentUser,
) -> DocumentQuestionResponse:
    try:
        answer, matches = (
            rag_service.answer_question(
                question=request.question,
                document_id=request.document_id,
            )
        )

        sources = [
            SourceItem(
                filename=match["metadata"].get(
                    "filename",
                    "unknown",
                ),
                document_id=match[
                    "metadata"
                ].get(
                    "document_id",
                    "unknown",
                ),
                chunk_index=int(
                    match["metadata"].get(
                        "chunk_index",
                        0,
                    )
                ),
                content=match["content"],
            )
            for match in matches
        ]

        return DocumentQuestionResponse(
            answer=answer,
            sources=sources,
            model=settings.gemini_model,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "RAG chat error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Document question answering "
                "failed."
            ),
        ) from error