import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx
from ollama import AsyncClient, ResponseError

from app.config import Settings
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _ollama_headers(base_url: str) -> dict[str, str]:
    """ngrok free tier returns an interstitial unless this header is sent."""
    if "ngrok" in base_url.lower():
        return {"ngrok-skip-browser-warning": "true"}
    return {}


def create_ollama_client(settings: Settings) -> AsyncClient:
    return AsyncClient(
        host=settings.ollama_base_url,
        timeout=settings.ollama_request_timeout,
        headers=_ollama_headers(settings.ollama_base_url),
    )


def is_transient_ollama_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError)):
        return True
    if isinstance(exc, (httpx.ConnectError, httpx.NetworkError)):
        return True
    if isinstance(exc, ResponseError) and exc.status_code in {502, 503, 504}:
        return True
    return False


def classify_ollama_error(exc: Exception) -> LLMServiceError:
    if isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError)):
        return LLMServiceError(
            message="Ollama request timed out.",
            status_code=504,
        )

    if isinstance(exc, (httpx.ConnectError, httpx.NetworkError)):
        return LLMServiceError(
            message="Ollama is unavailable. Ensure it is running and reachable.",
            status_code=503,
        )

    if isinstance(exc, ResponseError):
        if exc.status_code == 404:
            return LLMServiceError(
                message="Model is not loaded. Pull the model in Ollama first.",
                status_code=503,
            )
        return LLMServiceError(
            message=str(exc.error),
            status_code=exc.status_code if exc.status_code > 0 else 503,
        )

    return LLMServiceError(
        message="Ollama is unavailable. Ensure it is running and reachable.",
        status_code=503,
    )


async def with_retry(
    settings: Settings,
    operation: Callable[[], Awaitable[T]],
    *,
    operation_name: str,
) -> T:
    attempts = max(settings.ollama_retry_attempts, 1)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except LLMServiceError:
            raise
        except Exception as exc:
            last_error = exc
            if not is_transient_ollama_error(exc) or attempt >= attempts:
                logger.exception(
                    "%s failed after %s attempt(s)",
                    operation_name,
                    attempt,
                )
                raise classify_ollama_error(exc) from exc

            delay = settings.ollama_retry_delay * attempt
            logger.warning(
                "%s failed (attempt %s/%s), retrying in %.1fs: %s",
                operation_name,
                attempt,
                attempts,
                delay,
                exc,
            )
            await asyncio.sleep(delay)

    raise classify_ollama_error(last_error or RuntimeError("Unknown Ollama error"))


async def check_ollama_health(settings: Settings) -> dict:
    """Verify Ollama connectivity and whether the configured model is loaded."""
    client = create_ollama_client(settings)
    try:
        response = await client.list()
    except Exception as exc:
        logger.exception("Ollama health check failed")
        raise classify_ollama_error(exc) from exc
    finally:
        await client.close()

    model_names = {model.model for model in response.models}
    model_loaded = settings.gemma_model in model_names

    if not model_loaded:
        raise LLMServiceError(
            message=f"Model '{settings.gemma_model}' is not loaded in Ollama.",
            status_code=503,
        )

    return {
        "status": "healthy",
        "ollama": "reachable",
        "model": settings.gemma_model,
        "model_loaded": model_loaded,
    }
