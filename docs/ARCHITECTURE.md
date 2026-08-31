# 新项目架构

## GitHub仓库

GitHub是唯一代码源，计划结构：

```text
fx-risk-training/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── fxlab/
│   ├── config.py
│   ├── state.py
│   ├── data.py
│   ├── models.py
│   ├── risk.py
│   ├── simulation.py
│   ├── reporting.py
│   ├── storage.py
│   ├── ui.py
│   └── pages/
│       ├── case_page.py
│       ├── model_page.py
│       ├── exposure_page.py
│       ├── strategy_page.py
│       ├── simulation_page.py
│       └── report_page.py
├── data/
│   └── DEXCHUS_snapshot.csv
├── supabase/
│   └── schema.sql
├── reports/
│   └── .gitkeep
└── tests/
    ├── test_models.py
    ├── test_risk.py
    └── test_workflow.py
```

不得提交：真实Secrets、缓存、生成报告、原项目程序和技术组Word文档。

## Supabase新项目

第一版可不依赖Supabase运行。若启用，仅承担：

- `training_reports`：报告元数据
- `training-reports`：PDF私有存储桶
- 后续可选的实验记录

第一版不建设Auth、OTP和用户资料表。暴露表必须启用RLS；匿名与普通客户端不直接获得报告读写权限。Service Role密钥只能存放于Streamlit Secrets。

## Streamlit新App

- Repository：`xueyuebaizhou/fx-risk-training`
- Branch：`main`
- Main file path：`app.py`
- 建议Python：3.12
- 程序和依赖全部从GitHub拉取
- Supabase配置只填写到Streamlit Advanced settings → Secrets

在`app.py`尚未进入`main`前，不创建正式Streamlit部署，避免空入口导致部署失败。

## 分支与提交

- `main`：稳定基线
- `codex/refactor-v1`：第一版重构
- 重构分支完成语法、单元、真实数据和端到端测试后创建PR
- 禁止直接向原仓库`lithium-hedge-cloud`提交任何新项目内容
