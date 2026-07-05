from fastapi import APIRouter
from app.schemas import DocumentServiceStatusResponse,SupportedFileTypesResponse

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