from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingService:
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty document text.")

        chunks = self.text_splitter.split_text(text)

        cleaned_chunks = [
            chunk.strip()
            for chunk in chunks
            if chunk and chunk.strip()
        ]

        if not cleaned_chunks:
            raise ValueError("No valid chunks were created.")

        return cleaned_chunks


chunking_service = ChunkingService()