# Week10 Day3 - JSON Evaluation Parser

## 1. 今日目标

Day3 的目标是让 `AutoDrive-KB-RAG` 支持自动驾驶评价结果 JSON 文件解析。

在 Day2 中，接口只支持：

```text
.md / .markdown / .txt
```

Day3 后，接口升级为支持：

```text
.md / .markdown / .txt / .json
```

核心接口仍然是：

```text
POST /api/v1/documents/parse
```

---

## 2. 新增文件

```text
src/parsing/json_parser.py
```

该文件负责解析自动驾驶评价 JSON，并返回：

```text
filename
file_type
text_length
preview
status
metadata
```

---

## 3. JSON Parser 核心流程

```text
上传 JSON 文件
→ FastAPI 读取 bytes
→ decode_json_content() 转成 Python dict/list
→ extract_metadata_from_dict() 提取关键字段
→ build_evaluation_summary() 生成可读摘要文本
→ make_preview() 生成预览内容
→ 返回 API response
```

---

## 4. 主要函数说明

### 4.1 `decode_json_content()`

作用：将上传文件的 `bytes` 转成 Python 对象。

```text
bytes → str → dict/list
```

例如：

```json
{
  "scenario_id": "case_001",
  "metric": "track_miss_detection"
}
```

会变成 Python 字典：

```python
{
    "scenario_id": "case_001",
    "metric": "track_miss_detection"
}
```

---

### 4.2 `extract_metadata_from_dict()`

作用：从 JSON 字典中提取自动驾驶评价相关的重要字段。

重点字段包括：

```text
scenario_id
case_id
scene_id
metric
metric_name
object_id
track_id
result
status
reason
failure_reason
start_time
end_time
tp
fp
fn
tp_count
fp_count
fn_count
```

`metadata` 是结构化标签，后续可以用于检索、过滤和定位。

示例：

```json
{
  "scenario_id": "case_001",
  "metric": "track_miss_detection",
  "result": "fail",
  "object_id": "vehicle_32"
}
```

提取后：

```json
{
  "scenario_id": "case_001",
  "metric": "track_miss_detection",
  "result": "fail",
  "object_id": "vehicle_32"
}
```

---

### 4.3 `flatten_json_to_lines()`

作用：将复杂嵌套 JSON 展平成一行一行的可读文本。

示例 JSON：

```json
{
  "scenario_id": "case_001",
  "object": {
    "object_id": "vehicle_32",
    "type": "vehicle"
  }
}
```

展开后：

```text
scenario_id: case_001
object.object_id: vehicle_32
object.type: vehicle
```

这个函数的意义是：让嵌套 JSON 也能变成适合 RAG 检索的文本。

---

### 4.4 `build_evaluation_summary()`

作用：根据 `data` 和 `metadata` 构造一段可读摘要文本。

其中：

```text
metadata = 结构化标签，给程序和检索系统用
context / cleaned_text = 可读文本，给 RAG 和大模型用
```

生成的摘要类似：

```text
自动驾驶评价结果 JSON 解析摘要
scenario_id: case_001
metric: track_miss_detection
object_id: vehicle_32
result: fail
reason: target lost for more than threshold
tp_count: 18
fp_count: 2
fn_count: 1

原始 JSON 字段展开：
scenario_id: case_001
metric: track_miss_detection
result: fail
object_id: vehicle_32
start_time: 12.3
end_time: 15.8
reason: target lost for more than threshold
```

---

### 4.5 `parse_evaluation_json()`

作用：JSON parser 的总入口函数。

完整流程：

```text
decode_json_content()
→ extract_metadata_from_dict()
→ build_evaluation_summary()
→ make_preview()
→ return result dict
```

返回结果结构：

```python
{
    "filename": filename,
    "file_type": "evaluation_json",
    "text_length": len(cleaned_text),
    "preview": make_preview(cleaned_text),
    "status": "success",
    "metadata": metadata,
}
```

注意字段名必须是：

```text
file_type
```

不能写成：

```text
filetype
```

否则 FastAPI response 会报错。

---

## 5. 修改 `schemas.py`

`ParseDocumentResponse` 新增 `metadata` 字段：

```python
from typing import Any, Dict, List
from pydantic import BaseModel, Field

class ParseDocumentResponse(BaseModel):
    filename: str
    file_type: str
    text_length: int
    preview: str
    status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

这样：

- Markdown/TXT 返回 `metadata: {}`
- JSON 返回具体结构化字段

---

## 6. 修改 `documents.py`

新增根据文件后缀分流的逻辑：

```python
def parse_uploaded_document(filename: str, content: bytes) -> dict:
    suffix = Path(filename).suffix.lower()

    if suffix in {".md", ".markdown", ".txt"}:
        return parse_markdown_or_txt(filename, content)

    if suffix == ".json":
        return parse_evaluation_json(filename, content)

    raise ValueError(f"Unsupported file type: {suffix}")
```

接口返回时需要带上 metadata：

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

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

选择：

```text
POST /api/v1/documents/parse
```

点击：

```text
Try it out
→ Choose File
→ 上传 test_eval_day3.json
→ Execute
```

---

## 8. 验收结果

成功返回示例：

```json
{
  "filename": "test_eval_day3.json",
  "file_type": "evaluation_json",
  "text_length": 686,
  "preview": "自动驾驶评价结果 JSON 解析摘要...",
  "status": "success",
  "metadata": {
    "scenario_id": "case_001",
    "metric": "track_miss_detection",
    "result": "fail",
    "object_id": "vehicle_32",
    "start_time": 12.3,
    "end_time": 15.8,
    "reason": "target lost for more than threshold",
    "tp_count": 18,
    "fp_count": 2,
    "fn_count": 1
  }
}
```

重点检查：

```text
status = success
file_type = evaluation_json
metadata 中有 scenario_id / metric / result / object_id
preview 中有 JSON 解析摘要
```

---

## 9. 今日总结

Day3 完成了 JSON 评价结果解析功能。

项目从普通 Markdown/TXT 文档解析，升级为支持自动驾驶评价 JSON 的结构化解析。

本日核心收获：

```text
1. JSON 文件上传后，本质上先是 bytes
2. json.loads() 可以把 JSON 字符串转成 Python dict/list
3. metadata 是结构化标签，用于检索和过滤
4. cleaned_text / preview 是可读文本，用于 RAG context
5. FastAPI response_model 需要和返回字段保持一致
6. file_type 字段名必须统一，不能写成 filetype
```

Day3 为后续 Day4 PDF parser、Day5 upload-parse-clean-chunk API 打下基础。