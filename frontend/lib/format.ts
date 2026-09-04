export const formatRate = (value: number) => value.toFixed(4);

export const formatPercent = (value: number, digits = 1) =>
  new Intl.NumberFormat("zh-CN", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);

export const formatCny = (value: number) => {
  const sign = value < 0 ? "-" : "";
  const absolute = Math.abs(value);
  if (absolute >= 100_000_000) return `${sign}¥${(absolute / 100_000_000).toFixed(2)} 亿`;
  if (absolute >= 10_000) return `${sign}¥${(absolute / 10_000).toFixed(2)} 万`;
  return `${sign}¥${absolute.toLocaleString("zh-CN", { maximumFractionDigits: 2 })}`;
};

export const formatUsd = (value: number) =>
  `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;

export const compactDate = (value: string) => value.replaceAll("-", ".");
