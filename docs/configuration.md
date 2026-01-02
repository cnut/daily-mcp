# 配置指南

## CLI 参数

```bash
daily-mcp [OPTIONS]

Options:
  -d, --db-path PATH      数据库文件路径 (默认: ~/.daily-mcp/data.db)
  --diary-path PATH       日记目录路径 (默认: ~/.daily-mcp/diary)
  -v, --verbose           日志级别 (-v: INFO, -vv: DEBUG)
  --log-file PATH         日志输出文件
  --version               显示版本号
  --help                  显示帮助信息
```

## Claude Desktop 配置

配置文件位置：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 基础配置

```json
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp"
    }
  }
}
```

### 使用 uvx（推荐）

无需预先安装，自动管理依赖：

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

### 自定义数据库和日记路径

```json
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp",
      "args": ["--db-path", "/path/to/my-data.db", "--diary-path", "/path/to/diary"]
    }
  }
}
```

### 开启详细日志

```json
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp",
      "args": ["-vv", "--log-file", "/tmp/daily-mcp.log"]
    }
  }
}
```

## 数据存储

### 默认目录结构

```
~/.daily-mcp/
├── data.db          # SQLite 数据库（财务、待办、健康）
└── diary/           # 日记文件目录
    ├── 2024-01-15.json
    ├── 2024-01-16.json
    └── ...
```

### 数据库表

| 表名 | 用途 |
|------|------|
| `finance` | 收支记录 |
| `todos` | 待办任务 |
| `health` | 健康指标 |

### 备份数据

SQLite 是单文件数据库，直接复制即可备份：

```bash
cp ~/.daily-mcp/data.db ~/backup/daily-mcp-$(date +%Y%m%d).db
```

### 迁移数据

将数据迁移到新位置：

```bash
# 1. 复制数据文件
cp -r ~/.daily-mcp /new/path/daily-mcp

# 2. 更新配置使用新路径
{
  "mcpServers": {
    "daily-mcp": {
      "command": "daily-mcp",
      "args": ["--db-path", "/new/path/daily-mcp/data.db"]
    }
  }
}
```

## 日志级别

| 级别 | 参数 | 输出内容 |
|------|------|----------|
| WARN | (默认) | 仅警告和错误 |
| INFO | `-v` | 工具调用、资源读取 |
| DEBUG | `-vv` | 详细参数、SQL 查询 |

## 环境变量

目前不支持环境变量配置，所有配置通过 CLI 参数传递。

## 故障排除

### 查看详细日志

```bash
daily-mcp -vv --log-file ./debug.log
```

### 检查数据库

```bash
sqlite3 ~/.daily-mcp/data.db ".tables"
sqlite3 ~/.daily-mcp/data.db "SELECT * FROM finance LIMIT 5"
```

### 重置数据库

```bash
rm ~/.daily-mcp/data.db
# 重启 daily-mcp 会自动创建新数据库
```
