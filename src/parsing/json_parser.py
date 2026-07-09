import json
from typing import Any,Dict,List

from src.cleaning.text_cleaner import clean_text,make_preview

IMPORTANT_KEYS = {
    "scenario_id",
    "case_id",
    "scene_id",
    "metric",
    "metric_name",
    "object_id",
    "track_id",
    "result",
    "status",
    "reason",
    "failure_reason",
    "start_time",
    "end_time",
    "tp",
    "fp",
    "fn",
    "tp_count",
    "fp_count",
    "fn_count"
}

#将字节转换成Python
def decode_json_content(content:bytes)->Any:
    """
    Decode uploaded JSON bytes and parse it into Python object.
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("utf-8",errors="replace")
    return json.loads(text)

#从字典里面提取重要字段，从important_keys里面提取
def extract_metadata_from_dict(data:Dict[str,Any])->Dict[str,Any]:
    """
    Extract important autonomous-driving evaluation fields from a JSON dict.
    """
    metadata:Dict[str,Any] = {}

    for key,value in data.items():
        normalized_key = key.lower()

        if normalized_key in IMPORTANT_KEYS:
            metadata[normalized_key] = value
        
    return metadata


#把复杂JSON战平成一行一行的的可读文本
def flatten_json_to_lines(data: Any, prefix:str = "") ->List[str]:
    """
    Convert JSON object into readable lines.

    Example:
    scenario_id: case_001
    metric: track_miss_detection
    result: fail
    """
    lines:List[str] = []

    if isinstance(data,dict):
        for key,value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else str(key)

            if isinstance(value,(dict,list)):
                lines.extend(flatten_json_to_lines(value,new_prefix))
            else: 
                lines.append(f"{new_prefix}:{value}")
    
    elif isinstance(data,list):
        for index,item in enumerate(data):
            new_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            lines.extend(flatten_json_to_lines(item,new_prefix))
        
    else:
        lines.append(f"{prefix}:{data}")
    
    return lines

def build_evaluation_summary(data:Any,metadata:Dict[str,Any])->str:
    """
    Build a readable summary for autonomous-driving evaluation JSON.
    """
    summary_lines:List[str] = []
    summary_lines.append("自动驾驶评价结果 JSON 解析摘要")

    scenario_id = metadata.get("scenario_id") or metadata.get("case_id") or metadata.get("scene_id")
    metric = metadata.get("metric") or metadata.get("metric_name")
    object_id = metadata.get("object_id") or metadata.get("track_id")
    result = metadata.get("result") or metadata.get("status")
    reason = metadata.get("reason") or metadata.get("failure_reason")

    if scenario_id is not None:
        summary_lines.append(f"scenario_id:{scenario_id}")
    
    if metric is not None:
        summary_lines.append(f"metric:{metric}")
    
    if object_id is not None:
        summary_lines.append(f"object_id:{object_id}")
    
    if result is not None:
        summary_lines.append(f"result:{result}")

    if reason is not None:
        summary_lines.append(f"reason:{reason}")
    
    for key in ["tp","fp","fn","tp_count","fp_count","fn_count"]:
        if key in metadata:
            summary_lines.append(f"{key}:{metadata[key]}")
    
    summary_lines.append("")
    summary_lines.append("原始JSON字段展开")
    summary_lines.extend(flatten_json_to_lines(data))
    return clean_text("\n".join(summary_lines))


def parse_evaluation_json(filename:str,content:bytes)->dict:
    """
    Parse autonomous-driving evaluation JSON.

    Return cleaned text, preview, and extracted metadata.
    """
    data = decode_json_content(content)
    metadata:Dict[str,Any]={}

    if isinstance(data,dict):
        metadata = extract_metadata_from_dict(data)

    elif isinstance(data,list):
        metadata["num_records"] = len(data)

        if len(data) > 0 and isinstance(data[0],dict):
            metadata.update(extract_metadata_from_dict(data[0]))
        
    else:
        metadata["json_type"] = type(data).__name__

    cleaned_text = build_evaluation_summary(data,metadata)

    return {
        "filename":filename,
        "file_type":"evaluation_json",
        "text": cleaned_text,
        "text_length":len(cleaned_text),
        "preview":make_preview(cleaned_text),
        "status":"success",
        "metadata":metadata
    }




