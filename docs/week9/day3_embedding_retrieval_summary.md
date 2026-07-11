# Day 3: Embedding + Toy Retrieval

## 1. 今日目标

今天完成 RAG 中的检索雏形。

Day 2 已经把原始资料切成了 chunks，并保存到：

```text
data/processed/day2_chunks.json
```

Day 3 的目标是读取这些 chunks，并实现一个最小版 Retriever：

```text
chunks
→ 文本向量化
→ query 向量化
→ 相似度计算
→ 返回 TopK chunks
```

今天不接入大模型，也不接入 Milvus / FAISS，重点是理解 Retriever 的基本工作方式。

---

## 2. 今日完成内容

今天新增了两个核心文件：

```text
src/retrieval/toy_retriever.py
examples/run_day3_retrieval_demo.py
```

其中：

```text
toy_retriever.py
```

负责实现最小版检索逻辑。

```text
run_day3_retrieval_demo.py
```

负责读取 Day 2 生成的 chunks，构造测试 query，并打印 TopK 检索结果。

---

## 3. 数据流

Day 3 的数据流如下：

```text
data/processed/day2_chunks.json
        ↓
load_chunks()
        ↓
chunks
        ↓
ToyRetriever(chunks)
        ↓
self.chunks
self.chunk_vectors
        ↓
query
        ↓
retriever.search(query, top_k=3)
        ↓
TopK chunks
```

其中：

```text
self.chunks
```

保存原始 chunk 信息，包括：

```text
chunk_id
source
doc_type
text
metadata
```

```text
self.chunk_vectors
```

保存每个 chunk 对应的简单词频向量。

---

## 4. Toy Retriever 的实现思路

当前 Toy Retriever 使用的是非常简单的词频检索方法。

主要流程是：

```text
文本
→ tokenize()
→ text_to_vector()
→ cosine_similarity()
→ TopK 排序
```

### 4.1 tokenize()

`tokenize()` 负责把文本切成 token。

当前规则：

```text
英文、数字、下划线按单词提取
中文按单字提取
英文统一转小写
```

例如：

```text
scenario_001 为什么被判定为 FN？
```

会被处理成类似：

```text
scenario_001
fn
为
什
么
被
判
定
为
```

这里中文按单字切分只是为了快速跑通流程，不是最终方案。

### 4.2 text_to_vector()

`text_to_vector()` 使用 `Counter` 统计 token 出现次数。

例如：

```text
什么是 FP 误检？
```

可能被表示为：

```text
fp: 1
什: 1
么: 1
是: 1
误: 1
检: 1
```

这个结果可以理解成一个简单的稀疏词频向量。

### 4.3 cosine_similarity()

`cosine_similarity()` 用来计算 query 向量和 chunk 向量的相似度。

如果 query 和某个 chunk 有较多共同 token，那么相似度就会更高。

例如用户问：

```text
什么是 FP 误检？
```

系统会更容易召回：

```text
metric_doc_sections_2: FP 定义
```

因为 query 和该 chunk 中都包含：

```text
fp
误
检
```

---

## 5. 今日测试 Query

今天测试了以下问题：

```text
什么是 FP 误检？
什么是 FN 漏检？
Recall 怎么计算？
scenario_001 为什么被判定为 FN？
scenario_002 为什么是 FP？
```

当前检索结果中，基础概念类问题效果较好。

例如：

```text
Query: 什么是 FP 误检？
Top 1: metric_doc_sections_2
```

说明系统可以正确召回 FP 定义。

```text
Query: Recall 怎么计算？
Top 1: metric_doc_sections_4
```

说明系统可以正确召回 Precision 和 Recall 的公式说明。

---

## 6. 当前结果分析

当前结果说明 Toy Retriever 已经跑通了最小检索链路。

效果较好的部分：

```text
FP 定义类问题可以召回 FP 文档
FN 定义类问题可以召回 FN 文档
Recall 计算类问题可以召回 Precision / Recall 文档
事故案例类问题可以召回相关 Case
```

存在的问题：

```text
scenario_001 / scenario_002 这类具体场景问题，JSON chunk 没有稳定排到 Top 1
```

例如用户问：

```text
scenario_001 为什么被判定为 FN？
```

理想结果应该优先召回：

```text
evaluation_result_scenario_001
accident_case_sections_1
metric_doc_sections_3
```

但当前 Toy Retriever 更容易召回 FN 定义文档，因为它只基于 token 重合和词频相似度，不理解 `scenario_id` 这类 metadata 的业务重要性。

---

## 7. 当前 Toy Retriever 的局限

当前方法只是一个 toy retrieval，不是真正的工业级检索。

主要局限包括：

1. 中文按单字切分，不能理解完整词语；
2. 只看 token 重合，不理解语义；
3. 长 chunk 的向量长度更大，可能导致相似度被稀释；
4. 没有利用 metadata；
5. 没有对 `scenario_id`、`metric_name`、`FP/FN/TP` 等关键字段做加权；
6. 没有使用真正的 embedding 模型。

因此当前系统能说明检索流程，但检索质量还需要继续优化。

---

## 8. 后续增强方向

下一步可以对 Toy Retriever 做一个小增强：加入 metadata boost。

当前基础分数来自：

```text
cosine_similarity(query_vector, chunk_vector)
```

可以在此基础上增加规则加分：

```text
如果 query 中出现 scenario_001，
并且 chunk.metadata.scenario_id == scenario_001，
则给该 chunk 加分。

如果 query 中出现 FP / FN / TP，
并且 chunk.text 或 metadata 中包含对应结果，
则给该 chunk 加分。
```

增强后的目标是：

```text
scenario_001 为什么被判定为 FN？
```

优先召回：

```text
evaluation_result_scenario_001
accident_case_sections_1
metric_doc_sections_3
```

而不是只召回 FN 定义。

这一步可以作为 Day 3 的增强版，也可以放到 Day 4 之前完成。

---

## 9. 今日总结

今天完成了 AutoDrive-KB-RAG 的最小检索模块。

当前系统已经具备以下能力：

```text
读取 Day 2 生成的 chunks
把 chunk 文本转成简单词频向量
把用户 query 转成简单词频向量
计算 query 和每个 chunk 的余弦相似度
返回 TopK 相关 chunks
```

核心理解：

```text
Retriever 的本质是在知识库 chunks 中，找到和用户问题最相关的证据片段。
```

Day 3 当前版本虽然只是 toy retriever，但已经跑通了 RAG 中最关键的检索链路：

```text
query → retrieval → TopK evidence chunks
```

下一步将增强检索质量，并进入 Day 4：Retriever + Prompt 拼接，把 TopK chunks 组织成可以交给 LLM 的 Prompt。