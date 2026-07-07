from fastapi import APIRouter, UploadFile,File,HTTPException
from app.schemas import DocumentServiceStatusResponse,SupportedFileTypesResponse,ParseDocumentResponse
from src.parsing.markdown_parser import parse_markdown_or_txt
from pathlib import Path
from src.parsing.json_parser import parse_evaluation_json


router = APIRouter(
    prefix = "/api/v1/documents",
    tags = ["documents"]
)

def parse_uploaded_document(filename:str,content:bytes)->dict:
    suffix = Path(filename).suffix.lower()

    if suffix in {".md",".markdown",".txt"}:
        return parse_markdown_or_txt(filename,content)
    if suffix == ".json":
        return parse_evaluation_json(filename,content)
    
    raise ValueError(f"Unsupported file type: {suffix}")    


@router.get("/status",response_model=DocumentServiceStatusResponse)
def document_service_status()->DocumentServiceStatusResponse:
    return DocumentServiceStatusResponse(
        status = "ok",
        module = "documents",
        message="Document parsing and upload APIs will be implemented in Week10 Day2-Day5."
    )

@router.get("/supported-file-types",response_model=SupportedFileTypesResponse)
def supported_file_types()->SupportedFileTypesResponse:
    return SupportedFileTypesResponse(
        supported_file_types=[".md",".txt",".json",".pdf"],
        note = "Markdown/TXT/JSON parser is implemented. PDF will be added later."
    )

@router.post("/parse",response_model=ParseDocumentResponse)
async def parse_document_response(file:UploadFile = File(...))->ParseDocumentResponse:
    """
    Upload and parse a Markdown/TXT document.

    Current Day2 scope:
    - support .md / .markdown / .txt
    - decode file content
    - clean whitespace
    - return text length and preview
    """
    try:
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
        content = await file.read()
        result = parse_uploaded_document(file.filename,content)
        return ParseDocumentResponse(
            filename =  result["filename"],
            file_type = result["file_type"],
            text_length = result["text_length"],
            preview = result["preview"],
            status = result["status"],
            metadata=result.get("metadata",{}),
        ) 
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc))
