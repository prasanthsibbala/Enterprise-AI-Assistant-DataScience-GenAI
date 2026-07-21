from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    content_type: str
    pages: int
    characters: int
    message: str
