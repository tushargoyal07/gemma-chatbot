from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.models.chat import ChatMessage, UsageStats


class LLMService(ABC):
    """Abstract interface for language model providers.

    Future providers (e.g. OpenAI, local RAG-augmented pipelines) can
    implement this interface without changing the API layer.
    """

    @abstractmethod
    async def generate_response(self, messages: list[ChatMessage]) -> ChatMessage:
        """Generate an assistant reply from the conversation history."""

    @abstractmethod
    async def stream_response(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[tuple[str, UsageStats | None]]:
        """Yield token fragments, then a final tuple with empty content and usage."""
        yield "", None
