from pydantic import BaseModel


class TimeseriesPoint(BaseModel):
    ts: int
    value: float


class TimeseriesSeries(BaseModel):
    name: str
    points: list[TimeseriesPoint]


class TimeseriesResponse(BaseModel):
    metric: str
    range_minutes: int
    step_seconds: int
    series: list[TimeseriesSeries]
