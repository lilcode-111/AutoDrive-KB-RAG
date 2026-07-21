from typing import Any, Dict,List
import json

def format_evidence_chunks(retrieved_chunks: List[Dict[str,Any]])->str:
    """
    把 TopK 检索结果格式化成 Prompt 中的参考资料部分。

    Format retrieved chunks as evidence blocks for the RAG prompt.

    Args:
        retrieved_chunks:
            TopK results returned by RetrievalService.search().

    Returns:
        Formatted evidence text.

    Raises:
        ValueError:
            If no retrieved chunks are provided.
    """
    if not retrieved_chunks:
        raise ValueError("retrieved_chunks must not be empty")
    

    evidence_blocks: List[str] = []

    for index, chunk in enumerate(retrieved_chunks,start=1):
        rank = chunk.get("rank",index)
        score = chunk.get("score")
        chunk_id = str(chunk.get("chunk_id",""))
        source = str(chunk.get("source",""))
        doc_type = str(chunk.get("doc_type",""))
        metadata = chunk.get("metadata") or {}
        text = str(chunk.get("text","")).strip()

        if not text:
            raise ValueError(
                f"retrieved chunk at index {index - 1} "
                "must contain non-empty text"
            )
        
        if isinstance(score, (int, float)):
            score_text = f"{float(score):.4f}"
        else:
            score_text = "N/A"

        metadata_text = json.dumps(
            metadata,
            ensure_ascii=False,
            sort_keys=True,
        )

        evidence_block = "\n".join(
                            [
                                f"[S{index}]",
                                f"rank: {rank}",
                                f"score: {score_text}",
                                f"source: {source}",
                                f"chunk_id: {chunk_id}",
                                f"doc_type: {doc_type}",
                                f"metadata: {metadata_text}",
                                "content:",
                                text,
                            ])
        evidence_blocks.append(evidence_block)
    return "\n\n---\n\n".join(evidence_blocks)

def build_rag_prompt(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> str:
    """
    Build a grounded RAG prompt from a user query and retrieved chunks.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("query must not be blank")

    evidence_text = format_evidence_chunks(retrieved_chunks)

    return (
        "你是一个自动驾驶评价知识库助手。\n\n"
        "回答规则：\n"
        "1. 只能依据下面提供的参考资料回答。\n"
        "2. 不得编造参考资料中没有的信息。\n"
        "3. 如果资料不足，请明确回答“根据当前资料无法确定”。\n"
        "4. 引用依据时使用 [S1]、[S2] 等编号。\n"
        "5. 如果问题涉及 TP、FP 或 FN，需要解释对应评价含义。\n"
        "6. 如果问题涉及 scenario_id，需要优先结合对应场景资料。\n\n"
        "参考资料：\n"
        f"{evidence_text}\n\n"
        "用户问题：\n"
        f"{cleaned_query}\n\n"
        "请直接给出简洁回答，并标注使用的参考资料编号。"
    )
    
        