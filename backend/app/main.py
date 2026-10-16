from fastapi import FastAPI

from app.config import ENV
from app.routers import kitchen, orders

# D-22: 인증 스텁(auth_stub)은 dev/test 전용. 다른 ENV에서는 애플리케이션을 띄우지 않는다.
# JWT(B2)가 들어오면 이 가드는 지운다.
if ENV not in ("dev", "test"):
    raise RuntimeError(
        f"ENV={ENV!r}에서는 시작할 수 없습니다. 인증 스텁은 dev/test 전용입니다 (D-22, JWT는 B2)."
    )

app = FastAPI(title="식당 운영 웹앱 API", version="0.1.0")

app.include_router(orders.router, prefix="/api/v1")
app.include_router(kitchen.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
