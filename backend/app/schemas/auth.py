from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class UserRegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if len(cleaned_value) < 2:
            raise ValueError(
                "Full name must contain at least 2 characters."
            )

        return cleaned_value

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        if not any(
            character.isupper()
            for character in value
        ):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not any(
            character.islower()
            for character in value
        ):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not any(
            character.isdigit()
            for character in value
        ):
            raise ValueError(
                "Password must contain at least one number."
            )

        return value


class UserLoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: EmailStr,
    ) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class AuthMessageResponse(BaseModel):
    message: str