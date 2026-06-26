import asyncio
import contextlib
import logging
import sys
import time
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import api_router
from app.config import Settings, get_settings
from app.core.exceptions import LLMServiceError
from app.services.llm.ollama_client import check_ollama_health

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


def validate_startup_config(settings: Settings) -> None:
    if not settings.ollama_base_url.strip():
        logger.error("OLLAMA_BASE_URL is required but not set")
        sys.exit(1)


async def validate_ollama_at_startup(settings: Settings) -> None:
    try:
        health = await check_ollama_health(settings)
        logger.info(
            "Ollama startup check passed: model=%s loaded=%s",
            health["model"],
            health["model_loaded"],
        )
    except LLMServiceError as exc:
        level = logging.ERROR if settings.startup_validate_ollama else logging.WARNING
        logger.log(
            level,
            "Ollama startup validation failed (use GET /health/model to check): %s",
            exc.message,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    validate_startup_config(settings)
    # Run after startup so /health is available immediately for Railway.
    validation_task = asyncio.create_task(validate_ollama_at_startup(settings))
    yield
    validation_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await validation_task


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_pattern,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Gemma Chatbot API is running"}
