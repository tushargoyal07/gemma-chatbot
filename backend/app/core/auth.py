from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _expected_api_key(settings: Settings) -> str:
    """ACCESS_CODE takes precedence over API_KEY when both are set."""
    return settings.access_code.strip() or settings.api_key.strip()


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Require X-API-Key when ACCESS_CODE or API_KEY is configured."""
    expected = _expected_api_key(settings)
    if not expected:
        return

    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing access code.")
