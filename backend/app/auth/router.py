from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.dependencies import get_current_user, require_owner
from app.auth.models import Table, User
from app.auth.schemas import (
    LoginIn,
    LoginOut,
    QrReissueOut,
    StreamTokenOut,
    TableCreateIn,
    TableOut,
    TableSessionIn,
    TableSessionOut,
    UserCreateIn,
    UserOut,
    UserUpdateIn,
)
from app.auth.security import STREAM_TOKEN_TTL, TABLE_SESSION_TOKEN_TTL
from app.db import get_db
from app.models.base import utcnow

router = APIRouter(tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


def _table_out(table: Table) -> TableOut:
    return TableOut.model_validate(table)


@router.post("/auth/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    try:
        token, role = service.login(db, username=body.username, password=body.password)
    except service.Unauthorized as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from None
    return LoginOut(access_token=token, role=role)


@router.post("/stream/token", response_model=StreamTokenOut)
def issue_stream_token(current=Depends(get_current_user)):
    token = service.issue_stream_token(user_id=current.user_id, role=current.role.value)
    return StreamTokenOut(token=token, expires_at=utcnow() + STREAM_TOKEN_TTL)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _owner=Depends(require_owner)):
    return [_user_out(u) for u in service.list_users(db)]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreateIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        user = service.create_user(db, username=body.username, password=body.password, role=body.role.value)
    except service.Conflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return _user_out(user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, body: UserUpdateIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        user = service.update_user(
            db,
            user_id,
            password=body.password,
            role=body.role.value if body.role else None,
            is_active=body.is_active,
        )
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _user_out(user)


@router.get("/tables", response_model=list[TableOut])
def list_tables(db: Session = Depends(get_db), _owner=Depends(require_owner)):
    return [_table_out(t) for t in service.list_tables(db)]


@router.post("/tables", response_model=TableOut, status_code=201)
def create_table(body: TableCreateIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    table = service.create_table(db, table_no=body.table_no)
    return _table_out(table)


@router.post("/tables/{table_id}/session", response_model=TableSessionOut)
def create_table_session(table_id: str, body: TableSessionIn, db: Session = Depends(get_db)):
    try:
        token = service.create_table_session(db, table_id=table_id, qr_token=body.qr_token)
    except service.Unauthorized as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from None
    return TableSessionOut(table_session_token=token, expires_at=utcnow() + TABLE_SESSION_TOKEN_TTL)


@router.post("/tables/{table_id}/qr/reissue", response_model=QrReissueOut)
def reissue_table_qr(table_id: str, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        table = service.reissue_qr(db, table_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return QrReissueOut(qr_token=table.qr_token)
