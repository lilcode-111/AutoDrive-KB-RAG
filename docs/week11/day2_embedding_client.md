# Week11 Day2 - Embedding Client

## 1. Goal

Week11 Day2 的目标是为 AutoDrive-KB-RAG 增加 embedding 抽象层，完成从文本到向量的最小闭环。

当前目标：

```text
texts / chunks
→ EmbeddingClient
→ dense vectors
→ similarity score

本日暂不实现 vector index，也不接 FastAPI retrieval API。

2. Added Files

本日新增文件：

src/embeddings/__init__.py
src/embeddings/embedding_client.py
src/embeddings/sentence_transformer_client.py
examples/run_week11_embedding_demo.py
docs/week11/day2_embedding_client.md
3. Dependencies

requirements.txt 新增：

sentence-transformers
numpy

安装命令：

pip install -r requirements.txt
4. EmbeddingClient Design

新增抽象基类：

src/embeddings/embedding_client.py

核心代码结构：

from abc import ABC, abstractmethod
from typing import List


class EmbeddingClient(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError

设计目的：

1. 统一 embedding 调用方式
2. 隔离 retrieval 逻辑和具体 embedding 模型
3. 后续可以替换为 bge / e5 / OpenAI / local embedding service
4. retrieval service 只依赖 embed_texts() 和 embed_query()

embed_texts() 用于批量处理文档 chunks：

List[str] → List[List[float]]

embed_query() 用于处理单个用户问题：

str → List[float]
5. SentenceTransformerEmbeddingClient

新增实现类：

src/embeddings/sentence_transformer_client.py

使用模型：

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

选择原因：

1. 支持 multilingual，适合当前中文 query
2. 模型较轻量，适合本地开发
3. 输出 dense embedding，适合语义检索
4. 常见输出维度为 384

核心参数：

normalize_embeddings=True
convert_to_numpy=True
show_progress_bar=False

含义：

normalize_embeddings=True:
将向量归一化为单位向量。后续计算相似度时，dot product 等价于 cosine similarity。

convert_to_numpy=True:
让 sentence-transformers 返回 numpy.ndarray，便于后续矩阵计算。

show_progress_bar=False:
关闭进度条，避免后续作为 FastAPI 服务时终端输出混乱。
6. Query Embedding Design

embed_query() 内部复用 embed_texts()：

def embed_query(self, query: str) -> List[float]:
    if query is None or not str(query).strip():
        raise ValueError("query must be a non-empty string")

    vectors = self.embed_texts([query])
    return vectors[0]

原因：

1. embed_texts() 是批量接口，输入 List[str]
2. query 是单个字符串，所以先包装成 [query]
3. embed_texts([query]) 返回 List[List[float]]
4. 因为只传入一个 query，所以返回结果里只有一个 vector
5. vectors[0] 就是该 query 的 embedding

这样可以保证 query 和 chunk 使用完全一致的 embedding 配置。

7. Demo Script

新增 demo：

examples/run_week11_embedding_demo.py

测试文本：

FP 误检表示系统错误地检测到了不存在的目标。
FN 漏检表示真实存在的目标没有被系统检测出来。
Recall 召回率等于 TP / (TP + FN)。

测试 query：

什么是 FN 漏检？

测试逻辑：

1. 将三条文本转成 text_vectors
2. 将 query 转成 query_vector
3. 分别计算 query_vector 与每个 text_vector 的 dot product
4. 输出 similarity scores
8. Import Path Issue

直接运行：

python examples/run_week11_embedding_demo.py

可能出现：

ModuleNotFoundError: No module named 'src'

原因：

Python 运行 examples/ 下的脚本时，默认把 examples/ 作为搜索路径，
而不是项目根目录，所以找不到 src。

解决方式：

PYTHONPATH=. python examples/run_week11_embedding_demo.py

PYTHONPATH=. 的含义是：

将当前项目根目录加入 Python import 搜索路径。
9. HuggingFace Network Issue

首次运行 SentenceTransformer(model_name) 时，sentence-transformers 会从 HuggingFace 下载模型文件。

本机 WSL 环境直连 HuggingFace 失败：

[Errno 101] Network is unreachable

因此使用 HF 镜像：

HF_ENDPOINT=https://hf-mirror.com PYTHONPATH=. python examples/run_week11_embedding_demo.py

如果下载成功，后续模型会进入本地缓存，再次运行会更快。

10. Smoke Test Result

运行命令：

HF_ENDPOINT=https://hf-mirror.com PYTHONPATH=. python examples/run_week11_embedding_demo.py

实际输出：

Similarity scores:
rank_candidate = 0 score = 0.4936 text = FP 误检表示系统错误地检测到了不存在的目标。
rank_candidate = 1 score = 0.5403 text = FN 漏检表示真实存在的目标没有被系统检测出来。
rank_candidate = 2 score = 0.4516 text = Recall 召回率等于 TP / (TP + FN)。

结果分析：

query = 什么是 FN 漏检？

FN chunk 的 score = 0.5403，为三条文本中最高。
说明 embedding client 已经可以用于基本语义相似度计算。