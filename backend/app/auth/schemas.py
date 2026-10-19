from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Role


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class UserCreateIn(BaseModel):
    username: str
    password: str
    role: Role


class UserUpdateIn(BaseModel):
    password: str | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: str
    username: str
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class TableOut(BaseModel):
    id: str
    table_no: int
    qr_token: str
    qr_issued_at: datetime

    model_config = {"from_attributes": True}


class TableCreateIn(BaseModel):
    table_no: int


class TableSessionIn(BaseModel):
    qr_token: str


class TableSessionOut(BaseModel):
    table_session_token: str
    expires_at: datetime


class QrReissueOut(BaseModel):
    qr_token: str


class StreamTokenOut(BaseModel):
    token: str
    expires_at: datetime
