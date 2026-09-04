"use client";

import { useState } from "react";
import { BrainCircuit, DatabaseZap, RefreshCw, Sparkles } from "lucide-react";

import { ImportanceChart, MarketChart, ModelTestChart, VolatilityChart } from "@/components/charts";
import { Reveal } from "@/components/reveal";
import { DataSourceNote, Metric, PageHeader, PrimaryButton, SectionHeading } from "@/components/ui";
import { formatPercent, formatRate } from "@/lib/format";
import { useTraining } from "@/lib/training-context";

type ChartMode = "rate" | "returnPct" | "volatilityPct";

export function ModelStep() {
  const { market, analysis, runAnalysis, runningAnalysis, error, analysisNeedsRefresh } = useTraining();
  const [mode, setMode] = useState<ChartMode>("rate");
  const tabs: { id: ChartMode; label: string }[] = [
    { id: "rate", label: "历史汇率" },
    { id: "returnPct", label: "日对数收益率" },
    { id: "volatilityPct", label: "20 日滚动波动率" },
  ];

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 02 / DATA & AI"
          title="让真实数据先开口。"
          description="走势、特征、XGBoost 测试、GARCH 波动率和蒙特卡洛参数全部来自同一套真实 USD/CNY 日频数据。"
          aside={<div className="header-symbol"><BrainCircuit size={25} /><span>AI MODEL<br /><b>TIME-SERIES SAFE</b></span></div>}
        />
      </Reveal>

      <Reveal delay={60}>
        <DataSourceNote />
        <section className="content-section chart-section">
          <SectionHeading title="历史行情概览" note="全量历史用于回溯展示；建模使用最近五年窗口" />
          <div className="segmented-tabs" role="tablist" aria-label="历史行情图表">
            {tabs.map((tab) => <button key={tab.id} className={mode === tab.id ? "is-active" : ""} onClick={() => setMode(tab.id)} role="tab" aria-selected={mode === tab.id}>{tab.label}</button>)}
          </div>
          <div className="chart-panel">
            {market ? <MarketChart data={market.series} mode={mode} /> : <div className="chart-placeholder is-loading" />}
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="model-launch surface-ink">
          <div>
            <span className="mini-label">MODEL ESTIMATION</span>
            <h2>{analysis ? "模型结果已由真实测试集验证。" : "一次运行，建立后续全部风险情景。"}</h2>
            <p>按时间顺序 80% / 20% 划分数据，不随机打乱，不读取未来信息；完整情景固定生成 10,000 条路径。</p>
            {analysisNeedsRefresh && <div className="inline-warning">结算期限已改变，需要重新生成对应期限的路径。</div>}
            {error && <div className="inline-error">{error}</div>}
          </div>
          <PrimaryButton onClick={runAnalysis} disabled={runningAnalysis || !market} kind="light">
            {runningAnalysis ? "正在运行 GARCH 与 XGBoost…" : analysis ? "重新运行模型" : "运行模型与生成情景"}
          </PrimaryButton>
          <div className={`model-orbit ${runningAnalysis ? "is-running" : ""}`} aria-hidden="true"><Sparkles size={24} /><i /><i /><i /></div>
        </section>
      </Reveal>

      {analysis && (
        <>
          <Reveal>
            <section className="content-section">
              <SectionHeading eyebrow="VALIDATED OUTPUT" title="预测结果不是预设数字。" note={`${analysis.model.sampleStartDate} 至 ${analysis.model.sampleEndDate} · ${analysis.model.sampleSize} 个观测`} />
              <div className="prediction-grid">
                <article className="prediction-feature surface-lavender">
                  <div className="prediction-top"><span>下一交易日预测</span><b>{analysis.model.direction}</b></div>
                  <strong>{formatRate(analysis.model.predictionNextDay)}</strong>
                  <p>当前 {formatRate(analysis.model.previousRate)} · 市场波动状态 <em>{analysis.model.marketState}</em></p>
                  <div className="prediction-track"><span style={{ width: `${analysis.model.volatilityPercentile * 100}%` }} /></div>
                  <small>当前波动率位于历史 {formatPercent(analysis.model.volatilityPercentile, 0)} 分位</small>
                </article>
                <div className="metric-grid metric-grid-2">
                  <Metric label="MAE" value={analysis.model.mae.toFixed(5)} meta="真实测试集" />
                  <Metric label="RMSE" value={analysis.model.rmse.toFixed(5)} meta="真实测试集" />
                  <Metric label="方向准确率" value={formatPercent(analysis.model.directionAccuracy)} meta={`${analysis.model.testSize} 个测试样本`} tone="green" />
                  <Metric label="GARCH 年化波动率" value={formatPercent(analysis.model.annualVolatility)} meta="下一期条件波动率" tone="violet" />
                </div>
              </div>
            </section>
          </Reveal>

          <Reveal>
            <section className="content-section two-chart-grid">
              <article className="chart-panel"><div className="panel-title"><DatabaseZap size={18} /><div><h3>真实值与预测值</h3><p>最近 130 个测试样本</p></div></div><ModelTestChart data={analysis.model.testSeries} /></article>
              <article className="chart-panel"><div className="panel-title"><RefreshCw size={18} /><div><h3>特征重要性</h3><p>XGBoost 模型贡献</p></div></div><ImportanceChart data={analysis.model.featureImportance} /></article>
              <article className="chart-panel chart-panel-wide"><div className="panel-title"><Sparkles size={18} /><div><h3>GARCH 条件波动率</h3><p>最近 300 个建模观测</p></div></div><VolatilityChart data={analysis.model.conditionalVolatility} /></article>
            </section>
          </Reveal>
        </>
      )}
    </div>
  );
}
