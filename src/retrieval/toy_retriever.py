import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

def load_chunks(chunks_path:str)->List[Dict[str,Any]]:
    path = Path(chunks_path)
    return json.loads(path.read_text(encoding="utf-8"))

def tokenize(text:str)->List[str]:
    """
    简单分词函数。

    这里为了不依赖 jieba / sentence-transformers,先做一个 toy tokenizer:
    1. 英文、数字、下划线按单词提取，比如 scenario_001、fp_count;
    2. 中文按单字切分；
    3. 全部转成小写。

    这不是最终工业级分词方式，只用于 Day 3 理解 retrieval 流程。
    """
    text = text.lower()

    english_tokens = re.findall(r"[a-zA-Z0-9_]+",text)
    chinese_tokens = re.findall(r"[\u4e00-\u9fff]", text) #这个\u4e00-\u9fff是什么？  Unicode的汉字编码范围
    
    return english_tokens+chinese_tokens

def text_to_vector(text:str)->Counter:
    """
    把文本转成简单词频向量。
    Counter 可以理解成稀疏向量：
    {
        "fp": 2,
        "误": 1,
        "检": 1
    }
    """
    tokens = tokenize(text)
    return Counter(tokens)

def cosine_similarity(vec1:Counter,vec2:Counter)->float:
    """
    计算两个稀疏词频向量的余弦相似度。
    """
    if not vec1 or not vec2:    #无token,无相似度
        return 0.0
    
    common_tokens = set(vec1.keys())&set(vec2.keys())                       #找共有向量
    dot_product = sum(vec1[token]*vec2[token] for token in common_tokens)    #计算点积

    norm1 = math.sqrt(sum(value*value for value in vec1.values()))
    norm2 = math.sqrt(sum(value*value for value in vec2.values()))

    if norm1 == 0 or norm2 == 0:    #防止长度为0
        return 0.0
    
    return dot_product/(norm1*norm2)

class ToyRetriever:
    """
    一个最小版 Retriever。

    功能：
    1. 读取 chunks;
    2. 给每个 chunk 建立简单向量；
    3. 输入 query;
    4. 返回相似度最高的 TopK chunks。
    """

    def __init__(self,chunks:List[Dict[str,Any]]):
        self.chunks = chunks
        self.chunk_vectors: List[Counter] = [
            text_to_vector(chunk["text"]) for chunk in chunks
        ]

    def _metadata_boost(self, query: str, chunk: Dict[str,Any])->float:
        """
        根据业务字段做简单加分。
        这不是工业级排序算法，只是为了让 toy retriever 更符合自动驾驶评价场景。
        """
        boost = 0.0
        query_lower = query.lower()
        chunk_text_lower = chunk["text"].lower()
        metadata = chunk.get("metadata",{})

        # 1. scenario_id 精确匹配加分
        scenario_id = metadata.get("scenario_id","")
        if scenario_id and scenario_id.lower() in query_lower:
            boost+=0.3

        for keyword in ["tp","fp","fn"]:
            if keyword in query_lower and keyword in chunk_text_lower:
                boost+=0.10
        
        return boost
    
    def search(self,query:str,top_k: int=3)->List[Dict[str,Any]]:
        query_vector = text_to_vector(query)
        scored_results:List[Tuple[float,Dict[str,Any],float,float]] = []

        for chunk,chunk_vector in zip(self.chunks,self.chunk_vectors):
            base_score = cosine_similarity(query_vector,chunk_vector)
            boost_score = self._metadata_boost(query,chunk)
            final_score = base_score + boost_score
            scored_results.append((final_score,chunk,base_score,boost_score))

        scored_results.sort(key=lambda item:item[0], reverse=True)

        results = []
        for final_score, chunk, base_score, boost_score in scored_results[:top_k]:
            result = {
                "score":final_score,
                "base_score": base_score,
                "boost_score": boost_score,
                "chunk_id":chunk["chunk_id"],
                "source":chunk["source"],
                "doc_type":chunk["doc_type"],
                "text":chunk["text"],
                "metadata":chunk["metadata"],
            }
            results.append(result)

        return results
    

        


