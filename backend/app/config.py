import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


class Settings:
    """Application configuration loaded from environment variables."""

    # LLM provider: groq (remote) | ollama (local / company GPU)
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    # Ollama (self-hosted Gemma 4 on company GPU later)
    gemma_model: str = os.getenv("GEMMA_MODEL", "gemma4:e2b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Groq (remote inference for now)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    groq_request_timeout: float = float(os.getenv("GROQ_REQUEST_TIMEOUT", "120"))
    cors_origins: list[str] = [
        origin.strip().rstrip("/")
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    cors_origin_pattern: str | None = os.getenv("CORS_ORIGIN_PATTERN") or None
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = _env_int("PORT", 8000)
    ollama_request_timeout: float = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", "120")
    )
    ollama_retry_attempts: int = _env_int("OLLAMA_RETRY_ATTEMPTS", 3)
    ollama_retry_delay: float = float(os.getenv("OLLAMA_RETRY_DELAY", "1"))
    startup_validate_ollama: bool = _env_bool(
        "STARTUP_VALIDATE_OLLAMA",
        default=os.getenv("ENVIRONMENT", "development").lower() == "production",
    )
    app_title: str = "Gemma Chatbot API"
    app_version: str = "1.0.0"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
