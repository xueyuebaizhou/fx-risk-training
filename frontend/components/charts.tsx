"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AnalysisData, MarketPoint, StrategyRow } from "@/lib/types";

const axis = { fill: "#7b7785", fontSize: 11 };
const grid = "#e8e5ed";
const tooltipStyle = {
  border: "1px solid #e2dee8",
  borderRadius: 14,
  boxShadow: "0 18px 48px rgba(31, 26, 42, .12)",
  fontSize: 12,
};

export function MarketChart({
  data,
  mode = "rate",
  compact = false,
}: {
  data: MarketPoint[];
  mode?: "rate" | "returnPct" | "volatilityPct";
  compact?: boolean;
}) {
  const visible = compact ? data.slice(-180) : data;
  const labels = {
    rate: "USD/CNY",
    returnPct: "日收益率",
    volatilityPct: "年化波动率",
  };
  return (
    <div className={`chart ${compact ? "chart-compact" : ""}`}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={visible} margin={{ top: 12, right: 12, left: compact ? -24 : -4, bottom: 0 }}>
          <defs>
            <linearGradient id={`area-${mode}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6250d9" stopOpacity={0.24} />
              <stop offset="100%" stopColor="#6250d9" stopOpacity={0} />
            </linearGradient>
          </defs>
          {!compact && <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />}
          <XAxis
            dataKey="date"
            tick={axis}
            minTickGap={64}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: string) => value.slice(0, 7)}
            hide={compact}
          />
          <YAxis
            tick={axis}
            tickLine={false}
            axisLine={false}
            width={54}
            domain={["auto", "auto"]}
            hide={compact}
            tickFormatter={(value: number) =>
              mode === "rate" ? value.toFixed(2) : `${value.toFixed(1)}%`
            }
          />
          {!compact && (
            <Tooltip
              contentStyle={tooltipStyle}
              labelFormatter={(value) => `日期 ${value}`}
              formatter={(value) => [
                mode === "rate" ? Number(value).toFixed(4) : `${Number(value).toFixed(3)}%`,
                labels[mode],
              ]}
            />
          )}
          <Area
            type="monotone"
            dataKey={mode}
            stroke="#5644c8"
            strokeWidth={compact ? 2.2 : 1.8}
            fill={`url(#area-${mode})`}
            connectNulls
            isAnimationActive
            animationDuration={900}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ModelTestChart({ data }: { data: AnalysisData["model"]["testSeries"] }) {
  const visible = data.slice(-130);
  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={visible} margin={{ top: 12, right: 12, left: -4, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis dataKey="date" tick={axis} minTickGap={48} tickLine={false} axisLine={false} />
          <YAxis tick={axis} tickLine={false} axisLine={false} width={54} domain={["auto", "auto"]} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 12 }} />
          <Line type="monotone" dataKey="actual" name="真实值" dot={false} stroke="#25202f" strokeWidth={2} />
          <Line type="monotone" dataKey="predicted" name="预测值" dot={false} stroke="#00a486" strokeWidth={1.8} strokeDasharray="5 4" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ImportanceChart({ data }: { data: AnalysisData["model"]["featureImportance"] }) {
  return (
    <div className="chart chart-tall">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 18, left: 34, bottom: 0 }}>
          <CartesianGrid horizontal={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis type="number" hide />
          <YAxis type="category" dataKey="feature" tick={axis} tickLine={false} axisLine={false} width={98} />
          <Tooltip contentStyle={tooltipStyle} formatter={(value) => Number(value).toFixed(4)} />
          <Bar dataKey="importance" name="重要性" fill="#6855dc" radius={[0, 7, 7, 0]} animationDuration={900} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function VolatilityChart({
  data,
}: {
  data: AnalysisData["model"]["conditionalVolatility"];
}) {
  return (
    <div className="chart chart-tall">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data.slice(-300)} margin={{ top: 8, right: 12, left: -6, bottom: 0 }}>
          <defs>
            <linearGradient id="vol-area" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00a486" stopOpacity={0.32} />
              <stop offset="100%" stopColor="#00a486" stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis dataKey="date" tick={axis} minTickGap={48} tickLine={false} axisLine={false} />
          <YAxis tick={axis} tickLine={false} axisLine={false} width={52} tickFormatter={(value: number) => `${value.toFixed(1)}%`} />
          <Tooltip contentStyle={tooltipStyle} formatter={(value) => `${Number(value).toFixed(3)}%`} />
          <Area type="monotone" dataKey="volatilityPct" name="条件波动率" stroke="#008c73" fill="url(#vol-area)" strokeWidth={1.8} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PathChart({ paths }: { paths: AnalysisData["simulation"]["paths"] }) {
  const selected = paths.slice(0, 18);
  const length = selected[0]?.values.length ?? 0;
  const data = Array.from({ length }, (_, day) => {
    const point: Record<string, number> = { day };
    selected.forEach((path) => {
      point[`p${path.id}`] = path.values[day];
    });
    return point;
  });
  const colors = ["#6150d6", "#00a486", "#1675bb", "#d66f62", "#9888ef", "#45b99f"];
  return (
    <div className="chart chart-paths">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 12, left: -4, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis dataKey="day" tick={axis} tickLine={false} axisLine={false} />
          <YAxis tick={axis} tickLine={false} axisLine={false} width={54} domain={["auto", "auto"]} />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={(value) => `第 ${value} 个交易日`} />
          {selected.map((path, index) => (
            <Line
              key={path.id}
              type="monotone"
              dataKey={`p${path.id}`}
              name={`路径 ${path.id}`}
              dot={false}
              stroke={colors[index % colors.length]}
              strokeOpacity={0.38}
              strokeWidth={1}
              isAnimationActive={index < 6}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function HistogramChart({
  data,
  references,
  unit = "",
}: {
  data: { x: number; count: number }[];
  references: { value: number; label: string; color?: string }[];
  unit?: string;
}) {
  return (
    <div className="chart chart-histogram">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 10, left: -12, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis type="number" dataKey="x" domain={["dataMin", "dataMax"]} tick={axis} tickLine={false} axisLine={false} minTickGap={40} tickFormatter={(value: number) => `${value.toFixed(2)}${unit}`} />
          <YAxis tick={axis} tickLine={false} axisLine={false} width={48} />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={(value) => `${Number(value).toFixed(4)}${unit}`} />
          {references.map((reference, index) => {
            const color = reference.color || (index === 0 ? "#00a486" : "#d66f62");
            return (
              <ReferenceLine
                key={`${reference.label}-${reference.value}`}
                x={reference.value}
                stroke={color}
                strokeDasharray="5 4"
                label={{
                  value: reference.label,
                  fill: color,
                  fontSize: 11,
                  position: index % 2 === 0 ? "insideTopLeft" : "insideTopRight",
                }}
              />
            );
          })}
          <Bar dataKey="count" name="模拟次数" fill="#7563de" radius={[5, 5, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function StrategyRiskChart({ data }: { data: StrategyRow[] }) {
  const chartData = data.map((row) => ({
    ratio: `${Math.round(row.ratio * 100)}%`,
    CFaR: row.cfar95 / 10_000,
    波动: row.incomeStd / 10_000,
  }));
  return (
    <div className="chart chart-tall">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 12, right: 12, left: -4, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={grid} strokeDasharray="3 5" />
          <XAxis dataKey="ratio" tick={axis} tickLine={false} axisLine={false} />
          <YAxis tick={axis} tickLine={false} axisLine={false} width={54} />
          <Tooltip contentStyle={tooltipStyle} formatter={(value) => `${Number(value).toFixed(2)} 万`} />
          <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="CFaR" fill="#6754d8" radius={[7, 7, 0, 0]} />
          <Bar dataKey="波动" fill="#23aa8d" radius={[7, 7, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
