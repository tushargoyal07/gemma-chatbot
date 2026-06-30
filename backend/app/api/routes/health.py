from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.core.exceptions import LLMServiceError
from app.services.llm.groq_client import check_groq_health
from app.services.llm.ollama_client import check_ollama_health

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/health/model")
async def model_health_check(
    settings: Settings = Depends(get_settings),
) -> dict[str, str | bool]:
    try:
        if settings.llm_provider == "groq":
            return await check_groq_health(settings)
        return await check_ollama_health(settings)
    except LLMServiceError as exc:
        detail: dict[str, str | bool] = {
            "status": "unhealthy",
            "provider": settings.llm_provider,
            "error": exc.message,
        }
        if settings.llm_provider == "ollama":
            detail["ollama"] = "unreachable"
            if "not loaded" in exc.message.lower():
                detail["ollama"] = "reachable"
                detail["model"] = settings.gemma_model
                detail["model_loaded"] = False
        elif settings.llm_provider == "groq":
            detail["model"] = settings.groq_model
            detail["model_loaded"] = False
        raise HTTPException(status_code=exc.status_code, detail=detail) from exc
