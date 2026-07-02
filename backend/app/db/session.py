from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.engine import get_session_factory


async def get_session(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        yield session
