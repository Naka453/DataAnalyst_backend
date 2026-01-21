from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class Domain(str, Enum):
    export = "export"
    import_ = "import"  # "import" is python keyword


class Calc(str, Enum):
    month_value = "month_value"            # тухайн сарын дүн (sum)
    ytd = "ytd"                            # он эхнээс (sum)
    yoy = "yoy"                            # өмнөх оны мөн үе (month vs prev year same month)
    timeseries_month = "timeseries_month"  # жил дотор сар сараар (series)
    year_total = "year_total"              # тухайн жилийн нийлбэр
    avg_months = "avg_months"              # сүүлийн N сарын дундаж (month_value-ийн average)
    avg_years = "avg_years"                # сүүлийн N жилийн дундаж (year_total-ийн average)
    weighted_price = "weighted_price"      # sum(amountUSD)/sum(quantity)


class Metric(str, Enum):
    amountUSD = "amountUSD"
    quantity = "quantity"
    weighted_price = "weighted_price"


class TimeMonth(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)


class TimeYear(BaseModel):
    year: int = Field(..., ge=1900, le=2100)


TimeField = Union[str, TimeMonth, TimeYear]  # "latest" | {year,month} | {year}


class Intent(BaseModel):
    domain: Domain = Domain.export
    calc: Calc = Calc.month_value
    metric: Metric = Metric.amountUSD
    time: TimeField = "latest"

    # avg_months / avg_years үед ашиглах цонх
    window: int = Field(default=3, ge=1, le=60)

    filters: Dict[str, Any] = Field(default_factory=dict)
    topn: int = Field(default=50, ge=1, le=500)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    topn: int = Field(default=50, ge=1, le=500)