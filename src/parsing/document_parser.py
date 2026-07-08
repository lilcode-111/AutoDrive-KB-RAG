from pathlib import Path
from src.parsing.markdown_parser import parse_markdown_or_txt
from src.parsing.json_parser import parse_evaluation_json
from src.parsing.pdf_parser import parse_pdf_document

def parse_document_by_type(filename:str,content:bytes)->dict:
    """
    Dispatch uploaded document to the correct parser by file suffix.
    """
    suffix = Path(filename).suffix.lower()

    if suffix in {".md",".markdown",".txt"}:
        return parse_markdown_or_txt(filename,content)
    if suffix == ".json":
        return parse_evaluation_json(filename,content)
    if suffix == ".pdf":
        return parse_pdf_document(filename,content)
    
    raise ValueError(f"Unsupported file type: {suffix}")


