from pathlib import Path
from uuid import uuid4

import pymupdf
from fastapi import UploadFile


class DocumentService:
    allowed_content_types = {
        "application/pdf",
    }

    def __init__(self) -> None:
        self.upload_directory = Path("uploads")
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    def validate_pdf(self, file: UploadFile) -> None:
        if file.content_type not in self.allowed_content_types:
            raise ValueError("Only PDF files are currently supported.")

        if not file.filename:
            raise ValueError("Uploaded file must have a filename.")

        if not file.filename.lower().endswith(".pdf"):
            raise ValueError("File extension must be .pdf.")

    async def save_pdf(self, file: UploadFile) -> Path:
        self.validate_pdf(file)

        unique_filename = f"{uuid4()}_{file.filename}"
        file_path = self.upload_directory / unique_filename

        file_content = await file.read()

        if not file_content:
            raise ValueError("Uploaded PDF is empty.")

        max_file_size = 10 * 1024 * 1024

        if len(file_content) > max_file_size:
            raise ValueError("PDF size cannot exceed 10 MB.")

        file_path.write_bytes(file_content)

        return file_path

    def extract_text(self, file_path: Path) -> tuple[str, int]:
        try:
            document = pymupdf.open(file_path)

            page_texts: list[str] = []

            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text", sort=True).strip()

                page_texts.append(
                    f"\n--- Page {page_number} ---\n{text}"
                )

            page_count = document.page_count
            document.close()

            full_text = "\n".join(page_texts).strip()

            if not full_text:
                raise ValueError(
                    "No readable text was found in the PDF."
                )

            return full_text, page_count

        except pymupdf.FileDataError as error:
            raise ValueError(
                "The uploaded file is not a valid PDF."
            ) from error


document_service = DocumentService()