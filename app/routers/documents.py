from fastapi import APIRouter, UploadFile,File,HTTPException
from app.schemas import DocumentServiceStatusResponse,SupportedFileTypesResponse,ParseDocumentResponse,ParseAndChunkResponse
#from src.parsing.markdown_parser import parse_markdown_or_txt
#from pathlib import Path
#from src.parsing.json_parser import parse_evaluation_json
from src.parsing.document_parser import parse_document_by_type
from src.chunking.simple_chunker import chunk_parsed_document


router = APIRouter(
    prefix = "/api/v1/documents",
    tags = ["documents"]
)

"""
def parse_uploaded_document(filename:str,content:bytes)->dict:
    suffix = Path(filename).suffix.lower()

    if suffix in {".md",".markdown",".txt"}:
        return parse_markdown_or_txt(filename,content)
    if suffix == ".json":
        return parse_evaluation_json(filename,content)
    
    raise ValueError(f"Unsupported file type: {suffix}")    
"""

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
        note = "Markdown/TXT/JSON/PDF parser is implemented."
    )

@router.post(
    "/parse",
    response_model=ParseDocumentResponse,
    summary="Parse an uploaded document",
    description=(
        "Upload a supported Markdown, text, JSON, or PDF file "
        "and return normalized parsing metadata and a text preview."
    ),
    response_description=(
        "Parsed document metadata and text preview."
    ),
)
async def parse_document_response(
    file: UploadFile = File(
        ...,
        description=(
            "Document file to parse. Supported extensions include "
            ".md, .markdown, .txt, .json, and .pdf."
        ),
    ),
) -> ParseDocumentResponse:
    """
    Upload and parse a Markdown/TXT document.

    Current Day2 scope:
    - support .md / .markdown / .txt/.json / .pdf
    - decode or extract text
    - clean or summarize text
    - return text length, preview, and metadata
    """
    try:
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
        content = await file.read()
        result = parse_document_by_type(file.filename,content)
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

@router.post(
    "/parse-and-chunk",
    response_model=ParseAndChunkResponse,
    summary="Parse and chunk an uploaded document",
    description=(
        "Upload a supported document, extract normalized text, "
        "and split the text into overlapping chunks for downstream "
        "indexing."
    ),
    response_description=(
        "Parsed document metadata and generated chunks."
    ),
)
async def parse_and_chunk_document(
    file: UploadFile = File(
        ...,
        description=(
            "Document file to parse and chunk. Supported extensions "
            "include .md, .markdown, .txt, .json, and .pdf."
        ),
    ),
) -> ParseAndChunkResponse:
    """
    Upload, parse, clean, and chunk a document.

    Current Day5 scope:
    - support .md / .markdown / .txt / .json / .pdf
    - parse document into cleaned text
    - split text into chunks
    - return chunk list with metadata
    """
    try:
        if file.filename is None:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must have a filename."
            )

        content = await file.read()
        parse_result = parse_document_by_type(file.filename, content)

        text = parse_result.get("text", "")
        metadata = parse_result.get("metadata", {})

        chunks = chunk_parsed_document(
            text=text,
            filename=parse_result["filename"],
            file_type=parse_result["file_type"],
            base_metadata=metadata,
            chunk_size=500,
            overlap=80,
        )

        return ParseAndChunkResponse(
            filename=parse_result["filename"],
            file_type=parse_result["file_type"],
            status=parse_result["status"],
            text_length=parse_result["text_length"],
            chunk_count=len(chunks),
            chunks=chunks,
            metadata=metadata,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))