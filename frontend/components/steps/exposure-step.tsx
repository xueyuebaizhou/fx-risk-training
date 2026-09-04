"use client";

import { AlertTriangle, ArrowDown, CircleDollarSign, Gauge, ShieldAlert } from "lucide-react";

import { Reveal } from "@/components/reveal";
import { LockedState, Metric, PageHeader, SectionHeading } from "@/components/ui";
import { formatCny, formatPercent, formatRate, formatUsd } from "@/lib/format";
import { useTraining } from "@/lib/training-context";

export function ExposureStep() {
  const { analysis, inputs, market } = useTraining();
  if (!analysis) return <LockedState />;
  const risk = analysis.exposure.unhedged;
  const tone = risk.riskLevel === "高风险" ? "risk-high" : risk.riskLevel === "中风险" ? "risk-mid" : "risk-low";

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 03 / EXPOSURE"
          title="风险不是一个汇率点。"
          description="把美元应收转换成可比较的人民币现金流分布，分别观察相对当前价值的 VaR 与相对预算目标的 CFaR。"
          aside={<span className={`risk-badge ${tone}`}><span /> 企业敞口 · {risk.riskLevel}</span>}
        />
      </Reveal>

      <Reveal delay={70}>
        <section className={`risk-hero ${tone}`}>
          <div className="risk-hero-copy">
            <span className="mini-label">CASH FLOW AT RISK</span>
            <h2>{formatPercent(risk.riskRatio, 2)}</h2>
            <strong>Risk Ratio</strong>
            <p>在当前参数和 10,000 条统一教学情景下，95% CFaR 占预算人民币收入的比例。</p>
          </div>
          <div className="risk-scale">
            <div className="risk-scale-labels"><span>低风险 &lt; 2%</span><span>中风险 2%—5%</span><span>高风险 ≥ 5%</span></div>
            <div className="risk-scale-track"><span className="risk-low-zone" /><span className="risk-mid-zone" /><span className="risk-high-zone" /><i style={{ left: `${Math.min(risk.riskRatio / 0.08, 1) * 100}%` }} /></div>
            <small><AlertTriangle size={14} /> 内部教学预警规则，不代表监管、银行或金融机构统一标准</small>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading title="敞口快照" note="美元应收 · USD/CNY 下跌为不利方向" />
          <div className="metric-grid metric-grid-4">
            <Metric label="外币应收敞口" value={formatUsd(inputs.amount)} meta={`${inputs.termDays} 天后结算`} />
            <Metric label="预算人民币收入" value={formatCny(analysis.exposure.budgetIncome)} meta={`B = ${formatRate(inputs.budgetRate)}`} tone="violet" />
            <Metric label="95% VaR" value={formatCny(risk.var95)} meta="相对当前即期折算价值" tone="coral" />
            <Metric label="95% CFaR" value={formatCny(risk.cfar95)} meta="相对预算收入缺口" tone="coral" />
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section exposure-explain">
          <SectionHeading eyebrow="HOW TO READ IT" title="同一批情景，回答两个不同问题。" />
          <div className="explain-grid">
            <article><div><CircleDollarSign size={21} /></div><span>VALUE AT RISK</span><h3>VaR 看今天的价值可能损失多少。</h3><p>以当前即期汇率 {market ? formatRate(market.spotRate) : "—"} 折算的人民币价值为参照，观察汇率变动造成的尾部损失。</p><div className="formula-line">FX Lossᵢ = A × S₀ − Rᵢ</div></article>
            <article><div><ShieldAlert size={21} /></div><span>CASH FLOW AT RISK</span><h3>CFaR 看预算目标可能落空多少。</h3><p>以预算收入 {formatCny(analysis.exposure.budgetIncome)} 为参照，观察 5% 分位收入与预算之间的缺口。</p><div className="formula-line">CFaR₉₅ = max[R_budget − Q₅%(R), 0]</div></article>
            <article className="explain-direction"><div><Gauge size={21} /></div><span>EXPOSURE DIRECTION</span><h3>美元应收最怕 USD/CNY 下跌。</h3><p>相同美元兑换到更少人民币。远期套保的主要价值，是收窄这种现金流不确定性。</p><ArrowDown size={54} /></article>
          </div>
        </section>
      </Reveal>
    </div>
  );
}
