# 项目架构

## 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                    AI Agent                              │
│              (Claude Desktop, etc.)                      │
└─────────────────────────┬────────────────────────────────┘
                          │ MCP Protocol (JSON-RPC over stdio)
┌─────────────────────────▼────────────────────────────────┐
│                   Daily MCP Server                       │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Tools     │  │  Resources  │  │   Prompts   │      │
│  │  (10 个)    │  │   (3 个)    │  │   (4 个)    │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│         │                │                │              │
│  ┌──────▼────────────────▼────────────────▼──────┐      │
│  │              handlers.py                       │      │
│  │  - register_tools()                           │      │
│  │  - register_resources()                       │      │
│  │  - register_prompts()                         │      │
│  └──────────────────────┬────────────────────────┘      │
│                         │                                │
│  ┌──────────────────────▼────────────────────────┐      │
│  │                 tools/                         │      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │      │
│  │  │ finance  │ │   todo   │ │  health  │      │      │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘      │      │
│  │       │            │            │             │      │
│  │  ┌────▼────────────▼────────────▼─────┐      │      │
│  │  │             diary                  │      │      │
│  │  └────────────────────────────────────┘      │      │
│  └──────────────────────┬────────────────────────┘      │
│                         │                                │
├─────────────────────────▼────────────────────────────────┤
│                      db.py                               │
│                   (SQLite 封装)                          │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│                   Local Storage                          │
│  ┌─────────────────┐  ┌─────────────────────────┐       │
│  │    data.db      │  │     diary/*.json        │       │
│  │   (SQLite)      │  │      (Diary)            │       │
│  └─────────────────┘  └─────────────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

## 模块职责

### 入口层

| 模块 | 文件 | 职责 |
|------|------|------|
| CLI | `server.py` | 命令行入口，参数解析，启动服务器 |
| 包入口 | `__init__.py` | 导出公共 API，版本号 |

### 协议层

| 模块 | 文件 | 职责 |
|------|------|------|
| 处理器 | `handlers.py` | 注册 MCP 协议的 Tools/Resources/Prompts |
| Schema | `schemas.py` | Pydantic 模型，工具参数定义 |
| Resources | `resources.py` | 动态资源内容生成 |
| Prompts | `prompts.py` | 提示词模板定义 |

### 业务层

| 模块 | 文件 | 职责 |
|------|------|------|
| Finance | `tools/finance.py` | 收支记录、查询 |
| Todo | `tools/todo.py` | 待办管理 |
| Health | `tools/health.py` | 健康指标记录 |
| Diary | `tools/diary.py` | 日记记录、搜索 |

### 基础设施层

| 模块 | 文件 | 职责 |
|------|------|------|
| Database | `db.py` | SQLite 连接、表初始化、查询执行 |
| Logging | `logging.py` | 日志配置、格式化 |

## 数据流

### 工具调用流程

```
Agent 发送 call_tool 请求
        │
        ▼
handlers.py: call_tool()
        │
        ▼
_dispatch_tool() 路由到具体工具
        │
        ▼
tools/*.py: 执行业务逻辑
        │
        ▼
db.py: 数据库操作
        │
        ▼
返回结果给 Agent
```

### 资源读取流程

```
Agent 发送 read_resource 请求
        │
        ▼
handlers.py: read_resource()
        │
        ▼
_resolve_resource() 解析 URI
        │
        ▼
resources.py: 生成摘要内容
        │
        ▼
返回结果给 Agent
```

## 设计原则

### 1. 单一职责

每个模块只负责一个功能：

- `db.py` 只负责数据库操作
- `handlers.py` 只负责 MCP 协议处理
- `tools/*.py` 只负责具体业务逻辑

### 2. 依赖注入

Database 实例通过参数传递，便于测试：

```python
def record_expense(db: Database, amount: float, ...) -> str:
    # db 由调用方注入
    ...
```

### 3. 类型安全

使用 Pydantic 进行参数验证：

```python
class RecordExpense(BaseModel):
    amount: float = Field(..., gt=0)  # 自动验证 > 0
```

### 4. 可测试性

所有模块可独立测试：

```python
def test_record_expense(db):  # db 是 pytest fixture
    result = finance.record_expense(db, 100, "food")
    assert "Recorded" in result
```

## 扩展点

### 添加新工具

1. 在 `schemas.py` 定义参数 Schema
2. 在 `tools/` 实现业务逻辑
3. 在 `handlers.py` 注册工具

### 添加新资源

1. 在 `resources.py` 添加内容生成函数
2. 在 `handlers.py` 的 `list_resources` 添加资源定义
3. 在 `_resolve_resource` 添加 URI 解析

### 添加新提示词

1. 在 `prompts.py` 定义模板和元数据
2. 在 `handlers.py` 的 `_apply_prompt_defaults` 添加默认值处理

## 依赖关系

```
server.py
    └── handlers.py
            ├── schemas.py
            ├── resources.py
            ├── prompts.py
            └── tools/
                    ├── finance.py
                    ├── todo.py
                    ├── health.py
                    └── diary.py
                            └── db.py
                                    └── logging.py
```

核心依赖：
- `mcp` - MCP Python SDK
- `click` - CLI 框架
- `pydantic` - 数据验证
