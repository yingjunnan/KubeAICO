from app.api.routes.ai import router as ai_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.audit import router as audit_router
from app.api.routes.clusters import router as clusters_router
from app.api.routes.auth import router as auth_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.overview import router as overview_router
from app.api.routes.resources import router as resources_router

__all__ = [
    "auth_router",
    "overview_router",
    "metrics_router",
    "resources_router",
    "alerts_router",
    "audit_router",
    "clusters_router",
    "ai_router",
]
