# Week12：RAG Answer Pipeline

## 1. 本周目标

在 Week11 语义检索链路基础上，完成基础 RAG 问答闭环：

```text
query
→ TopK retrieval
→ grounded prompt
→ LLM generation
→ answer + sources
```

---

## 2. 本周完成内容

### 2.1 LLM 抽象层

新增：

```text
src/llm/llm_client.py
src/llm/fake_llm_client.py
```

统一接口：

```python
generate(prompt: str) -> str
```

`FakeLLMClient` 用于离线测试，支持：

```text
固定答案
记录 last_prompt
记录 call_count
拒绝空 Prompt
```

### 2.2 Grounded Prompt

完善：

```text
src/prompt/prompt_builder.py
```

Prompt 中加入：

```text
query
TopK chunk text
source
chunk_id
rank
score
metadata
[S1]、[S2] 引用编号
```

并明确要求：

```text
只能依据参考资料回答
不得编造
资料不足时返回无法确定
```

### 2.3 RAGService

新增：

```text
src/rag/rag_service.py
```

完成业务链路：

```text
RetrievalService
→ PromptBuilder
→ LLMClient
→ answer + sources
```

无检索资料时：

```text
不调用 LLM
直接返回 insufficient_context
```

### 2.4 RAG API

新增：

```text
POST /api/v1/rag/answer
```

请求示例：

```json
{
  "query": "什么是 FN 漏检？",
  "top_k": 3
}
```

响应包含：

```text
query
answer
answer_status
source_count
sources
```

`sources` 直接复用 Week11 的检索结果结构，没有重复定义 `RAGSource`。

### 2.5 真实 LLM Client

新增：

```text
src/llm/openai_compatible_llm_client.py
```

支持以下配置：

```text
OPENAI_API_KEY
OPENAI_MODEL
OPENAI_BASE_URL
```

单元测试通过注入 Fake SDK Client，避免真实网络请求和 API 费用。

---

## 3. 关键设计

### 3.1 Embedding 与生成模型职责分离

```text
Embedding Model
文本 → 向量 → TopK 检索

Generative LLM
问题 + 检索证据 + 回答约束 → 自然语言答案
```

### 3.2 来源不由 LLM 生成

```text
answer
来自 LLMClient

sources
来自 RetrievalService
```

这样可以避免模型伪造 `source`、`chunk_id` 和 `score`。

### 3.3 无资料回退

```text
没有 TopK 结果
→ 不构造正常 Prompt
→ 不调用 LLM
→ 返回“根据当前资料无法确定”
```

---

## 4. 测试与验收

本周全量测试结果：

```text
38 passed in 33.55s
```

完成 Fake 模式端到端验收：

```text
上传 metric_doc.md
→ 建立 384 维向量索引
→ 查询“什么是 FN 漏检？”
→ 召回 metric_doc.md
→ 返回固定 Fake Answer
→ 返回真实 sources
```

验收结果：

```text
answer_status = answered
source_count = 1
source = metric_doc.md
检索正文包含 FN 定义
```

当前真实生成模型的在线调用尚未作为 Week12 必须验收项，已完成 OpenAI-compatible Client 和无网络单元测试。

---

## 5. 当前问题

```text
1. InMemoryVectorIndex 在服务重启后会丢失
2. Router 测试会初始化真实 Encoder，启动约需数十秒
3. FakeLLMClient 只返回固定答案
4. 真实 LLM 仍需有效 API 配置进行在线验证
5. 尚未建立 RAG 评测数据集
```

---

## 6. Week12 结论

Week12 已完成基础 RAG Answer Pipeline：

```text
文档
→ Chunk
→ Embedding
→ TopK Retrieval
→ Grounded Prompt
→ LLMClient
→ Answer + Sources
```

项目已经从“只返回检索片段”升级为“能够通过 FastAPI 返回答案和依据”的基础 RAG 服务。

---

## 7. 下一周重点

Week13 进入工程化阶段：

```text
配置集中管理
Service 延迟初始化
测试速度优化
统一日志
统一异常处理
Dockerfile
README 与部署流程
```