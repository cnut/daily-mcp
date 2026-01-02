# Daily MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> 🗓️ Your Personal Life Assistant — Record, Query, and Visualize Daily Life with Natural Language

一个面向个人的 MCP (Model Context Protocol) 服务器，让你通过自然语言记录和管理日常生活。可嵌入 Claude Desktop 等 AI Agent，用对话的方式轻松记录财务、待办、健康和日常点滴。

## ✨ 特性

- **🗣️ 自然语言交互** - 通过 AI Agent 用日常对话记录生活，无需复杂操作
- **🔒 本地优先** - 数据存储在本地 SQLite，隐私安全有保障
- **🔍 SQL 查询** - 支持灵活的 SQL 查询，满足复杂数据分析需求
- **📊 数据可视化** - 返回结构化数据，配合 Agent 生成图表
- **📦 多维度记录** - 财务、待办、健康、日志一站式管理

## 📖 目录

- [快速开始](#-快速开始)
- [功能详解](#-功能详解)
- [MCP 协议支持](#-mcp-协议支持)
- [配置选项](#️-配置选项)
- [开发指南](#-开发指南)
- [项目架构](#-项目架构)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)

## 🚀 快速开始

### 安装

```bash
# 使用 pip 安装
pip install daily-mcp

# 或使用 uv（推荐）
uv pip install daily-mcp

# 或从源码安装
git clone https://github.com/peng/daily-mcp.git
cd daily-mcp
pip install -e .
```

### 配置 Claude Desktop

在 Claude Desktop 配置文件中添加：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp"
    }
  }
}
```

或使用 `uvx`（无需预先安装）：

```json
{
  "mcpServers": {
    "daily-mcp": {
      "command": "uvx",
      "args": ["daily-mcp"]
    }
  }
}
```

### 验证安装

重启 Claude Desktop 后，在对话中尝试：

```
用户：帮我记录今天午餐花了 35 元
```

## 🎯 功能详解

### 💰 财务管理 (Finance)

记录日常收支，支持分类和 SQL 查询。

| 功能 | 说明 |
|------|------|
| 记录支出 | 金额、分类、备注、日期 |
| 记录收入 | 金额、来源、备注、日期 |
| SQL 查询 | 灵活查询历史数据 |

**示例对话：**
```
用户：今天午餐花了 35 元，晚上买了本书 68 元
用户：这个月餐饮支出多少？
用户：画一个最近三个月的支出趋势图
```

**数据表结构：**
```sql
-- finance 表
id, type, amount, category, source, note, date, created_at
```

---

### ✅ 待办任务 (Todo)

管理日常任务，支持主题分组和完成情况追踪。

| 功能 | 说明 |
|------|------|
| 添加待办 | 内容、主题、截止日期 |
| 完成待办 | 按 ID 或关键词匹配 |
| 列出待办 | 按主题/状态筛选 |

**示例对话：**
```
用户：添加一个待办：周五前完成项目报告，主题是工作
用户：完成了"买牛奶"这个任务
用户：看看"健身"主题下还有哪些没完成的
```

---

### 🏥 健康记录 (Health)

追踪个人健康指标，建立长期健康档案。

| 指标类型 | 示例值 |
|----------|--------|
| blood_pressure | 120/80 |
| heart_rate | 72 |
| weight | 70.5 |
| blood_sugar | 5.6 |
| sleep | 7.5 (小时) |
| exercise | 跑步 5km |

**示例对话：**
```
用户：今天血压 125/82，心率 72
用户：昨晚睡了 7 小时
用户：画一下最近一个月的血压变化图
```

---

### 📝 日常日志 (Daily Log)

自由记录生活点滴，支持关键词搜索。

**示例对话：**
```
用户：今天早上跑了 5 公里，感觉不错，中午和老王吃了顿火锅
用户：搜索一下上周提到"火锅"的日志
```

## 🔌 MCP 协议支持

Daily MCP 完整实现了 MCP 协议的三大核心功能：

### Tools (工具)

| 工具名 | 描述 |
|--------|------|
| `record_expense` | 记录支出 |
| `record_income` | 记录收入 |
| `query_finance` | SQL 查询财务数据 |
| `add_todo` | 添加待办 |
| `complete_todo` | 完成待办 |
| `list_todos` | 列出待办 |
| `record_health` | 记录健康指标 |
| `query_health` | 查询健康数据 |
| `add_daily_log` | 添加日志 |
| `search_daily_log` | 搜索日志 |

### Resources (资源)

动态数据资源，Agent 可主动读取：

| URI | 描述 |
|-----|------|
| `daily://summary/today` | 今日摘要 |
| `daily://summary/weekly` | 周摘要 |
| `daily://summary/YYYY-MM-DD` | 指定日期摘要 |

### Prompts (提示词)

预设提示词模板，引导 Agent 执行复杂任务：

| 名称 | 描述 | 参数 |
|------|------|------|
| `daily-review` | 每日回顾 | `date` (可选) |
| `weekly-planning` | 周计划 | `focus` (可选) |
| `financial-analysis` | 财务分析 | `period` (必填) |
| `health-checkup` | 健康检查 | `metric_type`, `days` |

## ⚙️ 配置选项

### CLI 参数

```bash
daily-mcp [OPTIONS]

Options:
  -d, --db-path PATH   数据库文件路径 (默认: ~/.daily-mcp/data.db)
  -v, --verbose        日志级别 (-v: INFO, -vv: DEBUG)
  --log-file PATH      日志输出文件
  --version            显示版本号
  --help               显示帮助信息
```

### 示例

```bash
# 使用自定义数据库路径
daily-mcp --db-path ./my-data.db

# 开启详细日志
daily-mcp -vv --log-file ./debug.log

# 在 Claude Desktop 配置中使用
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp",
      "args": ["--db-path", "/path/to/data.db", "-v"]
    }
  }
}
```

### 数据存储

默认数据目录：`~/.daily-mcp/`

```
~/.daily-mcp/
├── data.db          # SQLite 数据库
└── logs/            # 日志文件目录
    └── 2024-01-15.json
```

## 👩‍💻 开发指南

### 环境准备

```bash
# 克隆项目
git clone https://github.com/peng/daily-mcp.git
cd daily-mcp

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install
```

### 常用命令

```bash
# 运行测试
make test
# 或
pytest tests/ -v

# 代码检查
make lint
# 或
ruff check src/ tests/

# 代码格式化
make format
# 或
ruff format src/ tests/

# 类型检查
make typecheck
# 或
mypy src/

# 运行所有检查
make check
```

### 开发工作流

1. **Fork & Clone** - Fork 项目并克隆到本地
2. **Create Branch** - 创建功能分支 `git checkout -b feature/xxx`
3. **Make Changes** - 编写代码和测试
4. **Run Checks** - 运行 `make check` 确保通过
5. **Commit** - 提交代码，遵循 [Conventional Commits](https://www.conventionalcommits.org/)
6. **Push & PR** - 推送并创建 Pull Request

### 代码规范

- **Python 3.10+** - 使用现代 Python 特性
- **Type Hints** - 所有函数必须有类型注解
- **Docstrings** - 公共 API 必须有文档字符串
- **Ruff** - 代码风格检查和格式化
- **MyPy** - 严格模式类型检查

## 🏗️ 项目架构

```
daily-mcp/
├── src/daily_mcp/
│   ├── __init__.py       # 包入口，导出 main
│   ├── server.py         # MCP 服务器入口，CLI 定义
│   ├── handlers.py       # MCP 处理器 (Tools/Resources/Prompts)
│   ├── schemas.py        # Pydantic 模型，工具参数定义
│   ├── db.py             # SQLite 数据库封装
│   ├── logging.py        # 日志配置
│   ├── resources.py      # MCP Resources 实现
│   ├── prompts.py        # MCP Prompts 模板
│   └── tools/            # 工具实现
│       ├── __init__.py
│       ├── finance.py    # 财务工具
│       ├── todo.py       # 待办工具
│       ├── health.py     # 健康工具
│       └── daily_log.py  # 日志工具
├── tests/                # 测试文件
│   ├── conftest.py       # pytest fixtures
│   ├── test_finance.py
│   ├── test_todo.py
│   ├── test_health.py
│   └── test_daily_log.py
├── pyproject.toml        # 项目配置
├── Makefile              # 常用命令
└── README.md
```

### 核心模块说明

| 模块 | 职责 |
|------|------|
| `server.py` | CLI 入口，启动 MCP 服务器 |
| `handlers.py` | 注册 MCP 协议的 Tools/Resources/Prompts |
| `schemas.py` | Pydantic 模型，自动生成 JSON Schema |
| `db.py` | SQLite 数据库操作封装 |
| `tools/*` | 各功能模块的具体实现 |

### 设计原则

1. **单一职责** - 每个模块只负责一个功能
2. **依赖注入** - Database 实例通过参数传递
3. **类型安全** - 使用 Pydantic 进行参数验证
4. **可测试性** - 所有模块可独立测试

## ❓ 常见问题

### Q: 数据存储在哪里？

默认存储在 `~/.daily-mcp/data.db`，可通过 `--db-path` 参数自定义。

### Q: 如何备份数据？

直接复制 `~/.daily-mcp/data.db` 文件即可。SQLite 是单文件数据库。

### Q: 支持哪些 AI Agent？

任何支持 MCP 协议的 Agent 都可以使用，包括：
- Claude Desktop
- 其他 MCP 兼容客户端

### Q: 如何查看所有可用工具？

在 Claude Desktop 中，点击 🔌 图标可以看到 daily-mcp 提供的所有工具。

### Q: 如何调试问题？

```bash
# 开启详细日志
daily-mcp -vv --log-file ./debug.log
```

## 🤝 贡献指南

欢迎贡献！请查看 [开发指南](#-开发指南) 了解如何设置开发环境。

### 贡献方式

- 🐛 **报告 Bug** - 提交 Issue 描述问题
- 💡 **功能建议** - 提交 Issue 讨论新功能
- 📝 **改进文档** - 修复错误或补充说明
- 🔧 **提交代码** - Fork 后提交 Pull Request

### Commit 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
refactor: 重构代码
test: 添加测试
chore: 其他修改
```

## 📄 License

[MIT](LICENSE) © peng

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议规范
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Python SDK
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - 官方 MCP Server 参考实现
