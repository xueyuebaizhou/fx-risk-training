"use client";

import type { CSSProperties } from "react";
import { EqualApproximately, Lock, SlidersHorizontal, TrendingDown } from "lucide-react";

import { Reveal } from "@/components/reveal";
import { LockedState, Metric, PageHeader, PrimaryButton, SectionHeading } from "@/components/ui";
import { formatCny, formatPercent, formatRate, formatUsd } from "@/lib/format";
import { useTraining } from "@/lib/training-context";

const quickRatios = [0, 0.25, 0.5, 0.75, 1];

export function StrategyStep() {
  const { analysis, inputs, updateInput, setActiveStep } = useTraining();
  if (!analysis) return <LockedState />;
  const metrics = analysis.strategy.selected;

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 04 / HEDGE SANDBOX"
          title="把不确定性，变成一个可以调节的比例。"
          description="在同一批到期汇率情景上连续调整远期套保比例，观察锁定金额、现金流尾部风险与收益分布如何变化。"
          aside={<div className="header-symbol"><SlidersHorizontal size={25} /><span>LIVE SANDBOX<br /><b>10,000 SCENARIOS</b></span></div>}
        />
      </Reveal>

      <Reveal delay={70}>
        <section className="strategy-console surface-lavender">
          <div className="strategy-control">
            <div className="control-heading"><span className="mini-label">HEDGE RATIO</span><strong>{formatPercent(inputs.hedgeRatio, 0)}</strong></div>
            <input
              className="range-input"
              aria-label="远期套保比例"
              type="range"
              min={0}
              max={100}
              step={1}
              value={inputs.hedgeRatio * 100}
              onChange={(event) => updateInput("hedgeRatio", Number(event.target.value) / 100)}
              style={{ "--range-progress": `${inputs.hedgeRatio * 100}%` } as CSSProperties}
            />
            <div className="range-scale"><span>0% 保留全部浮动</span><span>100% 完全锁定</span></div>
            <div className="quick-ratios">
              {quickRatios.map((ratio) => <button key={ratio} className={inputs.hedgeRatio === ratio ? "is-active" : ""} onClick={() => updateInput("hedgeRatio", ratio)}>{ratio * 100}%</button>)}
            </div>
          </div>
          <label className="forward-control">
            <span>教学案例远期报价 F</span>
            <div><input aria-label="远期汇率" type="number" min={1} max={20} step={0.01} value={inputs.forwardRate} onChange={(event) => updateInput("forwardRate", Number(event.target.value))} /><em>CNY/USD</em></div>
            <small>不是实时银行报价，不包含手续费、授信或保证金成本</small>
          </label>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading title="策略结果" note="输入改变后在浏览器内基于同一批 10,000 个终值即时重算" />
          <div className="metric-grid metric-grid-4">
            <Metric label="锁定美元金额" value={formatUsd(analysis.strategy.lockedAmount)} meta={`${formatPercent(inputs.hedgeRatio, 0)} × A`} tone="violet" />
            <Metric label="平均人民币收入" value={formatCny(metrics.meanIncome)} meta="策略情景均值" />
            <Metric label="CFaR₉₅" value={formatCny(metrics.cfar95)} meta={`Risk Ratio ${formatPercent(metrics.riskRatio, 2)}`} tone="coral" />
            <Metric label="CFaR 风险下降" value={formatPercent(analysis.strategy.cfarReduction)} meta="相对完全不套保" tone="green" />
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="strategy-story surface-ink">
          <div className="formula-visual">
            <span>R<sub>hedged</sub></span>
            <EqualApproximately size={28} />
            <strong>A [ hF + (1 − h)S<sub>T</sub> ]</strong>
          </div>
          <div className="strategy-story-copy">
            <span className="mini-label">WHAT CHANGED</span>
            <h2>{inputs.hedgeRatio === 1 ? "人民币收入已被远期报价完全锁定。" : inputs.hedgeRatio === 0 ? "当前策略保留全部汇率浮动。" : `${formatPercent(inputs.hedgeRatio, 0)} 的美元应收不再随到期汇率波动。`}</h2>
            <p>在情景平均到期汇率 {formatRate(analysis.simulation.terminalMean)} 下，远期相对完全不套保的平均收入差额为 {formatCny(analysis.strategy.meanHedgeEffect)}。</p>
            <div className="strategy-principle"><Lock size={18} /><span>套保目标是降低现金流波动与尾部风险；放弃部分有利汇率变动收益，不等同于策略“亏损”。</span></div>
          </div>
          <TrendingDown className="strategy-watermark" size={180} strokeWidth={0.7} aria-hidden="true" />
        </section>
      </Reveal>

      <div className="section-action"><PrimaryButton onClick={() => setActiveStep("simulation")}>查看蒙特卡洛情景</PrimaryButton></div>
    </div>
  );
}
