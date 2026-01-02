# 功能详解

Daily MCP 提供四大核心功能模块，覆盖日常生活的主要记录需求。

## 💰 财务管理 (Finance)

记录日常收支，支持分类和 SQL 查询。

### 功能列表

| 功能 | 说明 |
|------|------|
| 记录支出 | 金额、分类、备注、日期 |
| 记录收入 | 金额、来源、备注、日期 |
| SQL 查询 | 灵活查询历史数据 |

### 示例对话

```
用户：今天午餐花了 35 元，晚上买了本书 68 元
用户：这个月餐饮支出多少？
用户：画一个最近三个月的支出趋势图
```

### 数据表结构

```sql
CREATE TABLE finance (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,        -- 'expense' 或 'income'
    amount REAL NOT NULL,
    category TEXT,             -- 支出分类
    source TEXT,               -- 收入来源
    note TEXT,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### SQL 查询示例

```sql
-- 本月支出总额
SELECT SUM(amount) FROM finance 
WHERE type='expense' AND date >= date('now', 'start of month')

-- 按分类统计支出
SELECT category, SUM(amount) as total FROM finance 
WHERE type='expense' GROUP BY category ORDER BY total DESC

-- 最近 10 笔支出
SELECT * FROM finance WHERE type='expense' ORDER BY date DESC LIMIT 10
```

---

## ✅ 待办任务 (Todo)

管理日常任务，支持主题分组和完成情况追踪。

### 功能列表

| 功能 | 说明 |
|------|------|
| 添加待办 | 内容、主题、截止日期 |
| 完成待办 | 按 ID 或关键词匹配 |
| 列出待办 | 按主题/状态筛选 |

### 示例对话

```
用户：添加一个待办：周五前完成项目报告，主题是工作
用户：完成了"买牛奶"这个任务
用户：看看"健身"主题下还有哪些没完成的
用户：这周完成了多少任务？
```

### 数据表结构

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    topic TEXT,                -- 主题/项目分类
    due_date TEXT,             -- 截止日期
    status TEXT DEFAULT 'pending',  -- 'pending' 或 'completed'
    completed_at TEXT,
    created_at TEXT NOT NULL
);
```

---

## 🏥 健康记录 (Health)

追踪个人健康指标，建立长期健康档案。

### 支持的指标类型

| 指标类型 | 说明 | 示例值 |
|----------|------|--------|
| `blood_pressure` | 血压 | 120/80 |
| `heart_rate` | 心率 | 72 |
| `weight` | 体重 | 70.5 |
| `blood_sugar` | 血糖 | 5.6 |
| `sleep` | 睡眠时长 | 7.5 (小时) |
| `exercise` | 运动 | 跑步 5km |

### 示例对话

```
用户：今天血压 125/82，心率 72
用户：昨晚睡了 7 小时，睡眠质量还行
用户：记录今天跑步 5 公里
用户：画一下最近一个月的血压变化图
用户：最近一周的睡眠情况怎么样？
```

### 数据表结构

```sql
CREATE TABLE health (
    id INTEGER PRIMARY KEY,
    metric_type TEXT NOT NULL,
    value TEXT NOT NULL,
    unit TEXT,
    note TEXT,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

## 📝 日记 (Diary)

自由记录生活点滴，支持关键词搜索和标签分类。

### 功能特点

- **自由文本** - 不限格式，随心记录
- **按日期组织** - 自动按日期归档
- **标签支持** - 可选标签分类（如 work, life, health）
- **关键词搜索** - 快速检索历史记录
- **日期范围查询** - 查看指定时间段的日记

### 示例对话

```
用户：今天早上跑了 5 公里，感觉不错，中午和老王吃了顿火锅
用户：记录一下今天的会议内容，标签是 work
用户：搜索一下上周提到"火锅"的日记
用户：看看上个月的日记
```

### 存储方式

日记以 JSON 文件形式存储在 `~/.daily-mcp/diary/` 目录：

```
~/.daily-mcp/diary/
├── 2024-01-15.json
├── 2024-01-16.json
└── ...
```

每个文件包含当天的所有日记条目：

```json
{
  "date": "2024-01-15",
  "entries": [
    {
      "datetime": "2024-01-15 09:30:45",
      "content": "今天早上跑了 5 公里，感觉不错",
      "tags": ["health"]
    },
    {
      "datetime": "2024-01-15 12:45:30",
      "content": "中午和老王吃了顿火锅，花了 150",
      "tags": null
    }
  ]
}
```
