# AutoDrive-KB-RAG

## 1. 项目简介

AutoDrive-KB-RAG 是一个面向自动驾驶评价场景的 RAG 知识库问答项目。

本项目不是普通 PDF 聊天机器人，而是围绕自动驾驶评价资料进行检索和问答，主要处理以下类型的数据：

```text
1. 自动驾驶评价指标说明
2. 评价 JSON 结果
3. 事故案例和失败原因说明
```

当前项目已经完成 RAG 前半段链路：

```text
原始资料
→ Chunking 文档切块
→ Toy Retrieval TopK 检索
→ Prompt Building 构造 RAG Prompt
```

后续会继续接入 Embedding 模型、FAISS / Milvus、FastAPI 和 LLM 生成链。

---

## 2. 项目目标

本项目的目标是构建一个面向自动驾驶评价资料的知识库系统，用于辅助理解：

```text
TP / FP / FN 的定义
Precision / Recall 的计算方式
评价 JSON 字段含义
某个 scenario 被判定为 FP / FN 的原因
事故案例和失败原因
```

示例问题：

```text
什么是 FP 误检？
什么是 FN 漏检？
Recall 怎么计算？
scenario_001 为什么被判定为 FN？
scenario_002 为什么是 FP？
```

---

## 3. 当前项目结构

```text
week9_autoDrive_RAG/
├── data/
│   ├── samples/
│   │   ├── metric_doc.md
│   │   ├── evaluation_result.json
│   │   └── accident_case.md
│   └── processed/
│       └── day2_chunks.json
├── examples/
│   ├── run_day2_chunking_demo.py
│   ├── run_day3_retrieval_demo.py
│   └── run_day4_prompt_demo.py
├── src/
│   ├── chunking/
│   │   └── simple_chunker.py
│   ├── retrieval/
│   │   └── toy_retriever.py
│   └── prompt/
│       └── prompt_builder.py
├── week9.md/
│   ├── day1_rag_overview.md
│   ├── day2_chunking_summary.md
│   ├── day3_embedding_retrieval_summary.md
│   └── day4_prompt_building_summary.md
└── README.md
```

---

## 4. 数据说明

当前样例数据位于：

```text
data/samples/
```

包括：

```text
metric_doc.md
```

用于说明 TP、FP、FN、Precision、Recall 等评价指标。

```text
evaluation_result.json
```

用于模拟自动驾驶评价结果，包含 scenario、objects、tp_count、fp_count、fn_count 和 failure_reason。

```text
accident_case.md
```

用于说明具体失败案例，例如路口车辆漏检和高速场景误检行人。

---

## 5. Day 2：Chunking 文档切块

### 5.1 功能

Day 2 实现了文档切块模块：

```text
src/chunking/simple_chunker.py
```

支持三类切块方式：

| 数据类型 | 切块方式 | 原因 |
|---|---|---|
| Markdown 指标文档 | 按标题切块 | 每个标题小节通常是完整语义单元 |
| Markdown 事故案例 | 按标题切块 | 每个 Case 通常可以独立分析 |
| 评价 JSON | 按 scenario_id 切块 | 一个 scenario 对应一次完整评价结果 |
| 普通 txt 文本 | 固定窗口切块 | 无结构信息时的兜底方案 |

### 5.2 运行方式

```bash
python examples/run_day2_chunking_demo.py
```

运行后生成：

```text
data/processed/day2_chunks.json
```

该文件是后续 Retriever 检索的知识库输入。

---

## 6. Day 3：Toy Retrieval 检索

### 6.1 功能

Day 3 实现了一个最小版 Toy Retriever：

```text
src/retrieval/toy_retriever.py
```

当前检索流程：

```text
chunk text
→ tokenize()
→ text_to_vector()
→ cosine_similarity()
→ TopK chunks
```

目前使用的是简单词频向量和余弦相似度。

这不是最终工业级检索方案，但可以帮助理解 RAG 的核心流程：

```text
用户 query 和 chunk 都变成向量，然后计算相似度，返回最相关的 TopK chunks。
```

### 6.2 运行方式

```bash
python examples/run_day3_retrieval_demo.py
```

示例 query：

```text
什么是 FP 误检？
什么是 FN 漏检？
Recall 怎么计算？
scenario_001 为什么被判定为 FN？
scenario_002 为什么是 FP？
```

---

## 7. Day 4：Prompt Building

### 7.1 功能

Day 4 实现了 Prompt Builder：

```text
src/prompt/prompt_builder.py
```

它的作用是把 Retriever 返回的 TopK chunks 整理成可以交给 LLM 的 Prompt。

核心流程：

```text
query
→ retriever.search(query)
→ TopK chunks
→ build_rag_prompt(query, retrieved_chunks)
→ final prompt
```

Prompt 中包含：

```text
1. 角色设定
2. 回答要求
3. TopK 参考资料
4. 用户问题
5. 输出格式约束
```

### 7.2 运行方式

```bash
python examples/run_day4_prompt_demo.py
```

当前只是生成 Prompt，暂时不调用 LLM。

---

## 8. 当前能力

当前项目已经具备以下能力：

```text
1. 读取自动驾驶评价资料
2. 将 Markdown 和 JSON 切成 chunks
3. 保存统一格式的 chunk 数据
4. 输入 query 后返回 TopK 相关 chunks
5. 根据 TopK chunks 构造 RAG Prompt
```

也就是说，项目已经完成了 RAG 前半段：

```text
Document Processing
→ Retrieval
→ Prompt Construction
```

---

## 9. 当前局限

当前项目还只是 Week 9 的学习版 Demo，存在以下局限：

```text
1. 还没有接入真正的 embedding 模型
2. 还没有接入 FAISS / Milvus 等向量数据库
3. 还没有接入 LLM 生成答案
4. 中文分词目前只是按单字切分
5. Toy Retriever 只适合理解流程，不适合作为最终检索方案
```

---

## 10. 后续计划

后续可以按以下方向继续扩展：

```text
1. 接入 sentence-transformers 或 bge / gte / Qwen embedding
2. 使用 FAISS 或 Milvus 存储向量
3. 接入 LLM，完成 Prompt → Answer
4. 使用 FastAPI 封装上传、检索和问答接口
5. 增加检索评测，例如 Recall@K
6. 增加 Docker 部署
```

下一阶段目标：

```text
输入问题
→ 检索 TopK chunks
→ 构造 Prompt
→ 调用 LLM
→ 输出带依据的答案
```

---

## 11. 项目定位

AutoDrive-KB-RAG 的定位不是普通文档问答，而是面向自动驾驶评价场景的知识库系统。

项目特点：

```text
1. 数据来自自动驾驶评价场景
2. 支持指标文档、评价 JSON、事故案例
3. 检索结果可以和 scenario_id、metric_name、scene_type 等 metadata 结合
4. 后续可以作为 AutoDrive-Log-Agent 的知识检索工具
```

这个项目可以和自动驾驶仿真评价、数据闭环、AI Agent、RAG 应用岗位结合。