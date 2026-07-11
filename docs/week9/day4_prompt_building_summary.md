# Day 4: Retriever + Prompt Building

## 1. 今日目标

今天完成 RAG 中的 Prompt 构造部分。

Day 2 已经完成了文档切块，Day 3 已经完成了 TopK 检索。Day 4 的目标是把检索到的 TopK chunks 整理成一个可以交给 LLM 的 Prompt。

核心链路如下：

```text
用户问题 query
→ Retriever 检索 TopK chunks
→ Prompt Builder 整理参考资料
→ 构造完整 RAG Prompt
→ 后续交给 LLM 生成答案
```

今天暂时不真正调用 LLM，只完成 Prompt 拼接。

---

## 2. 为什么需要 Prompt

从代码层面看，Prompt Builder 确实是在做字符串拼接：

```text
TopK 检索结果
+ 公共说明文本
+ 用户问题
+ 输出格式要求
```

但是在 RAG 系统里，Prompt 的作用不只是拼接文本。

Prompt 的真正作用是：

```text
告诉模型它是谁；
告诉模型可以使用哪些参考资料；
限制模型不能编造；
告诉模型优先看哪些信息；
规定模型按什么格式回答。
```

如果没有 Prompt 约束，LLM 可能会忽略证据、编造原因、输出格式不稳定，或者只解释概念而不分析具体场景。

---

## 3. RAG 中的模块分工

当前 RAG 前半段可以分成三个模块：

```text
Retriever
→ 负责找证据

Prompt Builder
→ 负责组织证据和任务

LLM
→ 负责基于证据生成答案
```

其中：

```text
Retriever 解决“找哪些资料”的问题；
Prompt Builder 解决“怎么把资料交给模型”的问题；
LLM 解决“怎么基于资料生成回答”的问题。
```

Day 4 做的是第二步。

---

## 4. Prompt Builder 的输入和输出

Prompt Builder 的输入包括两部分：

```text
1. 用户问题 query
2. Retriever 返回的 TopK chunks
```

例如：

```text
query:
scenario_002 为什么是 FP？

retrieved_chunks:
Top 1: evaluation_result_scenario_002
Top 2: accident_case_sections_2
Top 3: metric_doc_sections_2
```

Prompt Builder 的输出是一个完整 Prompt：

```text
你是一个自动驾驶评价系统助手。
请只根据给定参考资料回答问题。
如果参考资料不足，请回答“根据当前资料无法确定”。

参考资料：
[参考资料 1]
chunk_id: evaluation_result_scenario_002
内容: ...

[参考资料 2]
chunk_id: accident_case_sections_2
内容: ...

[参考资料 3]
chunk_id: metric_doc_sections_2
内容: ...

用户问题：
scenario_002 为什么是 FP？

请按以下格式回答：
简洁回答：
依据：
不确定信息：
```

---

## 5. 今日代码产出

今天新增了两个主要文件：

```text
src/prompt/prompt_builder.py
examples/run_day4_prompt_demo.py
```

其中：

```text
prompt_builder.py
```

负责把 TopK chunks 格式化成 Prompt。

```text
run_day4_prompt_demo.py
```

负责读取 Day 2 的 chunks，调用 Day 3 的 Retriever，然后用 Prompt Builder 生成最终 Prompt。

---

## 6. prompt_builder.py 的主要函数

### 6.1 format_evidence_chunks()

这个函数负责把 TopK 检索结果整理成 Prompt 中的“参考资料”部分。

输入：

```text
retrieved_chunks
```

输出：

```text
[参考资料 1]
chunk_id: ...
doc_type: ...
metadata:
...

内容:
...

--------------------------------------------------------------------------------
[参考资料 2]
...
```

这个函数不是把多个 chunks 融合成一个新知识，而是把它们按编号排列，方便 LLM 后续引用。

例如：

```text
[参考资料 1]
[参考资料 2]
[参考资料 3]
```

这样后续模型回答时可以写：

```text
依据来自参考资料 1 和参考资料 3。
```

---

### 6.2 build_rag_prompt()

这个函数负责构造完整 Prompt。

