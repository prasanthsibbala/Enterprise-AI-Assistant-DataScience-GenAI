from pydantic import BaseModel, Field


class DocumentIndexResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    characters: int
    chunks_created: int
    message: str


class DocumentQuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
    )
    document_id: str | None = None


class SourceItem(BaseModel):
    filename: str
    document_id: str
    chunk_index: int
    content: str


class DocumentQuestionResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    model: str

class IndexedDocumentItem(BaseModel):
    document_id: str
    filename: str
    chunks: int


class IndexedDocumentListResponse(BaseModel):
    documents: list[IndexedDocumentItem]
    total_documents: int


class DocumentDeleteResponse(BaseModel):
    document_id: str
    deleted_chunks: int
    message: str