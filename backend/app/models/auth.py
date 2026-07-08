from pydantic import BaseModel, Field


class VerifyAccessCodeRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class AuthStatusResponse(BaseModel):
    access_code_required: bool


class VerifyAccessCodeResponse(BaseModel):
    ok: bool = True
