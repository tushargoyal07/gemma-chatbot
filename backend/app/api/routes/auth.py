from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.auth import (
    AuthStatusResponse,
    VerifyAccessCodeRequest,
    VerifyAccessCodeResponse,
)

router = APIRouter(prefix="/auth")


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(
    settings: Settings = Depends(get_settings),
) -> AuthStatusResponse:
    return AuthStatusResponse(
        access_code_required=bool(settings.access_code.strip()),
    )


@router.post("/verify", response_model=VerifyAccessCodeResponse)
async def verify_access_code(
    body: VerifyAccessCodeRequest,
    settings: Settings = Depends(get_settings),
) -> VerifyAccessCodeResponse:
    expected = settings.access_code.strip()
    if not expected:
        return VerifyAccessCodeResponse()

    if body.code != expected:
        raise HTTPException(status_code=401, detail="Invalid access code.")

    return VerifyAccessCodeResponse()
