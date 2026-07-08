# Week10 Day4 - PDF Parser and Unified Document Parser

## 1. 今日目标

Day4 的目标是新增 PDF 解析能力，并统一管理不同文件类型的解析逻辑。

Day4 后，接口支持：

```text
.md / .markdown / .txt / .json / .pdf
```

核心接口仍然是：

```text
POST /api/v1/documents/parse
```

---

## 2. 今日改动文件

```text
src/parsing/pdf_parser.py
src/parsing/document_parser.py
app/routers/documents.py
requirements.txt
```

作用分别是：

```text
pdf_parser.py       解析 PDF 文件
document_parser.py  根据文件后缀分发到不同 parser
documents.py        FastAPI 接口调用统一 parser
requirements.txt    新增 pypdf 依赖
```

---

## 3. 新增依赖

Day4 使用 `pypdf` 解析 PDF。

`requirements.txt` 应包含：

```text
fastapi
uvicorn[standard]
python-multipart
pydantic
pypdf==6.14.2
```

注意 `pydantic` 和 `pypdf` 必须分成两行。

---

## 4. PDF Parser 核心流程

文件：

```text
src/parsing/pdf_parser.py
```

核心流程：

```text
PDF bytes
→ BytesIO(content)
→ PdfReader(pdf_file)
→ 遍历每一页
→ page.extract_text()
→ clean_text()
→ make_preview()
→ 返回 metadata
```

返回结果结构：

```python
{
    "filename": filename,
    "file_type": "pdf",
    "text_length": len(cleaned_text),
    "preview": make_preview(cleaned_text),
    "status": "success",
    "metadata": metadata,
}
```

PDF metadata 示例：

```json
{
  "num_pages": 3,
  "extracted_pages": 3,
  "has_text": true
}
```

字段含义：

```text
num_pages        PDF 总页数
extracted_pages  成功提取文字的页数
has_text         是否提取到了文本
```

---

## 5. Unified Document Parser

文件：

```text
src/parsing/document_parser.py
```

作用：统一管理文件类型分发。

```python
def parse_document_by_type(filename: str, content: bytes) -> dict:
    suffix = Path(filename).suffix.lower()

    if suffix in {".md", ".markdown", ".txt"}:
        return parse_markdown_or_txt(filename, content)

    if suffix == ".json":
        return parse_evaluation_json(filename, content)

    if suffix == ".pdf":
        return parse_pdf_document(filename, content)

    raise ValueError(f"Unsupported file type: {suffix}")
```

分发关系：

```text
.md / .markdown / .txt → markdown_parser.py
.json                  → json_parser.py
.pdf                   → pdf_parser.py
```

---

## 6. FastAPI Router 修改

文件：

```text
app/routers/documents.py
```

Day4 后，`documents.py` 不再自己判断文件类型，只调用统一 parser：

```python
content = await file.read()
result = parse_document_by_type(file.filename, content)
```

返回格式保持统一：

```python
return ParseDocumentResponse(
    filename=result["filename"],
    file_type=result["file_type"],
    text_length=result["text_length"],
    preview=result["preview"],
    status=result["status"],
    metadata=result.get("metadata", {}),
)
```

---

## 7. 测试方式

启动服务：

```bash
uvicorn app.main:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

测试接口：

```text
POST /api/v1/documents/parse
→ Try it out
→ Choose File
→ 上传 PDF
→ Execute
```

成功返回应包含：

```text
file_type = pdf
status = success
metadata.num_pages
metadata.extracted_pages
metadata.has_text
preview
```

---

## 8. 重要注意点

### 1. 字段名必须一致

错误：

```python
"num_page": len(reader.pages)
```

正确：

```python
"num_pages": len(reader.pages)
```

因为后面读取的是：

```python
pdf_result["num_pages"]
```

---

### 2. 删除无关 import

`pdf_parser.py` 中不需要：

```python
from importlib import metadata
from numpy import full
```

正确 import：

```python
from io import BytesIO
from typing import Any, Dict, List

from pypdf import PdfReader

from src.cleaning.text_cleaner import clean_text, make_preview
```

---

### 3. 扫描 PDF 可能没有文本

`pypdf` 适合文本型 PDF。

如果是扫描件或图片型 PDF，可能返回：

```text
No extractable text found in this PDF. The file may be a scanned image PDF.
```

这不是代码错误，扫描 PDF 后续需要 OCR，Day4 暂不处理。

---

## 9. 提交前检查

```bash
python -m py_compile src/parsing/pdf_parser.py
python -m py_compile src/parsing/document_parser.py
python -c "from src.parsing.pdf_parser import parse_pdf_document; print('pdf parser import ok')"
python -c "from src.parsing.document_parser import parse_document_by_type; print('document parser import ok')"
python -c "from app.main import app; print('app import ok')"
```

---

## 10. 今日总结

Day4 完成了两件核心工作：

```text
1. 新增 PDF parser，支持文本型 PDF 解析
2. 新增 document_parser.py，统一管理 md/txt/json/pdf 的解析分发
```

Day4 后，项目支持：

```text
Markdown / TXT / JSON / PDF
```

这为 Day5 的完整流程打下基础：

```text
upload → parse → clean → chunk
```