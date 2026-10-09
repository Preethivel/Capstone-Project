"""Gemini-backed educational assistant service."""

import logging
import os

logger = logging.getLogger(__name__)


class AIServiceError(RuntimeError):
    """Expected failure while contacting the configured AI provider."""


def generate_learning_response(message: str, context: str = "") -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AIServiceError("AI service is not configured")

    try:
        from google import genai
    except ImportError as exc:
        logger.exception("Gemini SDK is not installed")
        raise AIServiceError("AI service is unavailable") from exc

    prompt = (
       "You are LearnVerse AI, an educational learning assistant. Do not say hello or greet the user on every response. Answer directly and helpfully. "
        "Help learners understand lessons, explain concepts simply, summarize material, "
        "provide examples, create practice questions, and answer course-related questions. "
        "Be accurate, encouraging, concise, and clearly state when a question is outside "
        "the available learning context.\n\n"
        f"Learning context:\n{context or 'No specific course context was provided.'}\n\n"
        f"Learner question:\n{message}"
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
        )
        answer = getattr(response, "text", None)
        if not answer or not answer.strip():
            raise AIServiceError("AI service returned an empty response")
        return answer.strip()
    except AIServiceError:
        raise
    except Exception as exc:
        logger.warning("Gemini request failed: %s", type(exc).__name__)
        raise AIServiceError("AI service request failed") from exc
