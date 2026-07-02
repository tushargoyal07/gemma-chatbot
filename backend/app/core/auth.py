from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Require X-API-Key when API_KEY is configured. Skipped when unset (local dev)."""
    expected = settings.api_key.strip()
    if not expected:
        return

    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
