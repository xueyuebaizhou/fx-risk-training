# 跨境汇率风险智能预警与避险策略实训工具

面向经管人工智能课程的 USD/CNY 汇率风险识别、AI 建模、远期避险策略比较与实验报告工具。新版采用 **Next.js + TypeScript 前端、FastAPI 服务层和既有 `fxlab` Python 计算核心**，视觉方向参考 Bound 的现代企业金融产品体验，但品牌、内容和交互均为熵合科技独立设计。

## 六模块实训闭环

1. **实训案例**：默认 90 天后收到 1,000,000 USD，可修改金额、期限和预算汇率。
2. **汇率数据与 AI 模型**：真实 DEXCHUS 日频数据、GARCH(1,1)、XGBoost 与真实测试集指标。
3. **风险敞口与智能预警**：美元应收识别、VaR、CFaR、Risk Ratio。
4. **避险策略沙盘**：不套保与远期结汇，支持 0%—100% 连续套保比例。
5. **蒙特卡洛情景**：固定种子 10,000 条教学路径及策略分布比较。
6. **策略评价与实验报告**：学生选择、理由、PDF/HTML 生成。

## 数据真实性

- 在线数据：FRED `DEXCHUS`，表示 1 USD 可兑换的 CNY 数，原始来源为美国联邦储备委员会 H.10。
- 离线后备：`data/DEXCHUS_snapshot.csv`，为同一官方序列的已核验真实快照。
- 在线与快照均失败时停止计算，不生成、随机补齐或静默替换历史行情。
- 训练、测试、图表、GARCH 和情景参数来自同一套基础数据。
- 蒙特卡洛结果始终标为“模型生成的教学情景”，不冒充真实未来行情。

## 架构

```text
Browser
  └─ frontend/  Next.js + TypeScript + Recharts
       └─ backend/  FastAPI JSON / report endpoints
            └─ fxlab/  FRED、XGBoost、GARCH、风险、模拟、报告核心
```

旧 Streamlit 页面暂时保留为功能基线，不再作为新版产品入口或部署目标。

## 本地运行

后端：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-api.txt
uvicorn backend.main:app --reload --port 8000
```

前端：

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

打开 `http://localhost:3000`。API 文档位于 `http://localhost:8000/docs`。

测试与构建：

```bash
pip install -r requirements-dev.txt -r requirements-api.txt
ruff check .
pytest -q
cd frontend && npm run lint && npm run build
```

## 部署

| 位置 | 内容 |
|---|---|
| GitHub | 单一代码源；本分支完成后通过 PR 合并到 `main` |
| Cloudflare Pages | 部署 `frontend/out` 静态前端，构建时配置 `NEXT_PUBLIC_API_BASE_URL` |
| Railway | 使用根目录 `Dockerfile` 部署 FastAPI，健康检查 `/api/v1/health` |
| Supabase 新项目 | 后续可选：报告元数据与私有 PDF 存储，不是首版运行前提 |

Supabase 若启用，必须新建本项目独立实例并执行 `supabase/schema.sql`，不得连接原“熵合科技”数据库。

## 关键约束

- 首版只支持 USD/CNY 出口收汇，不建设登录、OTP、库存、商品期货、商品期权和利润模块。
- XGBoost 预测下一交易日汇率水平，时间顺序 80%/20% 划分，不随机打乱。
- GARCH(1,1)估计条件波动率；完整情景计算固定 10,000 条路径。
- VaR、CFaR 与各套保比例基于同一批人民币收入情景。
- 远期汇率 F 明确为教学案例报价，不是实时银行报价。

完整口径见 [重构规格](docs/REFACTOR_SPEC.md)，验收项见 [验收清单](docs/ACCEPTANCE_CHECKLIST.md)。
