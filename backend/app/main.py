import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import api_router
from app.config import Settings, get_settings

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


def log_startup_config(settings: Settings) -> None:
    if not settings.ollama_base_url.strip():
        logger.warning("OLLAMA_BASE_URL is not set — chat will fail until configured")
    else:
        logger.info(
            "Starting with ollama_base_url=%s model=%s environment=%s",
            settings.ollama_base_url,
            settings.gemma_model,
            settings.environment,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    log_startup_config(settings)
    yield


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
