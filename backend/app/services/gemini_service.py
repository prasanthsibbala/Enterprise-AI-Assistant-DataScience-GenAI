import time

from google import genai
from google.genai.errors import ServerError

from app.core.config import settings


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model

    def generate_response(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )

                if not response.text:
                    raise ValueError("Gemini returned an empty response.")

                return response.text

            except ServerError as error:
                if attempt == max_attempts:
                    raise RuntimeError(
                        "Gemini is temporarily unavailable after 3 attempts."
                    ) from error

                time.sleep(2 ** attempt)


gemini_service = GeminiService()