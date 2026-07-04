import json
import re    #这个是干嘛的
from pathlib import Path
from typing import Any, Dict, List


def read_text_file(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def make_chunk(
    chunk_id: str,
    source: str,
    doc_type: str,
    text: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "source": source,
        "doc_type": doc_type,
        "text": text.strip(),
        "metadata": metadata,
    }


def chunk_text_by_window(
    text: str,
    source: str,
    doc_type: str,
    chunk_size: int = 500,
    overlap: int = 80,
) -> List[Dict[str, Any]]:
    """
    按字符窗口切块。
    优点：简单稳定。
    缺点：可能切断语义。
    """
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]

        if chunk_text.strip():
            chunks.append(
                make_chunk(
                    chunk_id=f"{Path(source).stem}_window_{idx}",
                    source = source,
                    doc_type = doc_type,
                    text = chunk_text,
                    metadata={
                        "chunk_strategy":"fixed_window",
                        "start_char":start,
                        "end_char":end,
                        "chunk_size":chunk_size,
                        "overlap":overlap,
                    },
                )
            )
        
        if end == len(text):
            break

        start = end-overlap
        idx+=1
    return chunks

def chunk_markdown_by_heading(file_path:str)->List[Dict[str,Any]]:
    """
    按 Markdown 标题切块。
    适合指标文档、事故案例说明等结构化文本。
    """
    text = read_text_file(file_path)
    source = str(file_path)
    doc_type = "markdown"

    pattern = re.compile(r"(?=^#{1,6}\s+)",re.MULTILINE)   #正则表达式,读取标题下的内容
    sections = [section.strip() for section in pattern.split(text) if section.strip()]

    chunks = []

    for idx,section in enumerate(sections):
        first_line = section.splitlines()[0].strip() if section.splitlines() else ""
        title = first_line.lstrip("#").strip() if first_line.startswith("#") else "Untitled"

        chunks.append(
            make_chunk(
                chunk_id=f"{Path(source).stem}_sections_{idx}",
                source=source,
                doc_type=doc_type,
                text=section,
                metadata={
                    "chunk_strategy":"markdown_heading",
                    "section_title":title,
                    "section_index":idx,
                },
            )
        )
    return chunks

def chunk_json_by_scenario(file_path: str)->List[Dict[str,Any]]:
    """
    按 scenario_id 切评价 JSON。
    适合自动驾驶评价结果，因为一个 scenario 通常就是一个独立分析单元。
    """
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    source = str(path)
    doc_type = "json"
    chunks = []

    project = data.get("project","")
    version = data.get("version","")
    scenarios = data.get("scenarios",[])

    if isinstance(scenarios,list):    #判断是否是列表
        for idx,scenario in enumerate(scenarios):
            scenario_id = scenario.get("scenario_id",f"scenario_id{idx}")
            metric_name = scenario.get("metric_name","")
            scene_type = scenario.get("scene_type","")

            text = json.dumps(
                {
                    "project":project,
                    "version":version,
                    "scenario":scenario,
                },
                ensure_ascii= False,
                indent=2,
            )

            chunks.append(
                make_chunk(
                    chunk_id = f"{path.stem}_{scenario_id}",
                    source = source,
                    doc_type = doc_type,
                    text = text,
                    metadata={
                        "chunk_strategy": "json_by_scenario",
                        "scenario_id": scenario_id,
                        "metric_name": metric_name,
                        "scene_type": scene_type,
                        "scenario_index": idx,
                    },
                )
            )
    else:
        chunks.append(
            make_chunk(
                chunk_id = f"{path.stem}_full_json",
                source = source,
                doc_type = doc_type,
                text = json.dumps(data,ensure_ascii=False,indent=2),
                metadata={
                    "chunk_strategy": "full_json",
                }
            )
        )
    return chunks

def chunk_file(file_path:str)->List[Dict[str,Any]]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        return chunk_json_by_scenario(file_path)
    
    if suffix in [".md",".markdown"]:
        return chunk_markdown_by_heading(file_path)
    
    if suffix in [".txt"]:
        text = read_text_file(file_path)
        return chunk_text_by_window(
            text = text,
            source = str(file_path),
            doc_type = "text",
        )
    
    raise ValueError(f"Unsupported file type: {suffix}")

def chunk_files(file_paths: List[str])->List[Dict[str,Any]]:
    all_chunks =[]
    for file_path in file_paths:
        chunks = chunk_file(file_path)
        all_chunks.extend(chunks)
    return all_chunks
    






        