# Next.js / FastAPI 新版架构

## 目标

新版停止以 Streamlit 作为用户界面。计算公式、真实数据、模型、蒙特卡洛和报告生成继续由经过测试的 `fxlab` Python 核心负责；浏览器交互、状态、图表和动效迁移到 Next.js。

## 目录

```text
fx-risk-training/
├── frontend/                 # Next.js + TypeScript 静态前端
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/                  # FastAPI 服务层
│   ├── main.py
│   ├── schemas.py
│   └── service.py
├── fxlab/                    # 原 Python 计算核心
├── data/                     # 经核验的真实 FRED 快照
├── tests/
├── Dockerfile                # Railway 后端部署
├── railway.json
└── requirements-api.txt
```

## 数据流

1. 前端调用 `GET /api/v1/market` 取得真实行情和来源元数据。
2. 用户在实训案例中设置 A、T、B；模型页调用 `POST /api/v1/analysis`。
3. 后端在同一真实数据窗口上拟合 XGBoost 与 GARCH，并使用固定种子生成 10,000 条路径。
4. 后端返回模型、敞口、策略、路径抽样、完整终值和策略比较结果。
5. A、B、F、h 改变时，前端在同一完整终值样本上立即重算；T 改变时必须向后端重新生成路径。
6. 报告页调用 `POST /api/v1/reports`，由 Python 核心重新核算并生成 PDF 或 HTML。

## 缓存与一致性

- 后端进程缓存真实行情与模型结果，避免每次比例调整重复训练。
- 只有期限 T 改变会使路径失效；金额、预算汇率、远期报价和套保比例不改变路径本身。
- 报告不信任浏览器上传的计算结果，只接收业务输入并在服务端重算。
- 数据在线与快照均失败时返回 503，前端明确停止流程。

## 部署边界

- Cloudflare Pages 只承载静态前端，不保存密钥。
- Railway 承载 FastAPI 与 Python 模型依赖。
- Supabase 后续仅用于报告持久化，不进入首版关键链路。
- 原仓库 `lithium-hedge-cloud`、原数据库和原密钥均不得引用。
