from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database.session import get_db
from app.dependencies.auth import CurrentUser
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: UserRegisterRequest,
    database: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenResponse:
    try:
        user = auth_service.create_user(
            database,
            request,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    access_token, expires_in = (
        create_access_token(
            subject=user.email,
            additional_claims={
                "user_id": user.id,
                "role": user.role,
            },
        )
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    request: UserLoginRequest,
    database: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenResponse:
    user = auth_service.authenticate_user(
        database,
        request.email,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token, expires_in = (
        create_access_token(
            subject=user.email,
            additional_claims={
                "user_id": user.id,
                "role": user.role,
            },
        )
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_authenticated_user(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(
        current_user
    )