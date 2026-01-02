# 开发指南

## 环境准备

### 前置要求

- Python 3.10+
- Git

### 克隆项目

```bash
git clone https://github.com/cnut/daily-mcp.git
cd daily-mcp
```

### 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 安装依赖

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install
```

## 常用命令

项目提供 Makefile 简化常用操作：

```bash
# 运行测试
make test

# 代码检查
make lint

# 代码格式化
make format

# 类型检查
make typecheck

# 运行所有检查
make check

# 清理缓存文件
make clean
```

或直接使用工具：

```bash
# 测试
pytest tests/ -v

# Ruff 检查
ruff check src/ tests/

# Ruff 格式化
ruff format src/ tests/

# MyPy 类型检查
mypy src/
```

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 编写代码

遵循项目代码规范（见下文）。

### 3. 编写测试

在 `tests/` 目录添加对应测试：

```python
# tests/test_your_feature.py
import pytest
from daily_mcp.tools import your_module

def test_your_function(db):
    result = your_module.your_function(db, ...)
    assert "expected" in result
```

### 4. 运行检查

```bash
make check
```

### 5. 提交代码

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
git add .
git commit -m "feat: add your feature description"
```

### 6. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

## 代码规范

### Python 版本

使用 Python 3.10+ 特性：

```python
# 类型注解使用 | 而非 Union
def func(value: str | None = None) -> dict[str, Any]:
    ...

# match 语句
match name:
    case "option1":
        ...
    case _:
        ...
```

### 类型注解

所有函数必须有完整的类型注解：

```python
def record_expense(
    db: Database,
    amount: float,
    category: str,
    note: str | None = None,
    date: str | None = None,
) -> str:
    """Record an expense."""
    ...
```

### 文档字符串

公共 API 必须有 docstring：

```python
def query_finance(db: Database, sql: str) -> str:
    """
    Execute SQL query on finance table.

    Args:
        db: Database instance
        sql: SQL SELECT query

    Returns:
        Query results as formatted string

    Raises:
        ValueError: If SQL is not a SELECT query
    """
    ...
```

### 导入顺序

由 Ruff 自动管理，遵循 isort 规范：

```python
# 标准库
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

# 第三方库
from pydantic import BaseModel, Field

# 本地模块
from daily_mcp.db import Database
```

## 项目结构

```
daily-mcp/
├── src/daily_mcp/
│   ├── __init__.py       # 包入口
│   ├── server.py         # MCP 服务器入口，CLI
│   ├── handlers.py       # MCP 处理器注册
│   ├── schemas.py        # Pydantic 模型
│   ├── db.py             # 数据库封装
│   ├── logging.py        # 日志配置
│   ├── resources.py      # MCP Resources
│   ├── prompts.py        # MCP Prompts
│   └── tools/            # 工具实现
│       ├── __init__.py
│       ├── finance.py
│       ├── todo.py
│       ├── health.py
│       └── diary.py
├── tests/
│   ├── conftest.py       # pytest fixtures
│   └── test_*.py
├── docs/                 # 文档
├── pyproject.toml        # 项目配置
└── Makefile
```

## 添加新工具

### 1. 定义 Schema

在 `schemas.py` 添加 Pydantic 模型：

```python
class YourToolParams(BaseModel):
    """Schema for your tool."""
    
    param1: str = Field(..., description="Parameter description")
    param2: int = Field(10, description="Optional with default")
```

在 `DailyTools` 枚举添加工具名：

```python
class DailyTools(str, Enum):
    # ...existing...
    YOUR_TOOL = "your_tool"
```

### 2. 实现工具

在 `tools/` 目录创建或修改模块：

```python
# tools/your_module.py
from daily_mcp.db import Database

def your_tool(db: Database, param1: str, param2: int = 10) -> str:
    """Tool implementation."""
    # 实现逻辑
    return "Result message"
```

### 3. 注册工具

在 `handlers.py` 的 `register_tools` 函数中添加：

```python
Tool(
    name=DailyTools.YOUR_TOOL,
    description="Your tool description",
    inputSchema=YourToolParams.model_json_schema(),
),
```

在 `_dispatch_tool` 函数中添加处理：

```python
DailyTools.YOUR_TOOL: lambda d, a: your_module.your_tool(d, **a),
```

### 4. 添加测试

```python
# tests/test_your_module.py
def test_your_tool(db):
    result = your_module.your_tool(db, "value", 20)
    assert "expected" in result
```

## 测试

### 运行测试

```bash
# 全部测试
pytest tests/ -v

# 单个文件
pytest tests/test_finance.py -v

# 单个测试
pytest tests/test_finance.py::test_record_expense -v

# 带覆盖率
pytest tests/ --cov=src/daily_mcp --cov-report=html
```

### Fixtures

`conftest.py` 提供的 fixtures：

```python
@pytest.fixture
def db(tmp_path):
    """提供临时数据库实例"""
    ...

@pytest.fixture
def sample_data(db):
    """预填充测试数据"""
    ...
```

## 发布

### 版本号

遵循 [Semantic Versioning](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- 在 `pyproject.toml` 和 `__init__.py` 中更新

### 构建

```bash
pip install build
python -m build
```

### 发布到 PyPI

```bash
pip install twine
twine upload dist/*
```
