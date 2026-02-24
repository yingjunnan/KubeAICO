from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzer.adapters import NoopLLMAdapter
from app.analyzer.rules import RuleEngine
from app.collector.kubernetes import KubernetesCollector
from app.collector.prometheus import PrometheusCollector
from app.core.config import get_settings
from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_db
from app.repository.ai_task import AITaskRepository
from app.repository.audit import AuditRepository
from app.repository.user import UserRepository
from app.service.ai import AIService
from app.service.alerts import AlertService
from app.service.audit import AuditService
from app.service.metrics import MetricsService
from app.service.overview import OverviewService
from app.service.resources import ResourceService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@lru_cache
def get_audit_repository() -> AuditRepository:
    return AuditRepository()


@lru_cache
def get_ai_task_repository() -> AITaskRepository:
    return AITaskRepository()


@lru_cache
def get_prometheus_collector() -> PrometheusCollector:
    return PrometheusCollector(get_settings())


@lru_cache
def get_k8s_collector() -> KubernetesCollector:
    return KubernetesCollector(get_settings())


@lru_cache
def get_alert_service() -> AlertService:
    return AlertService(get_k8s_collector(), get_prometheus_collector())


@lru_cache
def get_overview_service() -> OverviewService:
    return OverviewService(get_k8s_collector(), get_prometheus_collector(), get_alert_service())


@lru_cache
def get_metrics_service() -> MetricsService:
    return MetricsService(get_prometheus_collector())


@lru_cache
def get_resource_service() -> ResourceService:
    return ResourceService(get_k8s_collector(), get_audit_repository())


@lru_cache
def get_audit_service() -> AuditService:
    return AuditService(get_audit_repository())


@lru_cache
def get_ai_service() -> AIService:
    settings = get_settings()
    return AIService(
        task_repo=get_ai_task_repository(),
        rule_engine=RuleEngine(),
        llm_adapter=NoopLLMAdapter(),
        llm_enabled=settings.enable_llm,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        username = decode_token(token)
    except ValueError as exc:
        raise credentials_exception from exc

    repo = get_user_repository()
    user = await repo.get_by_username(db, username)
    if not user or not user.is_active:
        raise credentials_exception

    return user
