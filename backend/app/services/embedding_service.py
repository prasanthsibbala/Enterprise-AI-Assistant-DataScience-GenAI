from google import genai
from google.genai import types

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = (
            settings.gemini_embedding_model
        )

    def create_document_embeddings(
        self,
        chunks: list[str],
    ) -> list[list[float]]:
        if not chunks:
            raise ValueError(
                "Chunks are required for embedding."
            )

        embeddings: list[list[float]] = []

        for chunk in chunks:
            cleaned_chunk = chunk.strip()

            if not cleaned_chunk:
                continue

            response = (
                self.client.models.embed_content(
                    model=self.model,
                    contents=cleaned_chunk,
                    config=types.EmbedContentConfig(
                        task_type=(
                            "RETRIEVAL_DOCUMENT"
                        ),
                    ),
                )
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini did not return an embedding."
                )

            embeddings.append(
                list(
                    response.embeddings[
                        0
                    ].values
                )
            )

        if not embeddings:
            raise RuntimeError(
                "No valid document embeddings were created."
            )

        return embeddings

    def create_query_embedding(
        self,
        query: str,
    ) -> list[float]:
        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError(
                "Query cannot be empty."
            )

        response = (
            self.client.models.embed_content(
                model=self.model,
                contents=cleaned_query,
                config=types.EmbedContentConfig(
                    task_type=(
                        "RETRIEVAL_QUERY"
                    ),
                ),
            )
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini did not return a query embedding."
            )

        return list(
            response.embeddings[0].values
        )


embedding_service = EmbeddingService()