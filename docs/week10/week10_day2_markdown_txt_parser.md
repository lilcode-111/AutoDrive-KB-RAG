# Week10 Day2：Markdown / TXT 解析接口

## 1. 今日目标

给 `AutoDrive-KB-RAG` 增加一个文档解析接口：

```text
POST /api/v1/documents/parse
```

支持上传：

```text
.md / .markdown / .txt
```

接口完成的流程：

```text
上传文件
→ 读取 bytes
→ 判断文件类型
→ bytes 解码成 str
→ 清洗文本
→ 返回 preview
```

Day2 暂时不保存文件，也不做 chunking。

---

## 2. 新增文件

```text
src/cleaning/text_cleaner.py
src/parsing/markdown_parser.py
```

修改文件：

```text
app/schemas.py
app/routers/documents.py
```

---

## 3. 核心流程

```text
用户上传文件
        ↓
POST /api/v1/documents/parse
        ↓
FastAPI 调用 parse_document()
        ↓
await file.read()
        ↓
读取上传文件 bytes
        ↓
parse_markdown_or_txt()
        ↓
detect_file_type()
判断 .md / .txt
        ↓
decode_file_content()
bytes → str
        ↓
clean_text()
清洗换行、空格、空行
        ↓
make_preview()
生成预览
        ↓
返回 ParseDocumentResponse
```

---

## 4. FastAPI 调用机制

启动服务：

```bash
uvicorn app.main:app --reload
```

调用关系：

```text
uvicorn 启动 app/main.py 里的 app
        ↓
main.py 注册 documents.router
        ↓
用户请求 POST /api/v1/documents/parse
        ↓
FastAPI 自动调用 parse_document()
```

`parse_document()` 不是手动在 `main.py` 里调用的，而是 FastAPI 收到 HTTP 请求后自动调用。

---

## 5. 文本清洗模块

文件：

```text
src/cleaning/text_cleaner.py
```

主要功能：

```text
normalize_newlines()
统一换行符

strip_trailing_spaces()
删除每行末尾空格

collapse_blank_lines()
压缩过多空行

clean_text()
串起完整清洗流程

make_preview()
截取前 300 个字符作为预览
```

---

## 6. Markdown / TXT 解析模块

文件：

```text
src/parsing/markdown_parser.py
```

主要功能：

```text
detect_file_type()
根据后缀判断文件类型

decode_file_content()
把 bytes 解码成 str

parse_markdown_or_txt()
完成类型判断、解码、清洗、preview 生成
```

注意点：

```python
Path(filename).suffix.lower()
```

`lower()` 必须有括号。

---

## 7. 新增响应模型

文件：

```text
app/schemas.py
```

新增：

```python
class ParseDocumentResponse(BaseModel):
    filename: str
    file_type: str
    text_length: int
    preview: str
    status: str
```

返回示例：

```json
{
  "filename": "test_metric.md",
  "file_type": "markdown",
  "text_length": 78,
  "preview": "# 自动驾驶评价指标说明...",
  "status": "success"
}
```

---

## 8. 新增接口

文件：

```text
app/routers/documents.py
```

新增：

```python
@router.post("/parse", response_model=ParseDocumentResponse)
async def parse_document(file: UploadFile = File(...)) -> ParseDocumentResponse:
    ...
```

最终接口：

```text
POST /api/v1/documents/parse
```

这里必须用 `POST`，因为上传文件属于提交数据。  
如果写成 `GET`，用 curl 上传时会报：

```json
{"detail": "Method Not Allowed"}
```

---

## 9. async / await

接口中使用：

```python
content = await file.read()
```

含义：

```text
等待 FastAPI 读取上传文件内容
```

读取结果是：

```text
bytes
```

因为用了 `await`，所以函数必须写成：

```python
async def parse_document(...)
```

---

## 10. 测试结果

启动服务：

```bash
uvicorn app.main:app --reload
```

测试 Markdown：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/parse" \
  -F "file=@/tmp/test_metric.md"
```

返回成功：

```json
{
  "filename": "test_metric.md",
  "file_type": "markdown",
  "text_length": 78,
  "preview": "...",
  "status": "success"
}
```

测试 `.txt`：

```text
file_type = txt
status = success
```

测试 `.json`：

```json
{
  "detail": "Unsupported file type: .json"
}
```

这是正确结果，因为 JSON 解析放到 Day3。

---

## 11. 网页测试

打开：

```text
http://127.0.0.1:8000/docs
```

操作：

```text
POST /api/v1/documents/parse
→ Try it out
→ Choose File
→ 选择 .md 或 .txt
→ Execute
→ 查看 Server response
```

---

## 12. 今日问题记录

### 1. 函数名不一致

错误：

```text
parse_markdown_or_text
```

正确：

```text
parse_markdown_or_txt
```

### 2. lower 少括号

错误：

```python
suffix = Path(filename).suffix.lower
```

正确：

```python
suffix = Path(filename).suffix.lower()
```

### 3. 字段名不一致

错误：

```python
"filetype": file_type
```

正确：

```python
"file_type": file_type
```

### 4. GET / POST 写错

错误：

```python
@router.get("/parse")
```

正确：

```python
@router.post("/parse")
```

---

## 13. 今日总结

Day2 完成了 Markdown / TXT 上传解析接口。

当前已经跑通：

```text
上传文件
→ 读取 bytes
→ 判断文件类型
→ 解码成 str
→ 清洗文本
→ 返回 preview
```

当前不保存文件、不做切块。  
Day3 将实现自动驾驶评价 JSON 解析。
