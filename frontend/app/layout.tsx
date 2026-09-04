import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "跨境汇率风险智能预警与避险策略实训工具",
  description: "基于真实 USD/CNY 数据的汇率风险识别、AI 建模、套保策略与蒙特卡洛实训平台。",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
