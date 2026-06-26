from collections.abc import AsyncIterator

from app.models.chat import ChatMessage, UsageStats
from app.services.llm.base import LLMService

MAX_HISTORY_MESSAGES = 20


class ChatService:
    """Orchestrates chat requests.

    This layer is the extension point for future RAG, embeddings, and
    document retrieval. Context augmentation can be added here before
    messages are passed to the LLM provider.
    """

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def chat(self, messages: list[ChatMessage]) -> ChatMessage:
        prepared_messages = self._prepare_messages(messages)
        return await self._llm_service.generate_response(prepared_messages)

    async def stream_chat(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[tuple[str, UsageStats | None]]:
        prepared_messages = self._prepare_messages(messages)
        async for item in self._llm_service.stream_response(prepared_messages):
            yield item

    def _prepare_messages(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        # Future: inject retrieved context from ChromaDB / embeddings here.
        if len(messages) <= MAX_HISTORY_MESSAGES:
            return messages
        return messages[-MAX_HISTORY_MESSAGES:]
