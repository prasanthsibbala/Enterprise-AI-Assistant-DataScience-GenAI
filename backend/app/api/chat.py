from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.core.config import settings
from app.dependencies.auth import CurrentUser
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.gemini_service import (
    gemini_service,
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    try:
        answer = (
            gemini_service.generate_response(
                request.message
            )
        )

        return ChatResponse(
            answer=answer,
            model=settings.gemini_model,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "General chat error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI service is temporarily "
                "unavailable."
            ),
        ) from error