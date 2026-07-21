from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        examples=["Explain enterprise AI assistant in simple terms."],
    )


class ChatResponse(BaseModel):
    answer: str
    model: str