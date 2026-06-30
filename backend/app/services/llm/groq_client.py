import logging

import httpx

from app.config import Settings
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

GROQ_API_BASE = "https://api.groq.com/openai/v1"


def _groq_headers(settings: Settings) -> dict[str, str]:
    if not settings.groq_api_key.strip():
        raise LLMServiceError(
            message="GROQ_API_KEY is not set.",
            status_code=503,
        )
    return {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }


def classify_groq_error(exc: Exception, *, status_code: int | None = None) -> LLMServiceError:
    if isinstance(exc, httpx.TimeoutException):
        return LLMServiceError(
            message="Groq request timed out.",
            status_code=504,
        )

    if isinstance(exc, (httpx.ConnectError, httpx.NetworkError)):
        return LLMServiceError(
            message="Groq is unavailable. Check your network connection.",
            status_code=503,
        )

    if status_code == 401:
        return LLMServiceError(
            message="Invalid Groq API key.",
            status_code=503,
        )

    if status_code == 429:
        return LLMServiceError(
            message="Groq rate limit exceeded. Try again shortly.",
            status_code=429,
        )

    if status_code == 404:
        return LLMServiceError(
            message=f"Model '{exc}' is not available on Groq.",
            status_code=503,
        )

    message = str(exc) if str(exc) else "Groq request failed."
    return LLMServiceError(message=message, status_code=status_code or 503)


def parse_groq_error_response(response: httpx.Response) -> LLMServiceError:
    detail = "Groq request failed."
    try:
        body = response.json()
        error = body.get("error", {})
        if isinstance(error, dict) and error.get("message"):
            detail = error["message"]
    except Exception:
        pass

    return classify_groq_error(Exception(detail), status_code=response.status_code)


async def check_groq_health(settings: Settings) -> dict:
    """Verify Groq API key and that the configured model is available."""
    url = f"{GROQ_API_BASE}/models"
    timeout = httpx.Timeout(settings.groq_request_timeout)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=_groq_headers(settings))
    except LLMServiceError:
        raise
    except Exception as exc:
        logger.exception("Groq health check failed")
        raise classify_groq_error(exc) from exc

    if response.status_code != 200:
        raise parse_groq_error_response(response)

    model_ids = {item["id"] for item in response.json().get("data", [])}
    model_available = settings.groq_model in model_ids

    if not model_available:
        raise LLMServiceError(
            message=f"Model '{settings.groq_model}' is not available on Groq.",
            status_code=503,
        )

    return {
        "status": "healthy",
        "provider": "groq",
        "model": settings.groq_model,
        "model_loaded": True,
    }
