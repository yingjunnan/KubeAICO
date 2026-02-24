import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import (
    get_k8s_collector,
    get_overview_service,
    get_prometheus_collector,
    get_user_repository,
)
from app.api.router import api_router
from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    user_repo = get_user_repository()
    async with AsyncSessionLocal() as db:
        await user_repo.ensure_default_admin(
            db,
            username=settings.default_admin_username,
            password=settings.default_admin_password,
        )

    yield

    await get_prometheus_collector().close()
    await get_k8s_collector().close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/overview")
async def overview_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return

    try:
        username = decode_token(token)
    except ValueError:
        await websocket.close(code=4401, reason="Invalid token")
        return

    async with AsyncSessionLocal() as db:
        user_repo = get_user_repository()
        user = await user_repo.get_by_username(db, username)
        if not user or not user.is_active:
            await websocket.close(code=4403, reason="User is not active")
            return

    await websocket.accept()

    overview_service = get_overview_service()

    try:
        while True:
            payload = await overview_service.get_cluster_summary()
            await websocket.send_json(payload.model_dump(mode="json"))
            await asyncio.sleep(settings.overview_stream_interval_seconds)
    except WebSocketDisconnect:
        return
