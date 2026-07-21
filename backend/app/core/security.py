from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


class TokenDecodeError(Exception):
    """Raised when a JWT token cannot be decoded."""


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    additional_claims: dict[str, Any] | None = None,
) -> tuple[str, int]:
    expire_minutes = (
        settings.jwt_access_token_expire_minutes
    )

    expires_in_seconds = expire_minutes * 60

    issued_at = datetime.now(timezone.utc)

    expires_at = issued_at + timedelta(
        minutes=expire_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": issued_at,
        "exp": expires_at,
        "type": "access",
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_in_seconds


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm
            ],
        )
    except JWTError as error:
        raise TokenDecodeError(
            "Invalid or expired access token."
        ) from error

    if payload.get("type") != "access":
        raise TokenDecodeError(
            "Invalid token type."
        )

    return payload