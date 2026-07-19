# Week11 Day5 - Retrieval API

## 1. Goal

Day5 的目标是把 Day4 的 `RetrievalService` 接入 FastAPI，完成文档入库和语义检索 API。

完整链路：

```text
上传文档
→ parse
→ clean
→ chunk
→ embedding
→ in-memory vector index
→ query search
→ TopK chunks
2. Added Files
app/routers/retrieval.py
docs/week11/day5_retrieval_api.md

修改文件：

app/main.py

在 app/main.py 中注册：

from app.routers import health, documents, retrieval

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(retrieval.router)
3. API Endpoints
3.1 Index Document
POST /api/v1/retrieval/index-document

功能：

UploadFile
→ parse_document_by_type()
→ chunk_parsed_document()
→ RetrievalService.index_chunks()
→ embedding vectors
→ InMemoryVectorIndex

返回：

filename
file_type
text_length
chunk_count
indexed_chunk_count
total_indexed_chunk_count
embedding_dimension
metadata
3.2 Search
POST /api/v1/retrieval/search

请求示例：

{
  "query": "什么是 FN 漏检？",
  "top_k": 3
}

功能：

query
→ embed_query()
→ query_vector
→ vector_index.search()
→ TopK chunks

检索结果包括：

rank
score
chunk_id
source
doc_type
text
text_length
metadata
3.3 Status
GET /api/v1/retrieval/status

用于查看当前内存索引中的 chunk 数量。

3.4 Clear
POST /api/v1/retrieval/clear

用于清空当前内存中的 chunks、vectors 和 embedding dimension。

4. Test File

测试文件：

week11_retrieval_test.md

测试问题：

什么是 FN 漏检？
Recall 怎么计算？
scenario_001 为什么失败？
scenario_002 为什么被判定为 FP？
5. Test Procedure
1. GET /api/v1/retrieval/status
2. POST /api/v1/retrieval/index-document
3. GET /api/v1/retrieval/status
4. POST /api/v1/retrieval/search
5. POST /api/v1/retrieval/clear
6. GET /api/v1/retrieval/status
6. Result

Day5 已完成：

1. Retrieval router 已注册
2. 文档上传后可以解析和切块
3. chunks 可以转换为 embedding vectors
4. chunks 和 vectors 可以加入内存索引
5. query 可以返回 TopK 相关片段
6. 支持查看和清空索引状态
7. Current Limitation

当前索引为内存索引：

1. FastAPI 重启后数据消失
2. 重复上传会重复追加 chunks
3. 尚未接入 FAISS / Milvus
4. 尚未实现持久化存储
5. 尚未接入 LLM 生成答案