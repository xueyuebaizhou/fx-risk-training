from __future__ import annotations

from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from fxlab.data import DataUnavailableError

from .schemas import ReportRequest, ScenarioInput
from .service import analysis_payload, build_report, get_fx_data, market_payload

app = FastAPI(
    title="跨境汇率风险实训 API",
    version="2.0.0",
    description="为 Next.js 实训前端提供真实 USD/CNY 数据、模型、风险与报告能力。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fx-risk-training-api"}


@app.get("/api/v1/market")
def market() -> dict:
    try:
        return market_payload(get_fx_data())
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/analysis")
def analyse(params: ScenarioInput) -> dict:
    try:
        payload, _ = analysis_payload(params)
        return payload
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/reports")
def report(request: ReportRequest) -> Response:
    try:
        content, media_type, filename = build_report(request)
    except DataUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (RuntimeError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )

