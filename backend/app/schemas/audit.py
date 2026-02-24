from datetime import datetime

from pydantic import BaseModel


class AuditLogItem(BaseModel):
    id: int
    user_id: int | None
    action: str
    target_kind: str
    target_name: str
    namespace: str | None
    status: str
    message: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AuditLogItem]
