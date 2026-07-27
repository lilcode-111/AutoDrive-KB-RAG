# AutoDrive-KB-RAG

## 1. 项目简介

AutoDrive-KB-RAG 是一个面向自动驾驶评价场景的 RAG 知识库问答项目。

项目主要处理以下类型的资料：

```text
1. 自动驾驶评价指标说明
2. 自动驾驶评价 JSON 结果
3. 事故案例与失败原因说明
```

项目目标不是构建普通 PDF 聊天机器人，而是将自动驾驶评价文档、场景结果和指标定义组织成可检索、可追溯的知识库。

---

## 2. 当前能力

项目当前已经打通基础 RAG 问答链路：

```text
文档上传
→ 文档解析
→ 文档切块
→ SentenceTransformer Embedding
→ InMemoryVectorIndex
→ TopK 语义检索
→ Grounded Prompt
→ LLM Client
→ Answer + Sources
```

目前支持：

```text
1. 上传 Markdown、JSON、TXT 和 PDF 文档
2. 将文档解析并切分为统一格式的 chunks
3. 使用 SentenceTransformer 生成语义向量
4. 使用内存向量索引完成 TopK 检索
5. 构造只允许依据检索资料回答的 Prompt
6. 使用 FakeLLMClient 验证完整 RAG 链路
7. 使用 OpenAICompatibleLLMClient 接入真实生成模型
8. 返回答案以及原始检索来源
9. 无检索资料时返回 insufficient_context
10. 通过 FastAPI 暴露上传、检索和问答接口
```

---

## 3. 项目结构

```text
AutoDrive-KB-RAG/
├── app/
│   ├── main.py
│   └── routers/
│       ├── health.py
│       ├── documents.py
│       ├── retrieval.py
│       └── rag.py
├── data/
│   └── samples/
│       ├── metric_doc.md
│       ├── evaluation_result.json
│       └── accident_case.md
├── src/
│   ├── chunking/
│   │   └── simple_chunker.py
│   ├── parsing/
│   │   └── document_parser.py
│   ├── embeddings/
│   │   ├── embedding_client.py
│   │   └── sentence_transformer_client.py
│   ├── retrieval/
│   │   ├── retrieval_service.py
│   │   └── vector_index.py
│   ├── prompt/
│   │   └── prompt_builder.py
│   ├── llm/
│   │   ├── llm_client.py
│   │   ├── fake_llm_client.py
│   │   └── openai_compatible_llm_client.py
│   └── rag/
│       └── rag_service.py
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 4. 核心模块

### 4.1 文档处理

文档上传后，系统会依次完成：

```text
文件类型识别
→ 文本解析
→ metadata 提取
→ chunk 切分
```

当前样例数据位于：

```text
data/samples/
```

包括：

| 文件 | 作用 |
|---|---|
| `metric_doc.md` | TP、FP、FN、Precision、Recall 等指标说明 |
| `evaluation_result.json` | 自动驾驶场景评价结果 |
| `accident_case.md` | 事故案例和失败原因说明 |

### 4.2 Embedding 与检索

当前使用：

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Embedding 向量维度为：

```text
384
```

检索流程：

```text
用户 query
→ query embedding
→ 与已索引 chunk 计算相似度
→ 按 score 排序
→ 返回 TopK chunks
```

### 4.3 PromptBuilder

PromptBuilder 将用户问题与 TopK 检索结果组合成 Grounded Prompt。

Prompt 约束包括：

```text
1. 只能依据提供的参考资料回答
2. 不得编造资料中不存在的信息
3. 资料不足时明确返回无法确定
4. 使用 [S1]、[S2] 等编号引用证据
5. 保留 source、chunk_id 和 metadata 等来源信息
```

### 4.4 RAGService

RAGService 负责组织完整业务流程：

```text
query
→ RetrievalService.search()
→ build_rag_prompt()
→ LLMClient.generate()
→ answer + sources
```

当没有检索结果时，系统不会继续调用 LLM，而是直接返回：

```json
{
  "answer": "根据当前资料无法确定。",
  "answer_status": "insufficient_context",
  "source_count": 0,
  "sources": []
}
```

### 4.5 LLM Client

项目定义了统一接口：

```python
generate(prompt: str) -> str
```

当前包含两种实现：

| Client | 作用 |
|---|---|
| `FakeLLMClient` | 返回固定答案，用于测试和本地开发 |
| `OpenAICompatibleLLMClient` | 调用 OpenAI-compatible Chat Completions API |

---

## 5. 安装

建议使用独立 Python 或 Conda 环境。

```bash
conda activate ai-roadmap
python -m pip install -r requirements.txt
```

确认主要依赖：

```bash
python -c "import fastapi"
python -c "import sentence_transformers"
python -c "from openai import OpenAI"
```

首次使用 SentenceTransformer 时可能需要下载 Encoder 模型。模型缓存完成后，后续运行会从本地加载。

---

## 6. 环境变量

参考 `.env.example`：

```text
LLM_PROVIDER=fake

OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_BASE_URL=
```

### Fake 模式

```bash
export LLM_PROVIDER=fake
```

Fake 模式不会访问真实生成模型，也不需要 API Key。

### OpenAI-compatible 模式

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="your-model-name"
```

使用第三方兼容服务时，还需要设置：

```bash
export OPENAI_BASE_URL="provider-api-base-url"
```

不要将真实 API Key 写入源代码或提交到 GitHub。

---

## 7. 启动服务

Fake 模式：

```bash
LLM_PROVIDER=fake \
PYTHONPATH=. \
uvicorn app.main:app --reload
```

启动成功后访问：

```text
http://127.0.0.1:8000/docs
```

Swagger 页面可以直接测试上传、检索和 RAG 问答接口。

---

## 8. API 接口

| 方法 | 接口 | 作用 |
|---|---|---|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/v1/retrieval/index-document` | 上传、解析、切块并建立索引 |
| `POST` | `/api/v1/retrieval/search` | TopK 语义检索 |
| `POST` | `/api/v1/retrieval/clear` | 清空内存索引 |
| `GET` | `/api/v1/retrieval/status` | 查看当前索引状态 |
| `POST` | `/api/v1/rag/answer` | 检索并生成答案 |

---

## 9. 快速验证

### 9.1 清空索引

```bash
curl -X POST \
  "http://127.0.0.1:8000/api/v1/retrieval/clear"
```

### 9.2 上传文档

```bash
curl -X POST \
  "http://127.0.0.1:8000/api/v1/retrieval/index-document" \
  -F "file=@data/samples/metric_doc.md"
```

### 9.3 TopK 检索

```bash
curl -X POST \
  "http://127.0.0.1:8000/api/v1/retrieval/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是 FN 漏检？",
    "top_k": 3
  }'
```

### 9.4 RAG 问答

```bash
curl -X POST \
  "http://127.0.0.1:8000/api/v1/rag/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是 FN 漏检？",
    "top_k": 3
  }'
```

Fake 模式下，答案为固定测试文本，但 `sources` 是真实检索结果。

示例响应：

```json
{
  "query": "什么是 FN 漏检？",
  "answer": "这是一个用于验证 RAG API 链路的测试答案。",
  "answer_status": "answered",
  "source_count": 1,
  "sources": [
    {
      "rank": 1,
      "score": 0.4005,
      "chunk_id": "metric_doc_window_0",
      "source": "metric_doc.md",
      "doc_type": "markdown",
      "text": "FN，全称 False Negative，表示真实存在的目标没有被系统检测出来。",
      "metadata": {}
    }
  ]
}
```

---

## 10. 运行测试

运行全部测试：

```bash
LLM_PROVIDER=fake \
PYTHONPATH=. \
pytest -q
```

本地 Week12 验收结果：

```text
38 passed
```

当前 Router 测试会在模块导入阶段初始化真实 Embedding Encoder，因此新的 Python 进程启动测试时可能需要数十秒。

这不是重复下载模型，而是 PyTorch、Transformers 和 Encoder 的初始化成本。

---

## 11. 当前限制

```text
1. 当前使用 InMemoryVectorIndex，服务重启后索引会丢失
2. 多个 Uvicorn Worker 之间无法共享内存索引
3. FakeLLMClient 只用于链路测试，不会生成真实答案
4. OpenAI-compatible Client 已实现，但真实模型调用需要有效配置
5. Embedding Encoder 当前在模块导入阶段初始化，测试启动较慢
6. 当前还没有系统化的 RAG 评测数据集
7. 尚未接入 FAISS、Milvus 等持久化向量数据库
```

---

## 12. 后续计划

下一阶段将重点进行工程化改造：

```text
1. 统一配置管理
2. Embedding 和 Service 延迟初始化
3. 日志与请求耗时记录
4. 统一异常处理
5. Dockerfile 与部署说明
6. README 和接口文档完善
7. 构建 RAG 检索与答案评测集
8. 后续接入持久化向量数据库
```

---

## 13. 项目定位

AutoDrive-KB-RAG 面向自动驾驶评价、仿真测试和数据闭环场景。

项目可以用于辅助理解：

```text
TP / FP / FN 指标
Precision / Recall
评价 JSON 字段
具体 scenario 的失败原因
事故案例与感知问题
```

后续可以作为 AutoDrive-Log-Agent 的知识检索与问答组件。