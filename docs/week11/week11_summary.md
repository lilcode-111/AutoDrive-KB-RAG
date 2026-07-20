# Week11 Summary - Embedding and Retrieval

## 1. Goal

Week11 的目标是实现文本 embedding、向量索引和语义检索 API。

完整链路：

```text
document
→ parse
→ chunk
→ embedding
→ vector index
→ query embedding
→ TopK retrieval
2. Implemented Modules
EmbeddingClient

文件：

src/embeddings/embedding_client.py

使用抽象基类定义统一接口：

embed_texts()
embed_query()
SentenceTransformerEmbeddingClient

文件：

src/embeddings/sentence_transformer_client.py

使用模型：

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

功能：

text → 384-dimensional embedding vector
InMemoryVectorIndex

文件：

src/retrieval/vector_index.py

功能：

store chunks and vectors
calculate vector similarity
return TopK chunks
clear and count index
RetrievalService

文件：

src/retrieval/retrieval_service.py

功能：

index_chunks()
search()
count()
clear()

它负责连接 embedding client 和 vector index。

3. Retrieval API

文件：

app/routers/retrieval.py

实现接口：

POST /api/v1/retrieval/index-document
POST /api/v1/retrieval/search
POST /api/v1/retrieval/clear
GET  /api/v1/retrieval/status
Index Pipeline
UploadFile
→ parse_document_by_type()
→ chunk_parsed_document()
→ RetrievalService.index_chunks()
→ embedding vectors
→ in-memory vector index
Search Pipeline
query
→ embed_query()
→ query vector
→ vector similarity
→ TopK chunks
4. Testing

自动化测试：

tests/test_retrieval_service.py

运行：

PYTHONPATH=. pytest -q

测试内容：

index chunks
semantic search
clear index
invalid query validation

真实 API 通过 Swagger 测试：

http://127.0.0.1:8000/docs
5. Week11 Result

Week11 已完成：

1. 文本可以转换为 embedding vectors
2. chunks 和 vectors 可以存入内存索引
3. query 可以进行语义检索
4. 检索结果包含 rank、score 和 chunk content
5. FastAPI 已提供文档入库和检索接口
6. 核心 retrieval service 已添加自动化测试
6. Current Limitations
1. 索引只保存在内存中
2. 服务重启后索引会丢失
3. 重复上传文档会产生重复 chunks
4. 目前使用简单点积排序
5. 尚未接入 FAISS、Milvus 或其他向量数据库
6. 尚未接入 LLM 生成最终答案