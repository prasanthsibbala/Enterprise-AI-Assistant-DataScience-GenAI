from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import UserRegisterRequest


class AuthService:
    @staticmethod
    def get_user_by_email(
        database: Session,
        email: str,
    ) -> User | None:
        normalized_email = email.strip().lower()

        statement = select(User).where(
            User.email == normalized_email
        )

        return database.scalar(statement)

    @staticmethod
    def get_user_by_id(
        database: Session,
        user_id: int,
    ) -> User | None:
        return database.get(User, user_id)

    @staticmethod
    def create_user(
        database: Session,
        request: UserRegisterRequest,
    ) -> User:
        existing_user = (
            AuthService.get_user_by_email(
                database,
                request.email,
            )
        )

        if existing_user:
            raise ValueError(
                "A user with this email already exists."
            )

        user = User(
            full_name=request.full_name.strip(),
            email=request.email.strip().lower(),
            hashed_password=hash_password(
                request.password
            ),
            role="analyst",
            is_active=True,
        )

        try:
            database.add(user)
            database.commit()
            database.refresh(user)
        except IntegrityError as error:
            database.rollback()

            raise ValueError(
                "A user with this email already exists."
            ) from error
        except Exception:
            database.rollback()
            raise

        return user

    @staticmethod
    def authenticate_user(
        database: Session,
        email: str,
        password: str,
    ) -> User | None:
        user = AuthService.get_user_by_email(
            database,
            email,
        )

        if user is None:
            return None

        password_is_valid = verify_password(
            password,
            user.hashed_password,
        )

        if not password_is_valid:
            return None

        if not user.is_active:
            return None

        return user


auth_service = AuthService()