输入：

```text
query
retrieved_chunks
```

输出：

```text
完整 RAG Prompt
```

主要包含：

```text
1. 角色设定
2. 回答要求
3. 参考资料
4. 用户问题
5. 输出格式
```

当前 Prompt 中包含这些约束：

```text
只能基于参考资料回答；
不要编造资料中没有的信息；
如果资料不足，需要说明无法确定；
如果涉及 TP / FP / FN，需要说明评价含义；
如果涉及 scenario_id，需要优先结合对应场景评价结果和失败案例；
回答需要包含“简洁回答 / 依据 / 不确定信息”。
```

这些约束的目的，是让后续 LLM 的回答更稳定、更可追溯。

---

## 7. 今日运行命令

在项目根目录运行：

```bash
python examples/run_day4_prompt_demo.py
```

运行后，会看到每个 query 对应的完整 Prompt。

例如：

```text
Query: scenario_002 为什么是 FP？
```

会生成类似：

```text
你是一个自动驾驶评价系统助手。

你的任务是根据给定参考资料回答用户问题。

要求：
1. 只能基于参考资料回答，不要编造资料中没有的信息。
2. 如果参考资料不足，请明确回答“根据当前资料无法确定”。
3. 回答时尽量指出依据来自哪个参考资料编号。
4. 如果问题涉及 TP / FP / FN，需要说明其评价含义。
5. 如果问题涉及 scenario_id，需要优先结合对应场景的评价结果和失败案例。

参考资料：
[参考资料 1]
chunk_id: evaluation_result_scenario_002
doc_type: json
metadata:
scenario_id: scenario_002
metric_name: perception_object_detection
scene_type: highway_following

内容:
...

用户问题：
scenario_002 为什么是 FP？

请按以下格式回答：

简洁回答：
...

依据：
- 参考资料 X：...

不确定信息：
- 如果没有不确定信息，写“无”。
```

---

## 8. 当前项目进度

到 Day 4 为止，AutoDrive-KB-RAG 已经完成了 RAG 前半段：

```text
原始资料
→ Chunking
→ Toy Retrieval
→ Prompt Building
```

对应关系：

```text
Day 2:
原始文档和 JSON → chunks

Day 3:
query → TopK chunks

Day 4:
TopK chunks + query → RAG Prompt
```

这说明系统已经能够完成：

```text
根据用户问题检索证据，并把证据组织成可交给 LLM 的输入。
```

---

## 9. 当前局限

当前 Day 4 还没有真正调用 LLM，所以还不能生成最终答案。

当前系统只做到：

```text
生成 Prompt
```

还没有做到：

```text
Prompt → LLM → Answer
```

因此现在看到 Prompt 时，可能会觉得它只是把 TopK 结果和公共文本拼到一起。

真正接入 LLM 后，Prompt 的作用会更明显：

```text
它会约束模型只能基于证据回答；
它会要求模型输出依据；
它会减少模型编造；
它会让回答格式稳定。
```

---

## 10. 后续增强方向

后续可以继续增强 Prompt Builder：

```text
1. 控制每个 chunk 的最大长度，避免 Prompt 太长；
2. 对参考资料按 score 排序；
3. 在 Prompt 中加入 score；
4. 要求 LLM 输出 JSON 格式；
5. 根据不同问题类型使用不同 Prompt 模板；
6. 接入真实 LLM，完成 Prompt → Answer。
```

其中最重要的下一步是：

```text
接入 LLM，让系统真正基于 Prompt 生成答案。
```

---

## 11. 今日总结

Day 4 完成了 RAG 中的 Prompt 构造。

核心理解：

```text
Prompt Builder 表面上是在拼接 TopK chunks 和公共文本；
本质上是在规定 LLM 如何使用证据、如何避免幻觉、如何按业务规则输出答案。
```

当前项目已经具备以下链路：

```text
文档切块
→ TopK 检索
→ Prompt 构造
```

下一步 Day 5 将开始整理 AutoDrive-KB-RAG 项目结构、README 和运行说明，让这个项目从学习 demo 逐步变成一个可以展示的 GitHub 项目。