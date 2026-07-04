# Day 2: Chunking Strategy

## 1. 今日目标

今天学习 RAG 中的 Chunking，也就是文档切块。

Chunking 的目标不是简单把文件拆开，而是把原始资料整理成适合后续检索的知识单元。后续 RAG 系统检索的对象不是原始大文件，而是这些切好的 chunks。

Day 2 的主要任务：

1. 理解为什么 RAG 需要切块；
2. 实现 Markdown 文档按标题切块；
3. 实现评价 JSON 按 `scenario_id` 切块；
4. 生成统一格式的 chunk 数据；
5. 为 Day 3 的 Embedding 和 Retrieval 做准备。

---

## 2. 为什么需要 Chunking

如果不切块，系统只能把整个文档作为一个检索单元。

例如一个评价 JSON 中可能包含很多场景：

```text
scenario_001
scenario_002
scenario_003
...
```

如果用户只问：

```text
scenario_001 为什么被判定为 FN？
```

但系统只能召回整个 JSON 文件，那么会有几个问题：

1. 文档太长，可能放不进 Prompt；
2. 无关场景太多，会干扰模型回答；
3. 模型需要自己在大文档中查找目标信息，容易出错；
4. 答案很难追溯到具体依据。

所以需要把大文档切成更小的语义单元。

在 RAG 中，一个 chunk 应该尽量表达一个完整含义，比如：

```text
一个指标定义
一个事故案例
一个评价场景
一个失败原因说明
```

---

## 3. 本项目的切块策略

AutoDrive-KB-RAG 中主要有三类数据：

| 数据类型 | 切块方式 | 原因 |
|---|---|---|
| 指标说明 Markdown | 按标题切块 | 每个标题小节通常是一个完整概念 |
| 事故案例 Markdown | 按标题切块 | 每个 Case 通常是一个独立分析单元 |
| 评价 JSON | 按 `scenario_id` 切块 | 一个 scenario 通常对应一次完整评价结果 |
| 普通 txt 文本 | 固定窗口切块 | 没有结构信息时的兜底方案 |

---

## 4. Markdown 为什么按标题切

Markdown 文档通常有标题结构：

```markdown
## TP 定义

## FP 定义

## FN 定义
```

这种文档适合按标题切块。

例如用户问：

```text
什么是 FP？
```

系统应该优先召回：

```text
## FP 定义
FP，全称 False Positive，表示系统检测出了一个实际不存在的目标。
```

如果不按标题切，而是简单按字符长度切，可能会把一个完整定义切断，影响后续检索效果。

---

## 5. JSON 为什么按 scenario_id 切

自动驾驶评价 JSON 是结构化数据。

一个 scenario 通常包含：

```text
scenario_id
scene_type
metric_name
timestamp_range
objects
tp_count
fp_count
fn_count
failure_reason
```

所以一个 scenario 就是一个自然的评价单元。

例如：

```text
evaluation_result_scenario_001
evaluation_result_scenario_002
```

用户问：

```text
scenario_001 为什么被判定为 FN？
```

系统就应该召回 `scenario_001` 对应的 chunk，而不是整个评价 JSON。

这样可以让检索更精准，也方便后续生成答案时引用具体证据。

---

## 6. Chunk 的统一格式

今天生成的每个 chunk 都包含以下字段：

```json
{
  "chunk_id": "evaluation_result_scenario_001",
  "source": "data/samples/evaluation_result.json",
  "doc_type": "json",
  "text": "...",
  "metadata": {
    "chunk_strategy": "json_by_scenario",
    "scenario_id": "scenario_001",
    "metric_name": "perception_object_detection",
    "scene_type": "urban_crossing"
  }
}
```

其中：

- `chunk_id`：chunk 的唯一编号；
- `source`：来源文件；
- `doc_type`：文档类型，例如 markdown、json、text；
- `text`：真正用于 Embedding 和检索的文本内容；
- `metadata`：额外信息，用于溯源、过滤和调试。

---

## 7. metadata 的作用

metadata 很重要。

它的作用包括：

1. 记录 chunk 来自哪个文件；
2. 标记 chunk 使用了哪种切块策略；
3. 支持按 `scenario_id`、`metric_name`、`scene_type` 过滤；
4. 方便后续查看答案依据；
5. 方便调试 Retriever 为什么召回了某个 chunk。

例如后续用户问：

```text
只看 urban_crossing 场景，有哪些 FN？
```

就可以根据：

```text
scene_type = urban_crossing
```

进行过滤。

如果用户问：

```text
scenario_001 的失败原因是什么？
```

就可以根据：

```text
scenario_id = scenario_001
```

定位对应 chunk。

---

## 8. 今日代码产出

今天完成了两个主要代码文件：

```text
src/chunking/simple_chunker.py
examples/run_day2_chunking_demo.py
```

`simple_chunker.py` 中实现了以下函数：

```text
read_text_file()
make_chunk()
chunk_text_by_window()
chunk_markdown_by_heading()
chunk_json_by_scenario()
chunk_file()
chunk_files()
```

其中：

- `chunk_markdown_by_heading()`：负责按 Markdown 标题切块；
- `chunk_json_by_scenario()`：负责按 JSON 中的 `scenarios` 字段切块；
- `chunk_text_by_window()`：负责普通文本的固定窗口切块；
- `chunk_file()`：根据文件后缀选择不同切块方式；
- `chunk_files()`：批量处理多个文件。

---

## 9. 今日运行命令

在项目根目录运行：

```bash
python examples/run_day2_chunking_demo.py
```

运行后生成：

```text
data/processed/day2_chunks.json
```

正常情况下，输出中应该包含类似 chunk：

```text
metric_doc_sections_1
metric_doc_sections_2
evaluation_result_scenario_001
evaluation_result_scenario_002
accident_case_sections_1
accident_case_sections_2
```

其中：

```text
evaluation_result_scenario_001
evaluation_result_scenario_002
```

说明 JSON 已经成功按场景切块。

---

## 10. 今日总结

今天完成了 AutoDrive-KB-RAG 的 Chunking 初版。

核心理解是：

```text
Chunking 不是简单拆文件，而是把原始资料整理成 RAG 可以检索的知识单元。
```

在本项目中：

```text
指标文档按标题切块
→ 用于回答 TP / FP / FN / Precision / Recall 等定义问题

事故案例按 Case 切块
→ 用于回答具体失败案例和原因分析问题

评价 JSON 按 scenario_id 切块
→ 用于回答某个场景为什么被判定为 TP / FP / FN
```

Day 2 的结果为 Day 3 做准备。下一步将把这些 chunks 转成向量，并实现最小版 TopK Retrieval。