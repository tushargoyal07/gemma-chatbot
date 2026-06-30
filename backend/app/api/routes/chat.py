import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.core.exceptions import LLMServiceError
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.llm.factory import create_llm_service

router = APIRouter()


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    return ChatService(llm_service=create_llm_service(settings))


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    async def event_generator():
        # Flush headers immediately so the client gets 200 OK without waiting
        # for the first Ollama token (prompt evaluation can take many seconds).
        yield _sse_event({"type": "start"})
        try:
            async for fragment, usage in chat_service.stream_chat(request.messages):
                if fragment:
                    yield _sse_event({"type": "token", "content": fragment})
                if usage is not None:
                    yield _sse_event({"type": "done", "usage": usage.model_dump()})
        except LLMServiceError as exc:
            yield _sse_event({"type": "error", "message": exc.message})

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
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        assistant_message = await chat_service.chat(request.messages)
    except LLMServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return ChatResponse(message=assistant_message)
