"""D-22/B-05: ENV·JWT_SECRET이 없으면 애플리케이션이 시작되지 않는다.

이 테스트는 app.config를 임포트하지 않은 새 서브프로세스에서 환경변수를 제어해야
정확하다(이미 임포트된 모듈은 캐시되어 재검증이 안 됨). subprocess로 격리한다.
"""
import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def _run_import_config(env: dict[str, str], unset: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    full_env = {**os.environ, **env}
    for key in unset:
        full_env.pop(key, None)
    return subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=BACKEND_DIR,
        env=full_env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_missing_env_and_jwt_secret_fails_to_start():
    """ENV, JWT_SECRET을 모두 비우면 기본값 "prod"로 떨어져 시작이 막힌다."""
    env = {"DATABASE_URL": "postgresql+psycopg2://x:x@localhost:5432/x"}
    result = _run_import_config(env, unset=("ENV", "JWT_SECRET"))
    assert result.returncode != 0, "ENV/JWT_SECRET 없이도 시작됨 (D-22 위반)"
    assert "JWT_SECRET" in result.stderr


def test_dev_env_without_jwt_secret_starts_with_default():
    env = {
        "DATABASE_URL": "postgresql+psycopg2://x:x@localhost:5432/x",
        "ENV": "dev",
    }
    result = _run_import_config(env, unset=("JWT_SECRET",))
    assert result.returncode == 0, result.stderr


def test_prod_env_with_jwt_secret_starts():
    env = {
        "DATABASE_URL": "postgresql+psycopg2://x:x@localhost:5432/x",
        "ENV": "prod",
        "JWT_SECRET": "a-real-secret",
    }
    result = _run_import_config(env)
    assert result.returncode == 0, result.stderr
