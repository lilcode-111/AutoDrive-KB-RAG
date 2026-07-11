# Week10 Day1：FastAPI 服务骨架搭建

## 1. 今日目标

为 `AutoDrive-KB-RAG` 项目新增 FastAPI 后端服务骨架，让项目从本地脚本 demo 开始升级为可通过 API 调用的工程服务。

今日不实现文档解析、上传和切块逻辑，只完成基础服务入口和占位接口。

---

## 2. 为什么做 FastAPI

Week9 的 RAG 流程主要通过脚本运行：

```bash
python examples/run_day4_prompt_demo.py
```

这种方式适合验证逻辑，但不够工程化。

FastAPI 的作用是为后续 RAG 功能提供统一入口：

```text
上传文档
→ 解析文档
→ 清洗文本
→ 文档切块
→ 检索
→ 构造 Prompt
→ 返回结果
```

因此 Day1 的重点是先把 API 服务跑起来。

---

## 3. 新增目录结构

```text
AutoDrive-KB-RAG/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       ├── health.py
│       └── documents.py
├── requirements.txt
└── docs/
    └── week10_day1_fastapi_skeleton.md
```

文件作用：

| 文件 | 作用 |
|---|---|
| `app/main.py` | FastAPI 主入口 |
| `app/schemas.py` | 定义接口返回格式 |
| `app/routers/health.py` | 健康检查和项目信息接口 |
| `app/routers/documents.py` | 文档模块占位接口 |
| `requirements.txt` | 项目依赖 |

---

## 4. 依赖

`requirements.txt`：

```txt
fastapi
uvicorn[standard]
python-multipart
pydantic
```

安装命令：

```bash
pip install -r requirements.txt
```

---

## 5. 今日实现的接口

### 根路径接口

```text
GET /
```

作用：返回项目入口信息。

---

### 健康检查接口

```text
GET /health
```

作用：确认 FastAPI 服务是否正常运行。

返回示例：

```json
{
  "status": "ok",
  "project": "AutoDrive-KB-RAG",
  "week": "week10",
  "message": "FastAPI service is running"
}
```

---

### 项目信息接口

```text
GET /api/v1/info
```

作用：返回当前项目阶段、已完成模块和后续模块。

---

### 文档服务状态接口

```text
GET /api/v1/documents/status
```

作用：确认文档模块 router 已经接入。

---

### 支持文件类型接口

```text
GET /api/v1/documents/supported-file-types
```

作用：返回后续计划支持的文件类型。

```json
{
  "supported_file_types": [".md", ".txt", ".json", ".pdf"]
}
```

---

## 6. 核心代码关系

```text
schemas.py
定义接口返回的数据结构

health.py / documents.py
定义不同模块的接口

main.py
创建 FastAPI 主应用，并注册各个 router

uvicorn
启动 main.py 中的 app 对象
```

运行入口：

```bash
uvicorn app.main:app --reload
```

其中：

```text
app.main:app
= app/main.py 文件中的 app 对象
```

---

## 7. 启动与测试

启动服务：

```bash
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

测试接口：

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/documents/status
```

---

## 8. 今日遇到的问题

### 问题 1：`health.router` 找不到

报错：

```text
AttributeError: module 'app.routers.health' has no attribute 'router'
```

原因：`health.py` 中没有正确保存或定义：

```python
router = APIRouter(tags=["health"])
```

解决：检查文件路径和代码是否保存。

---

### 问题 2：Swagger 只显示 `"string"`

Swagger 中的：

```json
{
  "status": "string",
  "project": "string"
}
```

只是响应模型示例，不是真实返回值。

真实返回值需要点击 `Try it out -> Execute`，或直接访问 `/health`。

---

## 9. 今日完成情况

- [x] 创建 FastAPI 服务目录 `app/`
- [x] 编写 `main.py`
- [x] 编写 `schemas.py`
- [x] 编写 `health.py`
- [x] 编写 `documents.py`
- [x] 新增 `requirements.txt`
- [x] 成功启动服务
- [x] 打开 `/docs`
- [x] 理解 `app`、`router`、`schema`、`prefix`、`tags`

---

## 10. 今日总结

Week10 Day1 完成了 AutoDrive-KB-RAG 的 FastAPI 服务骨架。

当前项目已经具备基础 API 服务入口：

```text
GET /
GET /health
GET /api/v1/info
GET /api/v1/documents/status
GET /api/v1/documents/supported-file-types
```

这一步为后续接入 Markdown/TXT 解析、JSON 评价结果解析、PDF 解析和 upload-and-chunk API 打下基础。

---

## 11. 下一步

Week10 Day2 将实现：

```text
Markdown / TXT 文档解析
文本清洗
POST /api/v1/documents/parse
```

目标流程：

```text
读取 Markdown/TXT 文件
→ 提取文本
→ 清洗空行和空格
→ 返回文本长度和 preview
```


