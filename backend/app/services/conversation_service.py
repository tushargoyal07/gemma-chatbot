import logging

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConversationRecord, MessageRecord
from app.models.chat import ChatMessage, UsageStats
from app.models.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationResponse,
)

logger = logging.getLogger(__name__)

TITLE_MAX_LEN = 60


def _title_from_message(content: str) -> str:
    single_line = " ".join(content.strip().split())
    if len(single_line) <= TITLE_MAX_LEN:
        return single_line or "New Chat"
    return f"{single_line[: TITLE_MAX_LEN - 1]}…"


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_conversations(self, limit: int = 50) -> list[ConversationSummary]:
        result = await self._session.execute(
            select(ConversationRecord)
            .order_by(ConversationRecord.updated_at.desc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return [
            ConversationSummary(id=row.id, title=row.title, updated_at=row.updated_at)
            for row in rows
        ]

    async def create_conversation(self, title: str = "New Chat") -> CreateConversationResponse:
        record = ConversationRecord(title=title)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return CreateConversationResponse(
            id=record.id,
            title=record.title,
            created_at=record.created_at,
        )

    async def get_conversation(self, conversation_id: str) -> ConversationDetail | None:
        result = await self._session.execute(
            select(ConversationRecord).where(ConversationRecord.id == conversation_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            return None

        messages_result = await self._session.execute(
            select(MessageRecord)
            .where(MessageRecord.conversation_id == conversation_id)
            .order_by(MessageRecord.created_at)
        )
        message_rows = messages_result.scalars().all()

        return ConversationDetail(
            id=record.id,
            title=record.title,
            created_at=record.created_at,
            updated_at=record.updated_at,
            messages=[
                ChatMessage(role=row.role, content=row.content)  # type: ignore[arg-type]
                for row in message_rows
            ],
        )

    async def delete_conversation(self, conversation_id: str) -> bool:
        result = await self._session.execute(
            delete(ConversationRecord).where(ConversationRecord.id == conversation_id)
        )
        await self._session.commit()
        return result.rowcount > 0

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        usage: UsageStats | None = None,
    ) -> None:
        record = MessageRecord(
            conversation_id=conversation_id,
            role=role,
            content=content,
            usage=usage.model_dump() if usage else None,
        )
        self._session.add(record)
        await self._session.execute(
            update(ConversationRecord)
            .where(ConversationRecord.id == conversation_id)
            .values(updated_at=func.now())
        )

        if role == "user":
            await self._maybe_set_title(conversation_id, content)

        await self._session.commit()

    async def _maybe_set_title(self, conversation_id: str, content: str) -> None:
        result = await self._session.execute(
            select(ConversationRecord).where(ConversationRecord.id == conversation_id)
        )
        record = result.scalar_one_or_none()
        if record is None or record.title != "New Chat":
            return
        record.title = _title_from_message(content)
