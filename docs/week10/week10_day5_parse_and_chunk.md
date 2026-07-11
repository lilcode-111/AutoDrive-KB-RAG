# Week10 Day5 - Parse and Chunk API

## 1. 今日目标

Day5 的目标是把前几天完成的文档解析能力接入 chunking 流程，形成 RAG 前处理接口。

核心流程：

```text
upload → parse → clean → chunk
```

新增接口：

```text
POST /api/v1/documents/parse-and-chunk
```

该接口支持：

```text
.md / .markdown / .txt / .json / .pdf
```

---

## 2. 已有基础

Day5 复用了前面已经完成的模块：

```text
Day2 Markdown/TXT parser
Day3 JSON evaluation parser
Day4 PDF parser
Week9 chunking module
```

本日没有重新写 chunker，而是复用 Week9 已有的：

```text
src/chunking/simple_chunker.py
```

---

## 3. 核心改动

Day5 主要修改以下文件：

```text
src/parsing/markdown_parser.py
src/parsing/json_parser.py
src/parsing/pdf_parser.py
src/chunking/simple_chunker.py
app/schemas.py
app/routers/documents.py
docs/week10_day5_parse_and_chunk.md
```

---

## 4. Parser 返回完整 text

Day5 需要对完整文本切块，所以各类 parser 的返回结果中新增：

```python
"text": cleaned_text
```

示例：

```python
return {
    "filename": filename,
    "file_type": file_type,
    "text": cleaned_text,
    "text_length": len(cleaned_text),
    "preview": make_preview(cleaned_text),
    "status": "success",
    "metadata": metadata,
}
```

注意：

```text
/parse 接口仍然只返回 preview
/parse-and-chunk 接口使用 text 来切 chunk
```

---

## 5. 新增 FastAPI 适配函数

在已有 chunker 中新增：

```python
chunk_parsed_document()
```

作用：

```text
接收 parser 解析后的完整 text
→ 调用 chunk_text_by_window()
→ 生成 chunks
→ 合并 parser metadata 和 chunk metadata
→ 返回统一格式的 chunk 列表
```

每个 chunk 包含：

```text
chunk_id
source
doc_type
text
text_length
metadata
```

---

## 6. Metadata 合并

每个 chunk 的 metadata 由三部分组成：

```text
1. parser metadata
   例如 scenario_id / metric / result / object_id

2. chunk metadata
   例如 chunk_strategy / start_char / end_char / chunk_size / overlap

3. Day5 补充字段
   例如 filename / file_type / chunk_index
```

示例：

```json
{
  "scenario_id": "case_001",
  "metric": "track_miss_detection",
  "result": "fail",
  "chunk_strategy": "fixed_window",
  "start_char": 0,
  "end_char": 500,
  "chunk_size": 500,
  "overlap": 80,
  "filename": "test_eval_day3.json",
  "file_type": "evaluation_json",
  "chunk_index": 0
}
```

---

## 7. 新增 Response Schema

在 `app/schemas.py` 中新增：

```python
class DocumentChunk(BaseModel):
    chunk_id: str
    source: str
    doc_type: str
    text: str
    text_length: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParseAndChunkResponse(BaseModel):
    filename: str
    file_type: str
    status: str
    text_length: int
    chunk_count: int
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 8. 新增 API

在 `app/routers/documents.py` 中新增：

```text
POST /api/v1/documents/parse-and-chunk
```

核心流程：

```text
读取上传文件 bytes
→ parse_document_by_type()
→ 获取 parse_result["text"]
→ chunk_parsed_document()
→ 返回 chunk_count 和 chunks
```

---

## 9. 测试结果

使用 `test_eval_day3.json` 测试成功。

返回结果包含：

```json
{
  "filename": "test_eval_day3.json",
  "file_type": "evaluation_json",
  "status": "success",
  "text_length": 686,
  "chunk_count": 2,
  "chunks": [
    {
      "chunk_id": "test_eval_day3_window_0",
      "text_length": 500,
      "metadata": {
        "scenario_id": "case_001",
        "metric": "track_miss_detection",
        "result": "fail",
        "chunk_strategy": "fixed_window",
        "start_char": 0,
        "end_char": 500
      }
    }
  ]
}
```

说明 Day5 流程已经跑通：

```text
JSON upload → parse → clean → chunk → return chunks
```

---

## 10. 今日总结

Day5 完成了 RAG 前处理中的关键一步：

```text
parse → clean → chunk
```

项目现在已经支持：

```text
Markdown / TXT / JSON / PDF 上传解析
并且可以将解析后的文本切成 chunks
```

这为后续 embedding、vector database、retrieval 和 RAG prompt 构建打下基础。

Day5 暂时不做：

```text
Milvus
FAISS
Embedding model
LLM QA
Docker
```

这些将在后续阶段继续实现。