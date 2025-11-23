# Copilot Instructions for AI Agents

## 项目架构概览
- 本项目为期货量化分析系统，采用模块化结构，核心目录为 `src/`，包含数据获取、处理、分析、数据库、报告输出等子模块。
- 主要组件：
  - `data_fetcher/akshare_client.py`：通过 Akshare 获取期货行情数据，支持多品种、频率限制、品种映射。
  - `input/data_processor.py`：负责数据清洗、转换、批量处理，调用数据获取和数据库存储。
  - `database/database.py`、`database/repository.py`：数据库连接、表结构管理、数据持久化，基于 SQLAlchemy，配置由 `config/settings.py` 提供。
  - `models/data_models.py`：定义核心数据表（行情、分析结果、信号等），所有表均继承自 `Base`。
  - `analysis/technical_analyzer.py`：实现技术指标计算（MA、RSI、MACD、布林带等）和趋势判断，输出建议。
  - `output/report_generator.py`：生成日报、信号报告，支持 JSON/CSV 导出，含准确率、趋势、绩效等统计。
  - `core/system_manager.py`：系统主入口，串联数据流（获取→处理→分析→报告），对外暴露 `run_daily_analysis` 等方法。

## 关键开发与调试流程
- **数据库初始化**：系统启动时自动创建表，表结构变更需同步 `models/data_models.py`。
- **数据流**：推荐通过 `system_manager.run_daily_analysis(symbols)` 触发全流程，或分别调用各子模块。
- **日志**：全局使用 `logging`，错误和进度均有详细日志，便于追踪。
- **测试**：测试脚本位于 `tests/`，如需集成测试建议从 `test_analy.py` 或 `test_report.py` 入手。
- **依赖**：核心依赖为 `akshare`、`sqlalchemy`、`pandas`，如需扩展请同步维护 `requirements.txt`。

## 项目约定与模式
- **单例模式**：如 `db_manager`、`akshare_client`、`data_processor`、`technical_analyzer`、`report_generator` 等均为全局单例。
- **数据表字段**：所有表字段均有注释，新增字段需同步注释说明。
- **异常处理**：各层均有 try/except，错误需日志记录并向上传递。
- **分析建议**：趋势类型（1:上涨, 2:震荡, 3:下跌），建议（buy/sell/hold），置信度为 0-1 浮点。
- **报告输出**：支持控制台、JSON、CSV，推荐统一用 `report_generator` 生成。

## 典型用法示例
```python
from src.core.system_manager import system
results = system.run_daily_analysis(["螺纹钢主连", "铁矿石主连"])
```

## 重要文件/目录参考
- `src/core/system_manager.py`：主流程、集成入口
- `src/database/database.py`、`src/models/data_models.py`：数据库结构
- `src/analysis/technical_analyzer.py`：指标与建议逻辑
- `src/output/report_generator.py`：报告与统计

## 其他
- 若需扩展新品种、指标或报告类型，建议先查阅对应模块注释与接口。
- 所有模块均应保持注释齐全、接口清晰。
