from typing import Any, Dict,List

def format_evidence_chunks(retrieved_chunks: List[Dict[str,Any]])->str:
    """
    把 TopK 检索结果格式化成 Prompt 中的参考资料部分。
    """
    evidence_blocks = []

    for idx, chunk in enumerate(retrieved_chunks,start=1):
        chunk_id = chunk.get("chunk_id","")
        doc_type = chunk.get("doc_type","")
        metadata = chunk.get("metadata",{})
        text = chunk.get("text","")

        scenario_id = metadata.get("scenario_id","")
        metric_name = metadata.get("metric_name","")
        scene_type = metadata.get("scene_type","")
        section_title = metadata.get("section_title","")

        metadata_lines = []
        if scenario_id:
            metadata_lines.append(f"scenario_id: {scenario_id}")
        if metric_name:
            metadata_lines.append(f"metric_name: {metric_name}")
        if scene_type:
            metadata_lines.append(f"scene_type: {scene_type}")
        if section_title:
            metadata_lines.append(f"section_title:{section_title}")

        metadata_text = "\n".join(metadata_lines) if metadata_lines else "无"

        evidence_block = f"""[参考资料{idx}]
                            chunk_id:{chunk_id}
                            doc_type:{doc_type}
                            metadata:{metadata_text}
                            内容:{text}
                            """
        evidence_blocks.append(evidence_block)
    return "\n" + ("-"*80+"\n").join(evidence_blocks)

def build_rag_prompt(query:str,retrieved_chunks:List[Dict[str,Any]])->str:
    """
    根据用户问题和检索到的 chunks 构造 RAG Prompt。
    """
    evidence_text = format_evidence_chunks(retrieved_chunks)
    prompt = f"""你是一个自动驾驶评价系统助手。
    你的任务是根据给定参考资料回答用户问题。

    要求：
    1. 只能基于参考资料回答，不要编造资料中没有的信息。
    2. 如果参考资料不足，请明确回答“根据当前资料无法确定”。
    3. 回答时尽量指出依据来自哪个参考资料编号。
    4. 如果问题涉及 TP / FP / FN，需要说明其评价含义。
    5. 如果问题涉及 scenario_id，需要优先结合对应场景的评价结果和失败案例。

    参考资料：
    {evidence_text}

    用户问题：
    {query}

    请按以下格式回答：

    简洁回答：
    ...

    依据：
    - 参考资料 X：...

    不确定信息：
    - 如果没有不确定信息，写“无”。
    """
    return prompt
    
        