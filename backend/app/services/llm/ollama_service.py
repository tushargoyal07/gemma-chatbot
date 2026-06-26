import logging
from collections.abc import AsyncIterator

from ollama import ResponseError

from app.config import Settings
from app.core.exceptions import LLMServiceError
from app.models.chat import ChatMessage, UsageStats
from app.services.llm.base import LLMService
from app.services.llm.ollama_client import (
    classify_ollama_error,
    create_ollama_client,
    with_retry,
)

logger = logging.getLogger(__name__)

OLLAMA_OPTIONS = {
    "num_predict": 1024,
}


class OllamaService(LLMService):
    """Ollama-backed LLM service for local inference."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = create_ollama_client(settings)

    def _to_ollama_messages(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
        return [
            {"role": message.role, "content": message.content} for message in messages
        ]

    async def generate_response(self, messages: list[ChatMessage]) -> ChatMessage:
        content_parts: list[str] = []

        async for fragment, usage in self.stream_response(messages):
            if fragment:
                content_parts.append(fragment)
            if usage is not None:
                break

        content = "".join(content_parts)
        if not content:
            raise LLMServiceError(
                message="Ollama returned an invalid or empty response.",
                status_code=502,
            )

        return ChatMessage(role="assistant", content=content)

    async def _start_chat_stream(self, ollama_messages: list[dict[str, str]]):
        return await self._client.chat(
            model=self._settings.gemma_model,
            messages=ollama_messages,
            stream=True,
            think=False,
            keep_alive="30m",
            options=OLLAMA_OPTIONS,
        )

    async def stream_response(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[tuple[str, UsageStats | None]]:
        ollama_messages = self._to_ollama_messages(messages)

        try:
            stream = await with_retry(
                self._settings,
                lambda: self._start_chat_stream(ollama_messages),
                operation_name="Ollama chat",
            )
        except LLMServiceError:
            raise
        except ResponseError as exc:
            logger.exception("Ollama returned an error")
            raise classify_ollama_error(exc) from exc
        except Exception as exc:
            logger.exception("Failed to reach Ollama")
            raise classify_ollama_error(exc) from exc

        usage: UsageStats | None = None
        saw_content = False

        try:
            async for chunk in stream:
                thinking = getattr(chunk.message, "thinking", None) or ""
                fragment = chunk.message.content or thinking
                if fragment:
                    saw_content = True
                    yield fragment, None

                if chunk.done:
                    prompt_tokens = chunk.prompt_eval_count or 0
                    completion_tokens = chunk.eval_count or 0
                    usage = UsageStats(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )
                    logger.info(
                        "tokens prompt=%s completion=%s duration_ms=%.0f",
                        prompt_tokens,
                        completion_tokens,
                        (chunk.total_duration or 0) / 1_000_000,
                    )
        except Exception as exc:
            logger.exception("Ollama stream failed")
            raise classify_ollama_error(exc) from exc

        if not saw_content and usage is None:
            raise LLMServiceError(
                message="Ollama returned an invalid or empty response.",
                status_code=502,
            )

        yield "", usage
