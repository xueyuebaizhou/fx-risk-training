from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from fxlab.config import (
    DEFAULT_AMOUNT,
    DEFAULT_BUDGET_RATE,
    DEFAULT_FORWARD_RATE,
    DEFAULT_HEDGE_RATIO,
    DEFAULT_TERM_DAYS,
    MAX_USDCNY_RATE,
    MIN_USDCNY_RATE,
)


class ScenarioInput(BaseModel):
    amount: float = Field(default=DEFAULT_AMOUNT, gt=0, le=1_000_000_000)
    term_days: int = Field(default=DEFAULT_TERM_DAYS, ge=1, le=730)
    budget_rate: float = Field(
        default=DEFAULT_BUDGET_RATE,
        ge=MIN_USDCNY_RATE,
        le=MAX_USDCNY_RATE,
    )
    forward_rate: float = Field(
        default=DEFAULT_FORWARD_RATE,
        ge=MIN_USDCNY_RATE,
        le=MAX_USDCNY_RATE,
    )
    hedge_ratio: float = Field(default=DEFAULT_HEDGE_RATIO, ge=0, le=1)


class ReportRequest(ScenarioInput):
    final_ratio: float = Field(default=DEFAULT_HEDGE_RATIO, ge=0, le=1)
    decision_reason: str = Field(min_length=1, max_length=500)
    format: Literal["pdf", "html"] = "pdf"

    @field_validator("decision_reason")
    @classmethod
    def reason_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("策略选择理由不能为空。")
        return cleaned

