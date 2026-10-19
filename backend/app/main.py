from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.inventory.router import router as inventory_router
from app.menu.router import router as menu_router
from app.routers import kitchen, orders

app = FastAPI(title="식당 운영 웹앱 API", version="0.2.0")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(menu_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(kitchen.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
