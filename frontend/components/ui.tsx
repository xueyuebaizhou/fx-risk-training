import type { ReactNode } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";

import { useTraining } from "@/lib/training-context";
import type { StepId } from "@/lib/types";

export function PageHeader({
  kicker,
  title,
  description,
  aside,
}: {
  kicker: string;
  title: string;
  description: string;
  aside?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div>
        <span className="eyebrow">{kicker}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {aside && <div className="page-header-aside">{aside}</div>}
    </header>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  note,
}: {
  eyebrow?: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <span>{eyebrow}</span>}
        <h2>{title}</h2>
      </div>
      {note && <p>{note}</p>}
    </div>
  );
}

export function Metric({
  label,
  value,
  meta,
  tone = "default",
}: {
  label: string;
  value: ReactNode;
  meta?: ReactNode;
  tone?: "default" | "green" | "violet" | "coral";
}) {
  return (
    <article className={`metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {meta && <small>{meta}</small>}
    </article>
  );
}

export function PrimaryButton({
  children,
  onClick,
  disabled = false,
  kind = "dark",
  type = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  kind?: "dark" | "light" | "accent";
  type?: "button" | "submit";
}) {
  return (
    <button className={`primary-button button-${kind}`} onClick={onClick} disabled={disabled} type={type}>
      <span>{children}</span>
      <ArrowRight size={17} strokeWidth={2} />
    </button>
  );
}

export function LockedState({ target = "model" }: { target?: StepId }) {
  const { setActiveStep, analysisNeedsRefresh } = useTraining();
  return (
    <div className="locked-state">
      <div className="lock-icon"><LockKeyhole size={22} /></div>
      <span className="eyebrow">RESULTS LOCKED</span>
      <h2>{analysisNeedsRefresh ? "期限已经改变，需要重新生成情景。" : "先运行真实数据模型，再进入本模块。"}</h2>
      <p>系统不会使用预设指标或模拟历史行情填充这里的结果。</p>
      <PrimaryButton onClick={() => setActiveStep(target)}>前往数据与 AI 模型</PrimaryButton>
    </div>
  );
}

export function DataSourceNote() {
  const { market, loadingMarket } = useTraining();
  return (
    <div className="source-note">
      <span className={`source-beacon ${loadingMarket ? "is-loading" : ""}`} />
      <div>
        <strong>{loadingMarket ? "正在读取真实行情" : market?.mode || "真实行情不可用"}</strong>
        <p>
          {market
            ? `${market.source} · ${market.startDate} 至 ${market.endDate} · ${market.observations.toLocaleString("zh-CN")} 个观测`
            : "数据读取失败时停止计算，不生成随机历史行情。"}
        </p>
      </div>
    </div>
  );
}
