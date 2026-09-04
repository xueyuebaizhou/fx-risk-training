"use client";

import { useMemo, useState } from "react";
import { Check, Download, FileCheck2, FileText, Scale } from "lucide-react";

import { Reveal } from "@/components/reveal";
import { LockedState, PageHeader, PrimaryButton, SectionHeading } from "@/components/ui";
import { requestReport } from "@/lib/api";
import { formatCny, formatPercent } from "@/lib/format";
import { calculateMetrics } from "@/lib/risk";
import { useTraining } from "@/lib/training-context";

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function ReportStep() {
  const { analysis, inputs } = useTraining();
  const [finalRatio, setFinalRatio] = useState(inputs.hedgeRatio);
  const [reason, setReason] = useState("");
  const [downloading, setDownloading] = useState<"pdf" | "html" | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const selected = useMemo(() => {
    if (!analysis) return null;
    return analysis.strategies.find((row) => row.ratio === finalRatio) || calculateMetrics(
      analysis.simulation.terminalRates,
      inputs,
      analysis.inputs.spotRate,
      finalRatio,
    );
  }, [analysis, finalRatio, inputs]);
  if (!analysis || !selected) return <LockedState />;

  const download = async (format: "pdf" | "html") => {
    if (!reason.trim()) {
      setMessage("请先填写策略选择理由。 ");
      return;
    }
    setDownloading(format);
    setMessage(null);
    try {
      const blob = await requestReport(inputs, finalRatio, reason, format);
      saveBlob(blob, `跨境汇率风险实训报告.${format}`);
      setMessage(`${format.toUpperCase()} 报告已生成并开始下载。`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "报告生成失败。 ");
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="step-page">
      <Reveal>
        <PageHeader
          kicker="STEP 06 / DECISION"
          title="最后一步，是解释你的选择。"
          description="比较五档固定套保比例，在现金流稳定性与保留有利汇率空间之间作出判断，并生成包含完整数据口径的实验报告。"
          aside={<div className="header-symbol"><FileCheck2 size={25} /><span>DECISION LOG<br /><b>PDF + HTML</b></span></div>}
        />
      </Reveal>

      <Reveal delay={70}>
        <section className="content-section">
          <SectionHeading title="策略总览" note="点击一行即可设为最终选择" />
          <div className="decision-cards">
            {analysis.strategies.map((row) => (
              <button key={row.ratio} className={finalRatio === row.ratio ? "is-selected" : ""} onClick={() => setFinalRatio(row.ratio)}>
                <span>{formatPercent(row.ratio, 0)} 套保</span>
                <strong>{formatCny(row.cfar95)}</strong>
                <small>CFaR₉₅</small>
                <div><em>风险下降</em><b>{formatPercent(row.riskReduction)}</b></div>
                {finalRatio === row.ratio && <i><Check size={13} /></i>}
              </button>
            ))}
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="decision-layout">
          <div className="decision-form">
            <SectionHeading eyebrow="YOUR DECISION" title="提交判断，而不只是提交一个数字。" />
            <div className="chosen-ratio"><div><Scale size={22} /></div><span>最终选择</span><strong>{formatPercent(finalRatio, 0)} 远期套保</strong></div>
            <label className="reason-field">
              <span>选择理由 <em>必填</em></span>
              <textarea value={reason} maxLength={500} onChange={(event) => setReason(event.target.value)} placeholder="例如：希望将 CFaR 控制在预算收入的 2% 以内，同时保留一部分有利汇率变动空间……" />
              <small>{reason.length} / 500</small>
            </label>
            {message && <div className={`form-message ${message.includes("已生成") ? "is-success" : ""}`}>{message}</div>}
            <div className="download-actions">
              <PrimaryButton onClick={() => download("pdf")} disabled={Boolean(downloading)}>{downloading === "pdf" ? "正在生成 PDF…" : "生成并下载 PDF"}</PrimaryButton>
              <button className="secondary-button" onClick={() => download("html")} disabled={Boolean(downloading)}><FileText size={17} />{downloading === "html" ? "正在生成…" : "下载 HTML 备用版"}</button>
            </div>
          </div>
          <aside className="report-preview surface-lavender">
            <div className="report-page">
              <div className="report-page-top"><span>熵合科技</span><em>FX LAB / 2026</em></div>
              <h3>跨境汇率风险<br />实训报告</h3>
              <p>USD/CNY · 出口收汇</p>
              <div className="report-rule" />
              <dl>
                <div><dt>应收金额</dt><dd>${inputs.amount.toLocaleString("en-US")}</dd></div>
                <div><dt>结算期限</dt><dd>{inputs.termDays} 天</dd></div>
                <div><dt>最终策略</dt><dd>{formatPercent(finalRatio, 0)} 远期</dd></div>
                <div><dt>策略 CFaR</dt><dd>{formatCny(selected.cfar95)}</dd></div>
              </dl>
              <div className="report-seal"><Download size={18} /><span>DATA · MODEL · RISK<br />STRATEGY · DECISION</span></div>
            </div>
          </aside>
        </section>
      </Reveal>
    </div>
  );
}
