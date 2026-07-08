from io import BytesIO
from typing import Any,Dict,List
from pypdf import PdfReader
from src.cleaning.text_cleaner import clean_text,make_preview

def extract_text_from_pdf(content:bytes)->Dict[str,Any]:
    """
    Extract text from uploaded PDF bytes.

    Current scope:
    - support text-based PDFs
    - scanned image PDFs may return empty text
    """
    pdf_file = BytesIO(content)
    reader = PdfReader(pdf_file)

    page_texts:List[str] = []

    for page_index,page in enumerate(reader.pages):
        text = page.extract_text() or ""

        if text.strip():
            page_texts.append(f"[Page {page_index +1}]\n{text}")
        
    full_text = "\n\n".join(page_texts)

    return{
        "num_pages":len(reader.pages),
        "extracted_pages":len(page_texts),
        "text":full_text
    }

def parse_pdf_document(filename:str,content:bytes)->dict:
    """
    Parse PDF document content.

    Return cleaned text metadata for FastAPI response.
    """
    pdf_result = extract_text_from_pdf(content)
    cleaned_text = clean_text(pdf_result["text"])

    metadata = {
        "num_pages" :pdf_result["num_pages"],
        "extracted_pages":pdf_result["extracted_pages"],
        "has_text":bool(cleaned_text)
    }

    if not cleaned_text:
        cleaned_text = (
            "No extractable text found in this PDF. "
            "The file may be a scanned image PDF."
        )

    return {
        "filename":filename,
        "file_type":"pdf",
        "text_length":len(cleaned_text),
        "preview":make_preview(cleaned_text),
        "status":"success",
        "metadata":metadata
    }