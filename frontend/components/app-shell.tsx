"use client";

import type { ComponentType } from "react";
import {
  BarChart3,
  BookOpenCheck,
  ChartNoAxesCombined,
  ChevronRight,
  FlaskConical,
  Gauge,
  SlidersHorizontal,
} from "lucide-react";

import { Brand } from "@/components/brand";
import { CaseStep } from "@/components/steps/case-step";
import { ExposureStep } from "@/components/steps/exposure-step";
import { ModelStep } from "@/components/steps/model-step";
import { ReportStep } from "@/components/steps/report-step";
import { SimulationStep } from "@/components/steps/simulation-step";
import { StrategyStep } from "@/components/steps/strategy-step";
import { useTraining } from "@/lib/training-context";
import type { StepId } from "@/lib/types";

const steps = [
  { id: "case" as const, number: "01", title: "实训案例", short: "案例", icon: BookOpenCheck },
  { id: "model" as const, number: "02", title: "数据与 AI 模型", short: "模型", icon: ChartNoAxesCombined },
  { id: "exposure" as const, number: "03", title: "风险敞口与预警", short: "敞口", icon: Gauge },
  { id: "strategy" as const, number: "04", title: "避险策略沙盘", short: "策略", icon: SlidersHorizontal },
  { id: "simulation" as const, number: "05", title: "蒙特卡洛情景", short: "情景", icon: FlaskConical },
  { id: "report" as const, number: "06", title: "策略评价与报告", short: "报告", icon: BarChart3 },
];

const views: Record<StepId, ComponentType> = {
  case: CaseStep,
  model: ModelStep,
  exposure: ExposureStep,
  strategy: StrategyStep,
  simulation: SimulationStep,
  report: ReportStep,
};

export function AppShell() {
  const { activeStep, setActiveStep, market, loadingMarket, analysis, error } = useTraining();
  const index = steps.findIndex((step) => step.id === activeStep);
  const ActiveView = views[activeStep];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-head">
          <Brand />
        </div>
        <div className="nav-caption">实训工作流</div>
        <nav className="step-nav" aria-label="实训步骤">
          {steps.map((step, stepIndex) => {
            const Icon = step.icon;
            const complete = stepIndex < index || (analysis && stepIndex > 0);
            return (
              <button key={step.id} onClick={() => setActiveStep(step.id)} className={activeStep === step.id ? "is-active" : ""}>
                <span className="nav-icon"><Icon size={18} strokeWidth={1.8} /></span>
                <span className="nav-copy"><small>{step.number}</small><strong>{step.title}</strong></span>
                {complete && <i className="nav-complete" />}
                {activeStep === step.id && <ChevronRight className="nav-arrow" size={16} />}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-foot">
          <div className="data-status">
            <span className={loadingMarket ? "is-loading" : market ? "" : "is-error"} />
            <div><strong>{market?.pair || "USD/CNY"}</strong><small>{loadingMarket ? "正在读取真实数据" : market ? `${market.mode} · ${market.endDate}` : "真实数据不可用"}</small></div>
          </div>
          <p>模型情景仅用于教学，不构成投资或交易建议。</p>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div className="mobile-brand"><Brand compact /></div>
          <div className="breadcrumb"><span>跨境汇率风险实训</span><ChevronRight size={14} /><strong>{steps[index].title}</strong></div>
          <div className="topbar-right">
            <div className="progress-copy"><span>实训进度</span><strong>{index + 1} / 6</strong></div>
            <div className="progress-track"><span style={{ width: `${((index + 1) / steps.length) * 100}%` }} /></div>
          </div>
        </header>

        <nav className="mobile-steps" aria-label="移动端实训步骤">
          {steps.map((step) => <button key={step.id} className={activeStep === step.id ? "is-active" : ""} onClick={() => setActiveStep(step.id)}><span>{step.number}</span>{step.short}</button>)}
        </nav>

        {error && !market && <div className="global-error"><strong>真实数据未连接。</strong><span>{error}</span> 系统已停止模型计算，不会用模拟历史行情代替。</div>}

        <main className="main-content" key={activeStep}>
          <ActiveView />
        </main>
      </div>
    </div>
  );
}
