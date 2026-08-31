# 跨境汇率风险智能预警与避险策略实训工具

面向经管人工智能课程的 USD/CNY 汇率风险识别、AI 建模、远期避险策略比较与实验报告工具。项目由原“熵合科技”程序的计算与展示经验迁移而来，但代码、数据、数据库、密钥和部署完全独立。

## 六页实训闭环

1. 实训案例：默认 90 天后收到 1,000,000 USD，可修改 A、T、B。
2. 汇率数据与 AI 模型：真实 DEXCHUS 日频数据、GARCH(1,1)、XGBoost 与真实测试集指标。
3. 风险敞口与智能预警：美元应收识别、VaR、CFaR、Risk Ratio。
4. 避险策略沙盘：不套保与远期结汇，连续/快捷套保比例。
5. 蒙特卡洛情景：固定种子 10,000 条教学路径及策略分布比较。
6. 策略评价与实验报告：学生选择、理由、PDF/HTML 生成与本地存档。

## 数据真实性

- 在线数据：FRED `DEXCHUS`，含义为 1 USD 可兑换的 CNY 数，原始来源为美国联邦储备委员会 H.10。
- 离线后备：`data/DEXCHUS_snapshot.csv`，为同一官方序列的已核验真实快照，范围 2021-01-04 至 2026-08-21。
- 在线与快照均失败时停止计算，不生成、随机补齐或静默替换历史行情。
- 训练、测试、图表、GARCH 和情景参数来自同一套基础数据。
- 蒙特卡洛结果始终标为“模型生成的教学情景”，不冒充真实未来行情。

## 本地运行

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

测试：

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -q
```

## 部署分工

| 位置 | 内容 |
|---|---|
| GitHub | 全部 Python、测试、真实公开数据快照、SQL 与非敏感配置 |
| Streamlit Cloud | Repository `xueyuebaizhou/fx-risk-training`；Branch `main`；Main file `app.py` |
| Supabase 新项目 | 可选报告元数据表 `training_reports` 与私有桶 `training-reports` |
| Streamlit Secrets | 新 Supabase URL 与 Service Role Key；绝不提交 GitHub |

Supabase 不是首版运行前提。如需启用，必须在本项目的新 Supabase 项目执行 `supabase/schema.sql`，不得在原“熵合科技”数据库执行。

## 关键约束

- 首版只支持 USD/CNY 出口收汇，不建设登录、OTP、库存、商品期货、商品期权和利润模块。
- XGBoost 预测下一交易日汇率水平，时间顺序 80%/20% 划分，不随机打乱。
- GARCH(1,1) 估计条件波动率；完整情景计算固定 10,000 条路径。
- VaR、CFaR 与各套保比例基于同一批人民币收入情景。
- 远期汇率 F 明确为教学案例报价，不是实时银行报价。

完整口径见 [重构规格](docs/REFACTOR_SPEC.md)，验收项见 [验收清单](docs/ACCEPTANCE_CHECKLIST.md)。
