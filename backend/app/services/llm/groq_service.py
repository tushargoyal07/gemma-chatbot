import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.config import Settings
from app.core.exceptions import LLMServiceError
from app.models.chat import ChatMessage, UsageStats
from app.services.llm.base import LLMService
from app.services.llm.groq_client import (
    GROQ_API_BASE,
    _groq_headers,
    classify_groq_error,
    parse_groq_error_response,
)

logger = logging.getLogger(__name__)

MAX_COMPLETION_TOKENS = 1024


class GroqService(LLMService):
    """Groq Cloud LLM service (OpenAI-compatible API)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _to_api_messages(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
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
                message="Groq returned an invalid or empty response.",
                status_code=502,
            )

        return ChatMessage(role="assistant", content=content)

    async def stream_response(
        self, messages: list[ChatMessage]
    ) -> AsyncIterator[tuple[str, UsageStats | None]]:
        payload = {
            "model": self._settings.groq_model,
            "messages": self._to_api_messages(messages),
            "stream": True,
            "max_tokens": MAX_COMPLETION_TOKENS,
            "stream_options": {"include_usage": True},
        }
        url = f"{GROQ_API_BASE}/chat/completions"
        timeout = httpx.Timeout(self._settings.groq_request_timeout)

        saw_content = False
        usage: UsageStats | None = None

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=_groq_headers(self._settings),
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        await response.aread()
                        raise parse_groq_error_response(response)

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue

                        data = line[6:].strip()
                        if not data or data == "[DONE]":
                            continue

                        chunk = json.loads(data)
                        choices = chunk.get("choices") or []
                        if choices:
                            delta = choices[0].get("delta") or {}
                            fragment = delta.get("content")
                            if fragment:
                                saw_content = True
                                yield fragment, None

                        chunk_usage = chunk.get("usage")
                        if chunk_usage:
                            prompt_tokens = chunk_usage.get("prompt_tokens") or 0
                            completion_tokens = chunk_usage.get("completion_tokens") or 0
                            usage = UsageStats(
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                                total_tokens=chunk_usage.get("total_tokens")
                                or prompt_tokens + completion_tokens,
                            )
                            logger.info(
                                "tokens prompt=%s completion=%s",
                                prompt_tokens,
                                completion_tokens,
                            )
        except LLMServiceError:
            raise
        except Exception as exc:
            logger.exception("Groq stream failed")
            raise classify_groq_error(exc) from exc

        if not saw_content and usage is None:
            raise LLMServiceError(
                message="Groq returned an invalid or empty response.",
                status_code=502,
            )

        yield "", usage
