from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_api_key
from app.db.session import get_session
from app.models.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    CreateConversationResponse,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations")


def get_conversation_service(
    session: AsyncSession = Depends(get_session),
) -> ConversationService:
    return ConversationService(session)


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    _: None = Depends(verify_api_key),
    service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationSummary]:
    return await service.list_conversations()


@router.post("", response_model=CreateConversationResponse, status_code=201)
async def create_conversation(
    body: CreateConversationRequest = CreateConversationRequest(),
    _: None = Depends(verify_api_key),
    service: ConversationService = Depends(get_conversation_service),
) -> CreateConversationResponse:
    return await service.create_conversation(title=body.title)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    _: None = Depends(verify_api_key),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationDetail:
    conversation = await service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    _: None = Depends(verify_api_key),
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    deleted = await service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
