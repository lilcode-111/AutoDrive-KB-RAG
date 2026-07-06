from fastapi import APIRouter, UploadFile,File,HTTPException
from app.schemas import DocumentServiceStatusResponse,SupportedFileTypesResponse,ParseDocumentResponse
from src.parsing.markdown_parser import parse_markdown_or_txt

router = APIRouter(
    prefix = "/api/v1/documents",
    tags = ["documents"]
)

@router.get("/status",response_model=DocumentServiceStatusResponse)
def document_service_status()->DocumentServiceStatusResponse:
    return DocumentServiceStatusResponse(
        status = "ok",
        module = "document",
        message="Document parsing and upload APIs will be implemented in Week10 Day2-Day5."
    )

@router.get("/supported-file-types",response_model=SupportedFileTypesResponse)
def supported_file_types()->SupportedFileTypesResponse:
    return SupportedFileTypesResponse(
        supported_file_types=[".md",".txt",".json",".pdf"],
        note = "Markdown/TXT will be implemented first, then JSON and PDF."
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
        content = await file.read()
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
        result = parse_markdown_or_txt(file.filename,content)
        return ParseDocumentResponse(
            filename =  result["filename"],
            file_type = result["file_type"],
            text_length = result["text_length"],
            preview = result["preview"],
            status = result["status"]
        ) 
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc))
