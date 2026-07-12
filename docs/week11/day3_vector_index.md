# Week11 Day3 - In-Memory Vector Index

## 1. Goal

Week11 Day3 的目标是实现 AutoDrive-KB-RAG 的本地向量索引模块。

Day2 已经完成：

```text
texts / chunks
→ EmbeddingClient
→ dense vectors

Day3 在此基础上继续完成：

chunks + vectors
→ InMemoryVectorIndex
→ query_vector
→ top_k retrieval results

也就是实现一个最小版的 embedding-based retriever。

2. Relationship with Week9 Toy Retriever

Week9 已经实现过 toy_retriever.py，其核心流程是：

chunk text
→ tokenize()
→ text_to_vector()
→ cosine_similarity()
→ TopK chunks

Week9 的 toy retriever 使用的是简单词频向量，主要用于理解 RAG 检索流程。

Week11 Day3 的 InMemoryVectorIndex 和 toy retriever 在整体思想上类似，都是：

query vector
vs
chunk vectors
→ similarity scores
→ sort
→ top_k chunks

但是二者有关键区别：

Item	Week9 Toy Retriever	Week11 InMemoryVectorIndex
Vector source	word frequency vector	sentence-transformers embedding
Semantic ability	mostly keyword overlap	semantic similarity
Responsibility	text vectorization + retrieval	vector storage + vector search
Coupling	tied to tokenizer and toy vectorizer	independent of embedding backend
Later usage	learning demo	retrieval service and API foundation

Day3 的重点不是重新写一个 toy retriever，而是将 Week9 的 toy retrieval 升级为更工程化的 embedding retrieval index。

3. Added Files

本日新增文件：

src/retrieval/vector_index.py
examples/run_week11_vector_index_demo.py
docs/week11/day3_vector_index.md

如果 src/retrieval/toy_retriever.py 已经存在，则保留该文件，不删除。它可以作为 Week9 baseline。

4. Core Class

新增核心类：

InMemoryVectorIndex

文件位置：

src/retrieval/vector_index.py

该类维护三个核心成员：

self.chunks
self.vectors
self.embedding_dimension

含义如下：

self.chunks:
保存原始 chunk 字典，包括 chunk_id、source、doc_type、text、metadata 等信息。

self.vectors:
保存每个 chunk 对应的 embedding vector。

self.embedding_dimension:
记录向量维度，例如 384，用于检查 query vector 和 chunk vector 是否维度一致。
5. Main Methods
5.1 add_chunks()
def add_chunks(
    self,
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]],
) -> None:

作用：

将 chunks 和对应的 vectors 加入本地索引。

核心约束：

1. len(chunks) 必须等于 len(vectors)
2. vector 不能为空
3. 所有 vector 的维度必须一致

原因：

每一个 chunk 必须对应一个 embedding vector。
如果 chunks 和 vectors 数量不一致，后续检索结果就无法正确对应原始文本。

例如：

chunk_0 → vector_0
chunk_1 → vector_1
chunk_2 → vector_2
5.2 search()
def search(
    self,
    query_vector: List[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:

作用：

输入 query embedding vector，返回最相似的 top_k chunks。

核心流程：

1. 检查 top_k 是否大于 0
2. 检查索引是否为空
3. 检查 query vector 维度是否匹配
4. 将 self.vectors 转成 numpy matrix
5. 将 query_vector 转成 numpy vector
6. 计算每个 chunk vector 与 query vector 的相似度
7. 按分数从高到低排序
8. 返回 top_k 个 chunk，并附加 rank 和 score

核心代码：

matrix = np.array(self.vectors, dtype=np.float32)
query = np.array(query_vector, dtype=np.float32)

scores = matrix @ query
top_indices = np.argsort(scores)[::-1][:top_k]
6. Similarity Calculation

Day2 中 SentenceTransformerEmbeddingClient 使用：

normalize_embeddings=True

这意味着模型输出的 embedding vector 已经是单位向量。

因此：

cosine_similarity(a, b) = dot_product(a, b)

所以 Day3 中直接使用：

scores = matrix @ query

计算相似度。

这可以避免每次检索时重复计算向量长度，使代码更简洁。

7. Demo Script

新增 demo 文件：

examples/run_week11_vector_index_demo.py

Demo 使用三个手写 chunks：

1. FP 误检表示系统错误地检测到了不存在的目标。
2. FN 漏检表示真实存在的目标没有被系统检测出来。
3. Recall 召回率等于 TP / (TP + FN)。

测试 query：

什么是 FN 漏检？

Demo 流程：

1. 初始化 SentenceTransformerEmbeddingClient
2. 初始化 InMemoryVectorIndex
3. 将三个 chunk 的 text 转成 embedding vectors
4. 调用 vector_index.add_chunks(chunks, vectors)
5. 将 query 转成 query_vector
6. 调用 vector_index.search(query_vector, top_k=3)
7. 输出 top_k 检索结果
8. Run Command

由于 HuggingFace 直连可能失败，本项目使用 HF mirror 下载模型：

HF_ENDPOINT=https://hf-mirror.com PYTHONPATH=. python examples/run_week11_vector_index_demo.py

如果模型已经缓存，也可以直接运行：

PYTHONPATH=. python examples/run_week11_vector_index_demo.py

其中：

PYTHONPATH=.

表示将当前项目根目录加入 Python import 搜索路径，避免出现：

ModuleNotFoundError: No module named 'src'
9. Smoke Test Result

运行命令：

HF_ENDPOINT=https://hf-mirror.com PYTHONPATH=. python examples/run_week11_vector_index_demo.py

预期输出类似：

index_chunk_count: 3
query: 什么是 FN 漏检？

TopK results:
rank=1 score=0.5403 chunk_id=metric_doc_fn text=FN 漏检表示真实存在的目标没有被系统检测出来。
rank=2 score=0.4936 chunk_id=metric_doc_fp text=FP 误检表示系统错误地检测到了不存在的目标。
rank=3 score=0.4516 chunk_id=metric_doc_recall text=Recall 召回率等于 TP / (TP + FN)。

验收重点：

1. index_chunk_count = 3
2. query = 什么是 FN 漏检？
3. rank=1 应该是 FN chunk
4. 每条结果都包含 rank、score、chunk_id、text
10. Current Status

Day3 已完成：

1. 实现 InMemoryVectorIndex
2. 支持 chunks + vectors 入库
3. 支持 query_vector 检索 top_k chunks
4. 支持 rank 和 score 返回
5. 使用 sentence-transformers embedding 替代 Week9 词频向量
6. demo 能验证 FN query 命中 FN chunk
11. Current Limitations

当前 InMemoryVectorIndex 只是 Week11 MVP，本身仍有明显限制：

1. 只保存在内存中，程序退出后索引消失
2. 不支持持久化存储
3. 不支持大规模 ANN 检索
4. 没有接入 FAISS / Milvus
5. 不支持 metadata filter
6. 不支持多文档隔离和文档删除

但是它已经足够支撑 Week11 后续流程：

parse-and-chunk
→ embedding
→ in-memory index
→ retrieval API