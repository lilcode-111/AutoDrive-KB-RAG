# Week11 Day4 - Retrieval Service

## 1. Goal

Day4 的目标是实现 `RetrievalService`，把 Day2 的 embedding 模块和 Day3 的 vector index 模块串起来。

当前链路：

```text
chunks
→ embed_texts()
→ vectors
→ InMemoryVectorIndex.add_chunks()

query
→ embed_query()
→ InMemoryVectorIndex.search()
→ top_k chunks

Day4 暂时不接 FastAPI，只做 Python 内部服务层。

2. Added Files
src/retrieval/retrieval_service.py
examples/run_week11_retrieval_service_demo.py
docs/week11/day4_retrieval_service.md
3. Core Design

RetrievalService 连接两个模块：

EmbeddingClient:
负责把文本和 query 转成 embedding vectors。

InMemoryVectorIndex:
负责保存 chunks + vectors，并根据 query_vector 返回 top_k chunks。

核心方法：

index_chunks(chunks)
search(query, top_k)
4. index_chunks()

功能：

chunks
→ 提取每个 chunk["text"]
→ embed_texts(texts)
→ vector_index.add_chunks(chunks, vectors)

返回内容包括：

status
indexed_chunk_count
total_indexed_chunk_count
embedding_dimension

该方法要求每个 chunk 必须包含非空 "text" 字段。

5. search()

功能：

query
→ embed_query(query)
→ vector_index.search(query_vector, top_k)
→ results

返回内容包括：

query
top_k
result_count
results

其中 results 中每个 chunk 会带有：

rank
score
chunk_id
source
doc_type
text
metadata
6. Why This Layer

如果没有 RetrievalService，Day5 写 FastAPI API 时就需要在 router 里直接处理：

embedding
vector index
query vector
top_k search
result formatting

这样 API 层会太乱。

加入 RetrievalService 后，FastAPI 只需要调用：

retrieval_service.index_chunks(chunks)
retrieval_service.search(query, top_k)

因此 Day4 的作用是为 Day5 的 Retrieval API 做准备。

7. Demo

运行命令：

HF_ENDPOINT=https://hf-mirror.com PYTHONPATH=. python examples/run_week11_retrieval_service_demo.py

如果模型已经缓存，也可以直接运行：

PYTHONPATH=. python examples/run_week11_retrieval_service_demo.py

测试 query：

什么是 FN 漏检？

预期结果：

rank=1 should be metric_doc_fn