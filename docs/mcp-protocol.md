# MCP 协议支持

Daily MCP 完整实现了 [Model Context Protocol](https://modelcontextprotocol.io/) 的三大核心功能：**Tools**、**Resources** 和 **Prompts**。

## Tools (工具)

工具是 Agent 可以调用的函数，用于执行具体操作。

### 完整工具列表

| 工具名 | 描述 | 主要参数 |
|--------|------|----------|
| `record_expense` | 记录支出 | `amount`, `category`, `note`, `date` |
| `record_income` | 记录收入 | `amount`, `source`, `note`, `date` |
| `query_finance` | SQL 查询财务数据 | `sql` |
| `add_todo` | 添加待办 | `content`, `topic`, `due_date` |
| `complete_todo` | 完成待办 | `todo_id` 或 `content_match` |
| `list_todos` | 列出待办 | `topic`, `status` |
| `record_health` | 记录健康指标 | `metric_type`, `value`, `unit`, `note` |
| `query_health` | 查询健康数据 | `metric_type`, `days`, `sql` |
| `add_daily_log` | 添加日志 | `content`, `date` |
| `search_daily_log` | 搜索日志 | `keyword`, `start_date`, `end_date` |

### 工具参数 Schema

所有工具参数使用 Pydantic 定义，自动生成 JSON Schema：

```python
class RecordExpense(BaseModel):
    amount: float = Field(..., description="Expense amount", gt=0)
    category: str = Field(..., description="Expense category")
    note: str | None = Field(None, description="Optional note")
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
```

---

## Resources (资源)

资源是 Agent 可以读取的动态数据，无需调用工具即可获取。

### 可用资源

| URI | 名称 | 描述 |
|-----|------|------|
| `daily://summary/today` | Today's Summary | 今日活动摘要 |
| `daily://summary/weekly` | Weekly Summary | 最近 7 天摘要 |
| `daily://summary/YYYY-MM-DD` | Date Summary | 指定日期摘要 |

### 资源内容示例

`daily://summary/today` 返回内容：

```
📅 Daily Summary for 2024-01-15

💰 Finance:
- Expenses: ¥235.00 (3 transactions)
- Income: ¥0.00

✅ Todos:
- Completed: 2
- Pending: 5
- Overdue: 1

🏥 Health:
- Blood Pressure: 120/80
- Weight: 70.5 kg

📝 Daily Logs: 3 entries
```

---

## Prompts (提示词)

预设提示词模板，引导 Agent 执行复杂的多步骤任务。

### 可用提示词

| 名称 | 描述 | 参数 |
|------|------|------|
| `daily-review` | 每日回顾与总结 | `date` (可选，默认今天) |
| `weekly-planning` | 周计划制定 | `focus` (可选，关注领域) |
| `financial-analysis` | 财务分析报告 | `period` (必填，如 "last month") |
| `health-checkup` | 健康数据检查 | `metric_type`, `days` |

### 使用方式

在 Claude Desktop 中，可以通过 `/` 命令调用提示词：

```
/daily-review date:2024-01-15
/financial-analysis period:last month
/health-checkup metric_type:blood_pressure days:30
```

### 提示词模板示例

**daily-review** 模板：

```
You are helping the user review their day. Based on the provided date, please:

1. **Summarize the day's activities** using the available tools:
   - Check finance records (income/expenses)
   - Review completed and pending todos
   - Look at health metrics recorded
   - Read daily log entries

2. **Provide insights**:
   - Spending patterns or unusual expenses
   - Task completion rate
   - Health trends or concerns

3. **Suggest improvements**:
   - Budget recommendations if overspending
   - Prioritize overdue tasks
   - Health reminders based on missing metrics

Date to review: {date}
```

---

## 技术实现

### 架构图

```
┌──────────────────────────────────────────┐
│           AI Agent (Claude Desktop)      │
└─────────────────┬────────────────────────┘
                  │ MCP Protocol (JSON-RPC)
┌─────────────────▼────────────────────────┐
│              Daily MCP Server            │
├──────────────────────────────────────────┤
│  @server.list_tools()                    │
│  @server.call_tool()                     │
│  @server.list_resources()                │
│  @server.read_resource()                 │
│  @server.list_prompts()                  │
│  @server.get_prompt()                    │
├──────────────────────────────────────────┤
│              handlers.py                 │
│  - register_tools()                      │
│  - register_resources()                  │
│  - register_prompts()                    │
└──────────────────────────────────────────┘
```

### 相关文件

| 文件 | 职责 |
|------|------|
| `handlers.py` | MCP 协议处理器注册 |
| `schemas.py` | Pydantic 模型定义 |
| `resources.py` | Resource 内容生成 |
| `prompts.py` | Prompt 模板定义 |
