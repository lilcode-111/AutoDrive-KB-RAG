from pathlib import Path
from src.cleaning.text_cleaner import clean_text,make_preview

SUPPORTED_SUFFIXES = {".md",".markdown",".txt"}

#判断文件类型
def detect_file_type(filename:str)->str:
    suffix = Path(filename).suffix.lower()  #取文件后缀

    if suffix in {".md",".markdown"}:
        return "markdown"
    if suffix == ".txt":
        return "txt"
    
    raise ValueError(f"Unsupported file type: {suffix}")

#讲文件从bytes转为str
def decode_file_content(content:bytes)->str:
    """
    Decode uploaded file bytes into text.

    UTF-8 is used first. If decoding fails, invalid characters are replaced.
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8",errors = "replace")

def parse_markdown_or_txt(filename:str,content:bytes)->dict:
    """
    Parse Markdown/TXT file content.

    Return cleaned text metadata for FastAPI response.
    """
    file_type = detect_file_type(filename)
    raw_text = decode_file_content(content)
    cleaned_text = clean_text(raw_text)

    return {
        "filename": filename,
        "file_type":file_type,
        "text": cleaned_text,
        "text_length":len(cleaned_text),
        "preview":make_preview(cleaned_text),
        "status":"success"
    }
    