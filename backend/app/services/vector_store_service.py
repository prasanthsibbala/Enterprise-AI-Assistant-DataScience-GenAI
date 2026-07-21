from typing import Any

import chromadb

from app.core.config import settings


class VectorStoreService:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={
                "description": (
                    "Enterprise AI Assistant document chunks"
                )
            },
        )

    def store_document(
        self,
        document_id: str,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings count must match."
            )

        ids = [
            f"{document_id}_chunk_{index}"
            for index in range(len(chunks))
        ]

        metadatas: list[dict[str, Any]] = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search_documents(
        self,
        query_embedding: list[float],
        document_id: str | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        where_filter = None

        if document_id:
            where_filter = {
                "document_id": document_id
            }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = (
            results.get("documents", [[]])[0] or []
        )
        metadatas = (
            results.get("metadatas", [[]])[0] or []
        )
        distances = (
            results.get("distances", [[]])[0] or []
        )

        matches: list[dict[str, Any]] = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            matches.append(
                {
                    "content": document,
                    "metadata": metadata or {},
                    "distance": distance,
                }
            )

        return matches

    def count_chunks(self) -> int:
        return self.collection.count()

    def list_documents(self) -> list[dict[str, Any]]:
        results = self.collection.get(
            include=["metadatas"],
        )

        metadatas = results.get("metadatas") or []

        document_map: dict[str, dict[str, Any]] = {}

        for metadata in metadatas:
            if not metadata:
                continue

            document_id = str(
                metadata.get("document_id", "")
            )

            if not document_id:
                continue

            if document_id not in document_map:
                document_map[document_id] = {
                    "document_id": document_id,
                    "filename": metadata.get(
                        "filename",
                        "unknown.pdf",
                    ),
                    "chunks": 0,
                }

            document_map[document_id]["chunks"] += 1

        return list(document_map.values())

    def delete_document(
        self,
        document_id: str,
    ) -> int:
        existing = self.collection.get(
            where={
                "document_id": document_id,
            },
            include=["metadatas"],
        )

        ids = existing.get("ids") or []

        if not ids:
            return 0

        self.collection.delete(
            ids=ids,
        )

        return len(ids)


vector_store_service = VectorStoreService()