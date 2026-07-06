import re


#统一换行符
def normalize_newlines(text:str)->str:
    """Normalize Windows/Mac newlines to Unix newlines."""
    return text.replace("\r\n","\n").replace("\r","\n")

#删除每一行末尾多余空格
def strip_trailing_spaces(text:str)->str:
    """Remove trailing spaces from each line."""
    lines = text.split("\n")
    return "\n".join(line.rstrip() for line in lines)

#把连续多行空格删掉
def collapse_blank_lines(text:str,max_blank_lines:int = 2)->str:
    """Collapse too many continuous blank lines."""
    pattern = r"\n{" + str(max_blank_lines+2) + r",}"
    replacement = "\n"*(max_blank_lines+1)
    return re.sub(pattern,replacement,text)


def clean_text(text:str)->str:
    """
    Basic text cleaning for Markdown/TXT documents.

    This function keeps Markdown headings and domain keywords,
    but removes unnecessary whitespace.
    """
    text = normalize_newlines(text)
    text = strip_trailing_spaces(text)
    text = collapse_blank_lines(text)
    return text.strip()

#作为预览，不直接返回所有的char
def make_preview(text:str,max_chars:int = 300)->str:
    """Return a short preview for API response."""
    if len(text) <=max_chars:
        return text
    return text[:max_chars] + "..."