# Daily MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> 🗓️ Your Personal Life Assistant — Record, Query, and Visualize Daily Life with Natural Language

一个面向个人的 MCP Server，通过自然语言记录和管理日常生活。嵌入 Claude Desktop 等 AI Agent，用对话记录财务、待办、健康和日常点滴。

## ✨ 特性

- **🗣️ 自然语言** - 用日常对话记录生活
- **🔒 本地存储** - SQLite 数据库，隐私安全
- **🔍 SQL 查询** - 灵活的数据分析
- **📊 可视化** - 配合 Agent 生成图表

## 🚀 快速开始

### 安装

```bash
pip install daily-mcp
```

### 配置 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

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

### 开始使用

重启 Claude Desktop，然后：

```
用户：今天午餐花了 35 元
用户：添加待办：周五前完成报告
用户：记录血压 120/80
用户：这个月花了多少钱？
```

## 🎯 功能模块

| 模块 | 功能 | 示例 |
|------|------|------|
| **💰 财务** | 收支记录、SQL 查询 | "午餐 35 元"、"本月支出统计" |
| **✅ 待办** | 任务管理、主题分组 | "添加待办"、"完成任务" |
| **🏥 健康** | 血压/心率/体重等 | "血压 120/80"、"睡眠 7 小时" |
| **📝 日志** | 自由记录、搜索 | "今天跑步 5km"、"搜索火锅" |

## 🔌 MCP 支持

| 类型 | 数量 | 说明 |
|------|------|------|
| **Tools** | 10 | 记录/查询各类数据 |
| **Resources** | 3 | 今日/周摘要 |
| **Prompts** | 4 | 每日回顾、财务分析等 |

## ⚙️ CLI 选项

```bash
daily-mcp [OPTIONS]

  -d, --db-path PATH   数据库路径 (默认: ~/.daily-mcp/data.db)
  -v, --verbose        日志级别 (-v: INFO, -vv: DEBUG)
  --log-file PATH      日志文件
  --version            版本号
```

## 📚 文档

- [功能详解](docs/features.md) - 各模块详细说明和示例
- [MCP 协议](docs/mcp-protocol.md) - Tools/Resources/Prompts 完整列表
- [配置指南](docs/configuration.md) - CLI 参数和数据存储
- [开发指南](docs/development.md) - 环境搭建和代码规范
- [项目架构](docs/architecture.md) - 模块设计和扩展方式

## 🛠️ 开发

```bash
git clone https://github.com/peng/daily-mcp.git
cd daily-mcp
pip install -e ".[dev]"

make test      # 运行测试
make lint      # 代码检查
make check     # 全部检查
```

## 📄 License

[MIT](LICENSE)
