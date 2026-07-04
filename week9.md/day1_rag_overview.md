# Day 1: RAG Overview

## 1. 什么是 RAG

RAG 全称是 Retrieval-Augmented Generation，中文一般叫检索增强生成。

它的核心思想是：先从外部知识库中检索和用户问题相关的资料，再把这些资料作为上下文交给大模型，让大模型基于证据生成答案。

普通 LLM 问答流程是：

```text
用户问题 → LLM → 答案
```

RAG 问答流程是：

```text
用户问题
→ 检索相关文档
→ 返回 TopK 证据片段
→ 拼接 Prompt
→ LLM 基于证据生成答案
```

因此，RAG 的重点不是简单调用大模型，而是让大模型在外部证据约束下回答问题。

## 2. 为什么需要 RAG

普通 LLM 问答存在三个问题。

### 2.1 知识不一定包含内部资料

大模型训练完成后，参数基本固定。公司内部文档、自动驾驶评价规则、项目 JSON 字段说明、事故案例等内容，不一定存在于模型参数中。

例如用户问：

```text
fp_count 在自动驾驶评价 JSON 中是什么意思？
```

普通 LLM 可能只能根据通用知识猜测。RAG 可以先检索项目文档，再基于文档回答。

### 2.2 容易幻觉

大模型可能生成看起来合理但没有证据的答案。

例如用户问：

```text
scenario_042 为什么被判定为漏检？
```

如果模型没有看到真实评价 JSON，它可能会回答“可能是遮挡、传感器噪声或光照变化”，但这不一定是事实。

RAG 的目标是让模型基于检索到的证据回答，例如：

```text
根据 scenario_042 的评价 JSON，object_id=17 在 3.2s 到 4.1s 之间没有匹配到检测框，因此被统计为 FN。
```

这种回答更适合工程问题定位。

### 2.3 上下文长度有限

工程资料通常很多，不能全部放进 Prompt。RAG 通过检索，只选择和当前问题最相关的文档片段，减少无关信息干扰。

## 3. RAG 的核心流程

RAG 的基本流程是：

```text
Documents
→ Chunking
→ Embedding
→ Vector Database
→ Retriever
→ Prompt
→ LLM
→ Answer
```

### 3.1 Documents

Documents 是原始资料来源。

在 AutoDrive-KB-RAG 项目中，Documents 可以包括：

* 自动驾驶评价指标说明
* 评价 JSON 样例
* 事故案例说明
* TP / FP / FN 判定规则
* 感知、预测、规划评价说明
* 实习中抽象出的脱敏评价流程文档

### 3.2 Chunking

Chunking 是文档切块。

由于文档通常较长，不能直接整篇送入向量库或 Prompt，因此需要切成较小的片段。

例如一份指标文档可以切成：

```text
chunk_1: TP 定义
chunk_2: FP 定义
chunk_3: FN 定义
chunk_4: Precision / Recall 计算方式
```

对于自动驾驶评价 JSON，后续可以按 scenario_id、metric_name、object_id、timestamp 等字段组织 chunk。

### 3.3 Embedding

Embedding 是把文本转成向量。

用户问题和文档 chunk 都会被转换成向量。系统通过计算向量相似度，判断哪个 chunk 和用户问题最相关。

### 3.4 Vector Database

Vector Database 用来存储 chunk 的向量，并支持相似度检索。

常见选择包括：

* FAISS
* Milvus
* Chroma
* Qdrant

本项目初期可以先用 FAISS 或简单 Python toy retrieval 跑通流程，后续再接 Milvus。

### 3.5 Retriever

Retriever 负责根据用户问题检索相关片段。

输入是用户问题，输出是 TopK 个相关 chunks。

例如用户问：

```text
什么是 FP？
```

Retriever 可能返回：

```text
Top1: FP 表示 false positive，即系统错误检测出了不存在的目标。
Top2: 在感知评价中，FP 会导致误检数量增加。
Top3: fp_count 字段表示当前场景中的误检目标数量。
```

### 3.6 Prompt + Generation

Prompt 阶段会把检索到的证据片段和用户问题组合起来，再交给 LLM。

一个简单 Prompt 模板如下：

```text
你是一个自动驾驶评价系统助手。
请只根据以下参考资料回答问题。
如果参考资料不足，请回答“根据当前资料无法确定”。

参考资料：
{context}

用户问题：
{question}

回答：
```

LLM 最终需要基于这些证据生成答案，而不是凭空回答。

## 4. RAG 和 Fine-tuning 的区别

Fine-tuning 会修改模型参数，适合改变模型行为、输出风格或学习特定任务格式。

RAG 不修改模型参数，而是通过外部知识库提供上下文，适合企业知识库、文档问答和频繁更新的内部资料查询。

| 对比项        | Fine-tuning | RAG             |
| ---------- | ----------- | --------------- |
| 是否修改模型参数   | 是           | 否               |
| 是否适合频繁更新知识 | 不太适合        | 适合              |
| 是否需要训练     | 需要          | 通常不需要           |
| 是否容易追溯依据   | 不容易         | 容易              |
| 适合场景       | 调整模型行为或格式   | 文档问答、知识库、内部资料查询 |

对于 AutoDrive-KB-RAG 项目，当前更适合使用 RAG，而不是 Fine-tuning。因为自动驾驶评价指标、JSON 字段说明、事故案例等内容属于外部知识，而且可能频繁变化。

## 5. AutoDrive-KB-RAG 项目定位

AutoDrive-KB-RAG 是一个面向自动驾驶仿真评价场景的知识库问答系统。

它不是普通 PDF 聊天机器人，而是围绕自动驾驶评价资料进行检索和问答。

系统目标包括：

1. 支持评价指标文档、评价 JSON、事故案例说明等资料接入；
2. 实现文档切块、Embedding、TopK 检索和 Prompt 构造；
3. 帮助用户查询 TP / FP / FN 定义、指标计算方式、JSON 字段含义和失败原因；
4. 后续接入 FastAPI、FAISS 或 Milvus，以及完整 LLM 生成链。

## 6. 本项目和普通 RAG Demo 的区别

普通 RAG Demo 通常只是 PDF 聊天机器人。

AutoDrive-KB-RAG 的差异点在于：

1. 场景来自自动驾驶评价；
2. 数据不只是 PDF，还包括评价 JSON 和事故案例；
3. 问题围绕 TP / FP / FN、指标计算、场景失败原因和评价结果解释；
4. 可以和实习经历中的评价指标开发、JSON 汇总、问题定位经验结合起来；
5. 后续可以扩展到 AutoDrive-Log-Agent，作为日志分析 Agent 的知识检索工具。

## 7. 今日总结

今天学习了 RAG 的总体链路。

核心结论：

```text
RAG = 检索证据 + 基于证据生成答案
```

RAG 的价值在于：

* 减少幻觉；
* 支持外部知识更新；
* 让答案可以追溯；
* 更适合企业内部知识库和工程问题定位；
* 适合自动驾驶评价文档、评价 JSON、事故案例等场景。

下一步 Day 2 将学习 Chunking，重点解决“自动驾驶文档和评价 JSON 应该如何切块”的问题。
