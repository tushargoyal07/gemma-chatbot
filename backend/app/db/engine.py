import logging
import ssl
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import Settings
from app.db.models import Base

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None

_RAILWAY_INTERNAL_SUFFIX = ".railway.internal"


def _ensure_sqlite_parent_dir(url: str) -> None:
    if not url.startswith("sqlite"):
        return
    # sqlite+aiosqlite:///./data/chat.db -> ./data/chat.db
    path_part = url.split("///", 1)[-1]
    if path_part == ":memory:":
        return
    Path(path_part).parent.mkdir(parents=True, exist_ok=True)


def _postgres_connect_args(url: str) -> dict:
    host = (urlparse(url).hostname or "").lower()

    # Railway private network — plain TCP, no SSL.
    if host.endswith(_RAILWAY_INTERNAL_SUFFIX):
        return {}

    # Railway public proxy uses self-signed certs; verify_mode=require fails otherwise.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return {"ssl": ctx}


def get_engine(settings: Settings) -> AsyncEngine:
    global _engine
    if _engine is None:
        url = settings.database_url
        _ensure_sqlite_parent_dir(url)
        connect_args: dict = {}
        engine_kwargs: dict = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        elif url.startswith("postgresql"):
            connect_args.update(_postgres_connect_args(url))
            engine_kwargs["pool_pre_ping"] = True
        _engine = create_async_engine(
            url,
            connect_args=connect_args,
            **engine_kwargs,
        )
    return _engine


def get_session_factory(settings: Settings) -> async_sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(settings),
            expire_on_commit=False,
        )
    return _session_factory


async def init_db(settings: Settings) -> None:
    engine = get_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    parsed = urlparse(settings.database_url)
    if parsed.scheme.startswith("sqlite"):
        label = "sqlite"
    else:
        label = f"postgresql ({parsed.hostname or 'unknown'})"
    logger.info("Database tables ready (%s)", label)


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
