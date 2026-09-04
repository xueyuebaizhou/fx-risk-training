import type { AnalysisData, MarketData, ScenarioInputs } from "@/lib/types";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `请求失败（${response.status}）`;
    try {
      const body = await response.json();
      if (body?.detail) message = String(body.detail);
    } catch {
      // Preserve the status-based message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function fetchMarket(): Promise<MarketData> {
  return readJson<MarketData>(await fetch(`${API_BASE}/api/v1/market`, { cache: "no-store" }));
}

export async function requestAnalysis(inputs: ScenarioInputs): Promise<AnalysisData> {
  return readJson<AnalysisData>(
    await fetch(`${API_BASE}/api/v1/analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: inputs.amount,
        term_days: inputs.termDays,
        budget_rate: inputs.budgetRate,
        forward_rate: inputs.forwardRate,
        hedge_ratio: inputs.hedgeRatio,
      }),
    }),
  );
}

export async function requestReport(
  inputs: ScenarioInputs,
  finalRatio: number,
  decisionReason: string,
  format: "pdf" | "html",
): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/v1/reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      amount: inputs.amount,
      term_days: inputs.termDays,
      budget_rate: inputs.budgetRate,
      forward_rate: inputs.forwardRate,
      hedge_ratio: inputs.hedgeRatio,
      final_ratio: finalRatio,
      decision_reason: decisionReason,
      format,
    }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || `报告生成失败（${response.status}）`);
  }
  return response.blob();
}
