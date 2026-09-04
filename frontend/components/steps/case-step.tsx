"use client";

import { ArrowDownRight, BadgeDollarSign, Globe2, ScanSearch, ShieldCheck, Workflow } from "lucide-react";

import { MarketChart } from "@/components/charts";
import { Reveal } from "@/components/reveal";
import { DataSourceNote, Metric, PageHeader, PrimaryButton, SectionHeading } from "@/components/ui";
import { formatCny, formatRate, formatUsd } from "@/lib/format";
import { useTraining } from "@/lib/training-context";

const tasks = [
  ["01", "读取真实行情", "FRED DEXCHUS 日频数据"],
  ["02", "运行 AI 模型", "GARCH + XGBoost"],
  ["03", "识别风险敞口", "VaR、CFaR 与预警"],
  ["04", "比较避险策略", "10,000 条统一情景"],
  ["05", "形成实验报告", "记录决策与依据"],
];

export function CaseStep() {
  const { inputs, updateInput, market, loadingMarket, setActiveStep } = useTraining();
  const budgetIncome = inputs.amount * inputs.budgetRate;

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 01 / CASE"
          title="先把风险说清楚。"
          description="建立统一的出口收汇案例。金额、期限与预算汇率将贯穿模型、风险、策略和报告，任何调整都会同步到后续结果。"
          aside={<span className="status-chip"><span /> USD/CNY · 出口收汇</span>}
        />
      </Reveal>

      <Reveal delay={70}>
        <section className="case-hero surface-lavender">
          <div className="case-story">
            <span className="mini-label">STANDARD TRAINING CASE</span>
            <h2>未来收到美元，<br />真正不确定的是人民币收入。</h2>
            <p>中国制造业企业向美国客户出口产品，计划在 {inputs.termDays} 天后收到 {formatUsd(inputs.amount)}。企业以人民币进行成本与利润管理，因此 USD/CNY 下跌会压缩最终结汇收入。</p>
            <div className="case-tags">
              <span><Globe2 size={15} />跨境贸易</span>
              <span><BadgeDollarSign size={15} />美元应收</span>
              <span><ShieldCheck size={15} />现金流保护</span>
            </div>
          </div>
          <div className="market-window">
            <div className="market-window-top">
              <div>
                <span>USD / CNY</span>
                <strong>{market ? formatRate(market.spotRate) : "—"}</strong>
              </div>
              <div className="market-direction"><ArrowDownRight size={19} /> 风险方向</div>
            </div>
            {market && <MarketChart data={market.series} compact />}
            {!market && <div className={`chart-placeholder ${loadingMarket ? "is-loading" : ""}`} />}
            <div className="market-window-foot">
              <span>最新有效观测</span><strong>{market?.endDate || "等待真实数据"}</strong>
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal delay={90}>
        <section className="content-section">
          <SectionHeading title="案例参数" note="所有输入均为六个模块的统一业务状态" />
          <div className="input-grid">
            <label className="field-shell">
              <span>外币应收金额 A</span>
              <div><b>$</b><input aria-label="外币应收金额" type="number" min={1} step={50000} value={inputs.amount} onChange={(event) => updateInput("amount", Math.max(1, Number(event.target.value)))} /><em>USD</em></div>
              <small>未来预计收到的美元货款</small>
            </label>
            <label className="field-shell">
              <span>结算期限 T</span>
              <div><input aria-label="结算期限" type="number" min={1} max={730} value={inputs.termDays} onChange={(event) => updateInput("termDays", Math.min(730, Math.max(1, Number(event.target.value))))} /><em>自然日</em></div>
              <small>将自动折算为交易日</small>
            </label>
            <label className="field-shell">
              <span>预算汇率 B</span>
              <div><input aria-label="预算汇率" type="number" min={1} max={20} step={0.01} value={inputs.budgetRate} onChange={(event) => updateInput("budgetRate", Number(event.target.value))} /><em>CNY/USD</em></div>
              <small>企业制定预算时采用的汇率</small>
            </label>
          </div>
          <div className="metric-grid metric-grid-4">
            <Metric label="交易方向" value="出口收汇" meta="USD → CNY" />
            <Metric label="风险暴露" value="美元应收" meta="USD/CNY 下跌不利" tone="coral" />
            <Metric label="当前即期汇率 S₀" value={market ? formatRate(market.spotRate) : "—"} meta={market?.endDate || "读取中"} tone="green" />
            <Metric label="预算人民币收入" value={formatCny(budgetIncome)} meta={`${inputs.budgetRate.toFixed(4)} × ${formatUsd(inputs.amount)}`} tone="violet" />
          </div>
          <DataSourceNote />
        </section>
      </Reveal>

      <Reveal>
        <section className="content-section">
          <SectionHeading eyebrow="THE TRAINING FLOW" title="从一笔应收，走完整个风险决策闭环。" note="不是展示页，而是一套可操作的实训流程" />
          <div className="workflow-grid">
            {tasks.map(([number, title, detail], index) => (
              <article key={number} className="workflow-item">
                <span>{number}</span>
                <div className="workflow-icon">{index === 0 ? <ScanSearch size={19} /> : index === 4 ? <Workflow size={19} /> : <span className="workflow-dot" />}</div>
                <h3>{title}</h3>
                <p>{detail}</p>
              </article>
            ))}
          </div>
          <div className="section-action">
            <PrimaryButton onClick={() => setActiveStep("model")}>进入真实数据与 AI 模型</PrimaryButton>
          </div>
        </section>
      </Reveal>
    </div>
  );
}
