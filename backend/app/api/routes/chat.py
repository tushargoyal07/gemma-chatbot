import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.auth import verify_api_key
from app.core.exceptions import LLMServiceError
from app.db.session import get_session
from app.models.chat import ChatRequest, ChatResponse, UsageStats
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.services.llm.factory import create_llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    return ChatService(llm_service=create_llm_service(settings))


def get_conversation_service(
    session: AsyncSession = Depends(get_session),
) -> ConversationService:
    return ConversationService(session)


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def _persist_exchange(
    conversation_service: ConversationService,
    conversation_id: str,
    user_content: str,
    assistant_content: str,
    usage: UsageStats | None,
) -> None:
    try:
        await conversation_service.add_message(
            conversation_id, "user", user_content
        )
        await conversation_service.add_message(
            conversation_id, "assistant", assistant_content, usage=usage
        )
    except Exception:
        logger.exception("Failed to persist chat for conversation %s", conversation_id)


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    _: None = Depends(verify_api_key),
    chat_service: ChatService = Depends(get_chat_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> StreamingResponse:
    user_message = request.messages[-1]
    conversation_id = request.conversation_id

    async def event_generator():
        assistant_content = ""
        usage: UsageStats | None = None
        yield _sse_event({"type": "start"})
        try:
            async for fragment, usage_stats in chat_service.stream_chat(request.messages):
                if fragment:
                    assistant_content += fragment
                    yield _sse_event({"type": "token", "content": fragment})
                if usage_stats is not None:
                    usage = usage_stats
                    yield _sse_event({"type": "done", "usage": usage_stats.model_dump()})
        except LLMServiceError as exc:
            yield _sse_event({"type": "error", "message": exc.message})
            return

        if conversation_id and assistant_content.strip():
            await _persist_exchange(
                conversation_service,
                conversation_id,
                user_message.content,
                assistant_content,
                usage,
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _: None = Depends(verify_api_key),
    chat_service: ChatService = Depends(get_chat_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    user_message = request.messages[-1]
    try:
        assistant_message = await chat_service.chat(request.messages)
    except LLMServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    if request.conversation_id:
        await _persist_exchange(
            conversation_service,
            request.conversation_id,
            user_message.content,
            assistant_message.content,
            None,
        )

    return ChatResponse(message=assistant_message)
