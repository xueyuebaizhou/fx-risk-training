from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import APP_TITLE, REPORT_DIR, SIMULATION_PATHS
from .risk import budget_income, calculate_risk_metrics, hedged_income


def _report_payload(state: dict) -> dict:
    data = state["fx_data"]
    models = state["model_result"]
    simulation = state["simulation_result"]
    ratio = float(state["final_ratio"])
    incomes = hedged_income(
        state["amount"], ratio, state["forward_rate"], simulation.terminal_rates
    )
    metrics = calculate_risk_metrics(
        incomes, budget_income(state["amount"], state["budget_rate"])
    )
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "data": data,
        "models": models,
        "simulation": simulation,
        "ratio": ratio,
        "reason": state["decision_reason"].strip(),
        "metrics": metrics,
        "strategy_table": state["strategy_table"].copy(),
        "amount": float(state["amount"]),
        "term_days": int(state["term_days"]),
        "spot_rate": float(state["spot_rate"]),
        "budget_rate": float(state["budget_rate"]),
        "forward_rate": float(state["forward_rate"]),
    }


def build_html_report(state: dict) -> str:
    p = _report_payload(state)
    xgb, garch = p["models"].xgboost, p["models"].garch
    table_html = p["strategy_table"].to_html(
        index=False, float_format=lambda x: f"{x:,.4f}"
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{escape(APP_TITLE)} 实验报告</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif;color:#24384b;max-width:980px;margin:40px auto;line-height:1.7}}h1,h2{{color:#17324d}}.meta{{color:#66788a}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #dce6ef;padding:7px;text-align:right}}th{{background:#eef5fb}}.note{{background:#f3f7fa;padding:12px;border-left:4px solid #3278b5}}@media print{{body{{margin:18mm}}}}</style></head><body>
<h1>{escape(APP_TITLE)}：实验报告</h1><p class="meta">生成时间：{p["generated_at"]}</p>
<h2>一、案例信息</h2><p>出口收汇；USD 应收金额 {p["amount"]:,.2f}；结算期限 {p["term_days"]} 个自然日；当前即期汇率 S₀={p["spot_rate"]:.4f}；预算汇率 B={p["budget_rate"]:.4f}；教学案例远期报价 F={p["forward_rate"]:.4f}，单位均为 CNY/USD。</p>
<h2>二、真实数据与 AI 模型</h2><p>来源：{escape(p["data"].source)}。样本范围：{p["data"].start_date} 至 {p["data"].end_date}；读取时间：{escape(p["data"].retrieved_at)}；模式：{escape(p["data"].mode)}。</p><p>XGBoost 下一交易日预测={xgb.prediction_next_day:.4f}，MAE={xgb.mae:.6f}，RMSE={xgb.rmse:.6f}，方向准确率={xgb.direction_accuracy:.2%}。GARCH 预测日波动率={garch.daily_volatility:.4%}，年化波动率={garch.annual_volatility:.2%}。</p>
<h2>三、风险敞口与策略比较</h2><p>企业持有美元应收敞口，USD/CNY 下跌会使结汇人民币收入减少。全部指标由同一批 {SIMULATION_PATHS:,} 条模型教学情景计算。</p>{table_html}
<h2>四、学生决策与评价</h2><p>最终选择：{p["ratio"]:.0%} 远期套保。理由：{escape(p["reason"])}</p><p>该策略平均收入 ¥{p["metrics"].mean_income:,.2f}，5%分位数收入 ¥{p["metrics"].q05_income:,.2f}，VaR₉₅ ¥{p["metrics"].var95:,.2f}，CFaR₉₅ ¥{p["metrics"].cfar95:,.2f}，Risk Ratio={p["metrics"].risk_ratio:.2%}，预警为“{p["metrics"].risk_level}”。</p>
<p class="note">说明：蒙特卡洛结果是模型生成的教学情景，不是真实未来行情；F 为教学案例远期报价，不是实时银行报价；风险阈值是系统内部教学规则，不代表监管、银行或其他金融机构的统一标准。</p>
</body></html>"""


def build_pdf_report(state: dict) -> bytes:
    p = _report_payload(state)
    xgb, garch = p["models"].xgboost, p["models"].garch
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "CNTitle",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=18,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324d"),
    )
    heading = ParagraphStyle(
        "CNHeading",
        parent=styles["Heading2"],
        fontName="STSong-Light",
        fontSize=13,
        leading=19,
        spaceBefore=8,
        textColor=colors.HexColor("#17324d"),
    )
    body = ParagraphStyle(
        "CNBody",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=9.5,
        leading=15,
    )
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"{APP_TITLE} 实验报告",
    )
    story = [
        Paragraph(f"{APP_TITLE}<br/>实验报告", title),
        Spacer(1, 5 * mm),
        Paragraph(f"生成时间：{p['generated_at']}", body),
    ]
    story += [
        Paragraph("一、案例信息", heading),
        Paragraph(
            f"出口收汇；USD 应收金额 {p['amount']:,.2f}；结算期限 {p['term_days']} 个自然日；S₀={p['spot_rate']:.4f}，B={p['budget_rate']:.4f}，教学案例远期报价 F={p['forward_rate']:.4f}，单位 CNY/USD。",
            body,
        ),
    ]
    story += [
        Paragraph("二、真实数据与 AI 模型", heading),
        Paragraph(
            f"数据来源：{p['data'].source}。样本范围 {p['data'].start_date} 至 {p['data'].end_date}；读取时间 {p['data'].retrieved_at}；模式 {p['data'].mode}。",
            body,
        ),
        Paragraph(
            f"XGBoost：下一交易日预测 {xgb.prediction_next_day:.4f}，MAE {xgb.mae:.6f}，RMSE {xgb.rmse:.6f}，方向准确率 {xgb.direction_accuracy:.2%}。GARCH：日波动率 {garch.daily_volatility:.4%}，年化波动率 {garch.annual_volatility:.2%}。",
            body,
        ),
    ]
    story.append(Paragraph("三、策略比较（同一批 10,000 条教学情景）", heading))
    columns = [
        "套保比例",
        "平均收入",
        "5%分位数收入",
        "收入标准差",
        "VaR95",
        "CFaR95",
        "风险下降幅度",
    ]
    rows = [["比例", "平均收入", "5%分位", "标准差", "VaR95", "CFaR95", "风险下降"]]
    for _, row in p["strategy_table"][columns].iterrows():
        rows.append(
            [
                f"{row['套保比例']:.0%}",
                f"{row['平均收入'] / 10000:,.2f}万",
                f"{row['5%分位数收入'] / 10000:,.2f}万",
                f"{row['收入标准差'] / 10000:,.2f}万",
                f"{row['VaR95'] / 10000:,.2f}万",
                f"{row['CFaR95'] / 10000:,.2f}万",
                f"{row['风险下降幅度']:.1%}",
            ]
        )
    table = Table(
        rows,
        repeatRows=1,
        colWidths=[18 * mm, 25 * mm, 25 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcebf7")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aabcca")),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f7fafc")],
                ),
            ]
        )
    )
    story += [
        table,
        Paragraph("四、学生决策与评价", heading),
        Paragraph(f"最终选择 {p['ratio']:.0%} 远期套保。理由：{p['reason']}", body),
        Paragraph(
            f"该策略平均收入 ¥{p['metrics'].mean_income:,.2f}，VaR₉₅ ¥{p['metrics'].var95:,.2f}，CFaR₉₅ ¥{p['metrics'].cfar95:,.2f}，Risk Ratio {p['metrics'].risk_ratio:.2%}，预警 {p['metrics'].risk_level}。",
            body,
        ),
        Spacer(1, 3 * mm),
        Paragraph(
            "说明：蒙特卡洛结果是模型生成的教学情景，不是真实未来行情；F 是教学案例远期报价，不是实时银行报价；风险阈值仅用于课程实训。",
            body,
        ),
    ]
    doc.build(story)
    return buf.getvalue()


def save_report(
    html_text: str,
    pdf_bytes: bytes,
    amount: float,
    term_days: int,
    report_dir: Path = REPORT_DIR,
) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_出口收汇_{int(amount)}USD_{int(term_days)}天"
    html_path, pdf_path = report_dir / f"{stem}.html", report_dir / f"{stem}.pdf"
    html_path.write_text(html_text, encoding="utf-8")
    pdf_path.write_bytes(pdf_bytes)
    return html_path, pdf_path
