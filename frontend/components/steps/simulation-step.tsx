"use client";

import { Binary, Dices, FlaskConical, Waves } from "lucide-react";

import { HistogramChart, PathChart, StrategyRiskChart } from "@/components/charts";
import { Reveal } from "@/components/reveal";
import { LockedState, Metric, PageHeader, SectionHeading } from "@/components/ui";
import { formatCny, formatPercent } from "@/lib/format";
import { useTraining } from "@/lib/training-context";

export function SimulationStep() {
  const { analysis, inputs } = useTraining();
  if (!analysis) return <LockedState />;
  const metrics = analysis.strategy.selected;

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 05 / MONTE CARLO"
          title="不是预测一条未来，而是看见一万个可能。"
          description="用真实历史收益率估计的漂移和 GARCH 条件波动率，生成固定随机种子的教学情景，所有策略始终在同一批终值上比较。"
          aside={<div className="header-symbol"><Dices size={25} /><span>FIXED SEED<br /><b>{analysis.simulation.seed}</b></span></div>}
        />
      </Reveal>

      <Reveal delay={70}>
        <section className="simulation-banner">
          <div><FlaskConical size={21} /><span><strong>模型教学情景</strong>不是对真实未来行情的承诺</span></div>
          <ul>
            <li>{inputs.termDays} 个自然日</li>
            <li>{analysis.simulation.tradingDays} 个交易日</li>
            <li>{analysis.simulation.pathsCount.toLocaleString("zh-CN")} 条完整路径</li>
            <li>展示 {Math.min(18, analysis.simulation.displayPathsCount)} 条</li>
          </ul>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading eyebrow="PATH SCENARIOS" title="每条线都是同一个起点下的另一种未来。" note="图表仅抽样；下方全部指标使用完整 10,000 条路径" />
          <article className="chart-panel"><div className="panel-title"><Waves size={18} /><div><h3>USD/CNY 路径情景</h3><p>交易日 × 模型汇率</p></div></div><PathChart paths={analysis.simulation.paths} /></article>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading title="终值与收入分布" note={`当前策略：${formatPercent(inputs.hedgeRatio, 0)} 远期套保`} />
          <div className="two-chart-grid">
            <article className="chart-panel"><div className="panel-title"><Binary size={18} /><div><h3>到期 USD/CNY 分布</h3><p>纵轴为模拟次数</p></div></div><HistogramChart data={analysis.simulation.terminalHistogram} reference={analysis.simulation.terminalMean} referenceLabel={`均值 ${analysis.simulation.terminalMean.toFixed(4)}`} /></article>
            <article className="chart-panel"><div className="panel-title"><Binary size={18} /><div><h3>人民币收入分布</h3><p>单位：万元 · 纵轴为模拟次数</p></div></div><HistogramChart data={analysis.simulation.incomeHistogram} reference={metrics.q05Income / 10_000} referenceLabel={`5%分位 ${(metrics.q05Income / 10_000).toFixed(2)}万`} unit="万" /></article>
          </div>
          <div className="metric-grid metric-grid-4">
            <Metric label="平均收入" value={formatCny(metrics.meanIncome)} meta="完整情景均值" />
            <Metric label="5% 分位数收入" value={formatCny(metrics.q05Income)} meta="尾部现金流" tone="coral" />
            <Metric label="收入标准差" value={formatCny(metrics.incomeStd)} meta="现金流波动" tone="violet" />
            <Metric label="VaR / CFaR" value={`${formatCny(metrics.var95)} / ${formatCny(metrics.cfar95)}`} meta="两种参照口径" tone="green" />
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading eyebrow="ONE SAMPLE, FIVE STRATEGIES" title="套保比例越高，尾部风险如何收窄。" />
          <div className="comparison-layout">
            <article className="chart-panel"><StrategyRiskChart data={analysis.strategies} /></article>
            <div className="strategy-table-wrap">
              <table className="strategy-table">
                <thead><tr><th>比例</th><th>平均收入</th><th>CFaR₉₅</th><th>Risk Ratio</th><th>风险下降</th></tr></thead>
                <tbody>{analysis.strategies.map((row) => <tr key={row.ratio} className={row.ratio === inputs.hedgeRatio ? "is-current" : ""}><td><strong>{formatPercent(row.ratio, 0)}</strong></td><td>{formatCny(row.meanIncome)}</td><td>{formatCny(row.cfar95)}</td><td>{formatPercent(row.riskRatio, 2)}</td><td>{formatPercent(row.riskReduction)}</td></tr>)}</tbody>
              </table>
            </div>
          </div>
        </section>
      </Reveal>
    </div>
  );
}
