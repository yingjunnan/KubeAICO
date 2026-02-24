from fastapi import APIRouter

from app.api.routes import (
    ai_router,
    alerts_router,
    audit_router,
    auth_router,
    metrics_router,
    overview_router,
    resources_router,
)

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(overview_router)
api_router.include_router(metrics_router)
api_router.include_router(resources_router)
api_router.include_router(alerts_router)
api_router.include_router(audit_router)
api_router.include_router(ai_router)
