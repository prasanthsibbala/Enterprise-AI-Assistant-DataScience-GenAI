from google import genai

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import (
    vector_store_service,
)


class RagService:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        self.model = settings.gemini_model

    def answer_question(
        self,
        question: str,
        document_id: str | None = None,
    ) -> tuple[str, list[dict]]:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        query_embedding = (
            embedding_service.create_query_embedding(
                question
            )
        )

        matches = vector_store_service.search_documents(
            query_embedding=query_embedding,
            document_id=document_id,
            limit=3,
        )

        if not matches:
            raise ValueError(
                "No indexed document content was found."
            )

        context_sections: list[str] = []

        for index, match in enumerate(
            matches,
            start=1,
        ):
            metadata = match["metadata"]
            content = match["content"]

            context_sections.append(
                (
                    f"Source {index}\n"
                    f"Filename: "
                    f"{metadata.get('filename', 'unknown')}\n"
                    f"Chunk: "
                    f"{metadata.get('chunk_index', 0)}\n"
                    f"Content:\n{content}"
                )
            )

        context = "\n\n".join(context_sections)

        prompt = f"""
You are an enterprise document assistant.

Answer the user's question using only the provided
document context.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present in the context, say:
   "The uploaded documents do not contain enough
   information to answer this question."
3. Keep the answer clear and concise.
4. Do not invent names, numbers, dates, or facts.
5. Mention the source filename when useful.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        answer = response.text

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty answer."
            )

        return answer.strip(), matches


rag_service = RagService()