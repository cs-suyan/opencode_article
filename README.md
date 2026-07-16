# opencode_article

AI 根据热点新闻自动生成 100% 原创自媒体爆款文章。

## 功能

- 自动采集微博、百度、今日头条热搜 Top 10
- 跨平台去重，随机选题，避免同一天重复生成
- 调用大模型 API 生成自媒体风格文章
- 自动配图（从 Bing 搜索匹配图片）
- 按日期自动归档

## 目录结构

```
├── main.py                       # 入口文件
├── config.toml                   # 配置文件
├── .env                          # 环境变量（敏感信息，已 gitignore）
├── .env.example                  # 环境变量模板
├── pyproject.toml                # 项目元数据
├── requirements.txt              # 依赖清单
├── src/
│   ├── __init__.py
│   ├── article_generator.py      # 文章生成（调用 LLM）
│   ├── file_saver.py             # 文件保存与去重
│   ├── image_fetcher.py          # Bing 图片搜索
│   ├── news_collector.py         # 多平台热搜采集
│   └── utils.py                  # 工具函数
├── tests/
│   ├── __init__.py
│   ├── test_article_generator.py
│   ├── test_file_saver.py
│   └── test_utils.py
└── output/                       # 生成的文章（按日期归档）
    └── YYYY-MM-DD/
        ├── 标题1.md
        └── 标题2.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

**方式一**（推荐）：使用 `.env` 文件

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

**方式二**：直接编辑 `config.toml`

```toml
[llm]
api_key = "sk-your-api-key"
```

### 3. 运行

```bash
python main.py
```

### 4. 定时自动运行（可选）

在 `config.toml` 中启用并设置时间：

```toml
[schedule]
enabled = true
time = "09:00"
```

然后运行：

```bash
python main.py --schedule
```

## 测试

```bash
pytest tests/
```
