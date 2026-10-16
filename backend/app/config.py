"""
pos-app 백엔드 설정.
DATABASE_URL은 .env에서만 읽는다 (커밋/채팅에 실제 접속 문자열을 남기지 않는다).
개발/테스트/운영 모두 PostgreSQL 18을 쓴다 (D-10 기술 스택, D-21 개발·테스트 DB, 16→18 변경).
ENV는 dev/test/prod 중 하나. 인증 스텁(auth_stub)은 dev/test에서만 켜지며,
다른 값이면 애플리케이션이 시작되지 않는다 (D-22).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# backend/.env를 로드한다. 이미 설정된 환경변수(예: CI, 쉘 export)가 있으면 덮어쓰지 않는다
# (override=False가 기본값).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ENV = os.environ.get("ENV", "dev")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL 환경변수가 필요합니다. backend/.env.example을 참고해 backend/.env를 만드세요 "
        "(PostgreSQL만 지원, SQLite 기본값은 D-21로 제거됨)."
    )

# SEED=42 고정 (D-12, 재현 가능한 테스트 데이터)
SEED = int(os.environ.get("SEED", "42"))
