from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.dependencies.auth import CurrentUser
from app.schemas.rag import DocumentIndexResponse
from app.services.chunking_service import chunking_service
from app.services.document_service import document_service
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import (
    vector_store_service,
)

router = APIRouter()


@router.post(
    "/documents/upload",
    response_model=DocumentIndexResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> DocumentIndexResponse:
    file_path = None

    try:
        file_path = await document_service.save_pdf(file)

        extracted_text, page_count = (
            document_service.extract_text(file_path)
        )

        chunks = chunking_service.split_text(
            extracted_text
        )

        embeddings = (
            embedding_service.create_document_embeddings(
                chunks
            )
        )

        document_id = str(uuid4())

        vector_store_service.store_document(
            document_id=document_id,
            filename=file.filename or "unknown.pdf",
            chunks=chunks,
            embeddings=embeddings,
        )

        return DocumentIndexResponse(
            document_id=document_id,
            filename=file.filename or "unknown.pdf",
            pages=page_count,
            characters=len(extracted_text),
            chunks_created=len(chunks),
            message=(
                "PDF uploaded, extracted, chunked, "
                "embedded and indexed successfully."
            ),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "Document indexing error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document indexing failed.",
        ) from error

    finally:
        await file.close()


@router.get("/documents")
def get_documents(
    current_user: CurrentUser,
):
    try:
        documents = (
            vector_store_service.list_documents()
        )

        return {
            "documents": documents,
        }

    except Exception as error:
        print(
            "Document listing error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load indexed documents.",
        ) from error


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    current_user: CurrentUser,
):
    try:
        deleted = (
            vector_store_service.delete_document(
                document_id
            )
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        return {
            "document_id": document_id,
            "message": (
                "Document deleted successfully."
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Document deletion error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the document.",
        ) from error