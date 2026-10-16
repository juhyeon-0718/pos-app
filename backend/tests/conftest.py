"""
Q2 계약 테스트 공통 픽스처.

PostgreSQL 18 DATABASE_URL이 없으면 전체 스킵합니다 (D-21).
테스트 격리: 각 테스트 전후 관련 테이블 TRUNCATE.
동시성 TC(TC-01)는 실제 커밋이 필요하므로 트랜잭션 롤백 방식이 아닌 TRUNCATE 방식을 씁니다.

실행 방법 (PostgreSQL 설치 후):
    cd C:/juehyeon/pos-app-back/backend
    pytest tests/contract/ -v
"""
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient


def _load_dotenv() -> None:
    """python-dotenv 없이 backend/.env를 파싱해 os.environ에 설정한다."""
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()

_DATABASE_URL = os.environ.get("DATABASE_URL", "")

if "postgresql" not in _DATABASE_URL:
    pytest.skip(
        "PostgreSQL DATABASE_URL이 필요합니다 (D-21). "
        "backend/.env에 DATABASE_URL을 설정하거나 환경변수로 전달하세요.",
        allow_module_level=True,
    )

# skip 이후 import — config.py가 이미 로드된 경우를 대비해 강제 교체
os.environ["DATABASE_URL"] = _DATABASE_URL

import app.models_all  # noqa: F401, E402 — Base.metadata에 모든 테이블 등록
from app.db import Base  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

_engine = create_engine(_DATABASE_URL)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)

# 테스트 실행 전 1회: 테이블이 없으면 생성
# (B1 전환 완료 후에는 alembic upgrade head로 대체한다)
Base.metadata.create_all(_engine)

_TRUNCATE = text("""
    TRUNCATE TABLE
        order_items,
        orders,
        stock_movements,
        idempotency_keys
    RESTART IDENTITY CASCADE
""")

# ingredients/menus/recipes는 seed가 직접 관리하므로 별도 TRUNCATE
_TRUNCATE_SEED = text("""
    TRUNCATE TABLE
        recipes,
        menus,
        ingredients
    RESTART IDENTITY CASCADE
""")


@pytest.fixture(autouse=True)
def clean_tables():
    """각 테스트 전후 모든 관련 테이블을 비운다."""
    with _engine.begin() as conn:
        conn.execute(_TRUNCATE)
        conn.execute(_TRUNCATE_SEED)
    yield
    with _engine.begin() as conn:
        conn.execute(_TRUNCATE)
        conn.execute(_TRUNCATE_SEED)


@pytest.fixture
def db():
    """테스트용 DB 세션. seed 삽입 및 결과 검증에 사용한다."""
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """FastAPI TestClient (동기). 스레드에서 공유 가능."""
    with TestClient(fastapi_app, raise_server_exceptions=False) as c:
        yield c
