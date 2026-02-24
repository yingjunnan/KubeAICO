from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AlertSeverity(str, Enum):
    p1 = "P1"
    p2 = "P2"
    p3 = "P3"


class AlertItem(BaseModel):
    id: str
    severity: AlertSeverity
    source: str
    title: str
    message: str
    namespace: str | None = None
    start_time: datetime
    recommendation: str


class AlertListResponse(BaseModel):
    total: int
    items: list[AlertItem]
