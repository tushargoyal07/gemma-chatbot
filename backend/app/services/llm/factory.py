from app.config import Settings
from app.services.llm.base import LLMService
from app.services.llm.groq_service import GroqService
from app.services.llm.ollama_service import OllamaService


def create_llm_service(settings: Settings) -> LLMService:
    provider = settings.llm_provider.lower()
    if provider == "groq":
        return GroqService(settings)
    if provider == "ollama":
        return OllamaService(settings)
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Use 'groq' or 'ollama'."
    )
