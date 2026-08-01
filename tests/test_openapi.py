from app.main import app


EXPECTED_TAG_NAMES = {
    "health",
    "documents",
    "retrieval",
    "rag",
}

def resolve_openapi_schema(
    schema: dict,
    schema_or_reference: dict,
) -> dict:
    """
    Resolve a local OpenAPI component reference when necessary.
    """
    reference = schema_or_reference.get("$ref")

    if reference is None:
        return schema_or_reference

    schema_name = reference.rsplit("/", 1)[-1]

    return schema["components"]["schemas"][schema_name]


def test_openapi_schema_contains_project_metadata() -> None:
    schema = app.openapi()

    assert schema["info"]["title"] == "AutoDrive-KB-RAG API"
    assert schema["info"]["version"] == "0.1.0"

    description = schema["info"]["description"]

    assert "document upload" in description
    assert "RAG answer generation" in description


def test_openapi_schema_contains_documented_tags() -> None:
    schema = app.openapi()

    tags = {
        tag["name"]: tag["description"]
        for tag in schema["tags"]
    }

    assert set(tags) == EXPECTED_TAG_NAMES

    for description in tags.values():
        assert isinstance(description, str)
        assert description.strip()


def test_openapi_schema_groups_core_endpoints() -> None:
    schema = app.openapi()

    assert (
        schema["paths"]["/health"]["get"]["tags"]
        == ["health"]
    )

    assert (
        schema["paths"]["/api/v1/documents/parse"]["post"]["tags"]
        == ["documents"]
    )

    assert (
        schema["paths"]["/api/v1/retrieval/search"]["post"]["tags"]
        == ["retrieval"]
    )

    assert (
        schema["paths"]["/api/v1/rag/answer"]["post"]["tags"]
        == ["rag"]
    )

def test_retrieval_search_request_schema_is_documented() -> None:
    schema = app.openapi()

    request_schema = schema["components"]["schemas"][
        "RetrievalSearchRequest"
    ]

    properties = request_schema["properties"]

    query_schema = properties["query"]
    top_k_schema = properties["top_k"]

    assert query_schema["minLength"] == 1
    assert "knowledge-base chunks" in query_schema["description"]

    assert top_k_schema["exclusiveMinimum"] == 0
    assert top_k_schema["default"] == 5
    assert "Maximum number" in top_k_schema["description"]


def test_rag_answer_request_schema_is_documented() -> None:
    schema = app.openapi()

    request_schema = schema["components"]["schemas"][
        "RAGAnswerRequest"
    ]

    properties = request_schema["properties"]

    query_schema = properties["query"]
    top_k_schema = properties["top_k"]

    assert query_schema["minLength"] == 1
    assert "Question to answer" in query_schema["description"]

    assert top_k_schema["exclusiveMinimum"] == 0
    assert top_k_schema["default"] == 5
    assert "answer-generation step" in top_k_schema[
        "description"
    ]

def test_core_operations_include_swagger_metadata() -> None:
    schema = app.openapi()

    retrieval_operation = schema["paths"][
        "/api/v1/retrieval/search"
    ]["post"]

    assert (
        retrieval_operation["summary"]
        == "Search indexed knowledge"
    )

    assert (
        "natural-language query"
        in retrieval_operation["description"]
    )

    assert (
        retrieval_operation["responses"]["200"]["description"]
        == "Ranked semantic retrieval results."
    )

    rag_operation = schema["paths"][
        "/api/v1/rag/answer"
    ]["post"]

    assert (
        rag_operation["summary"]
        == "Generate a grounded RAG answer"
    )

    assert (
        "retrieved knowledge-base content"
        in rag_operation["description"]
    )

    assert (
        rag_operation["responses"]["200"]["description"]
        == (
            "Generated answer together with its "
            "supporting sources."
        )
    )

def test_document_upload_operations_include_swagger_metadata() -> None:
    schema = app.openapi()

    parse_operation = schema["paths"]["/api/v1/documents/parse"]["post"]

    assert (parse_operation["summary"] == "Parse an uploaded document")

    assert ("text preview" in parse_operation["description"])

    assert (parse_operation["responses"]["200"]["description"] == "Parsed document metadata and text preview.")

    parse_request_schema = resolve_openapi_schema(
        schema,
        parse_operation["requestBody"]["content"][
            "multipart/form-data"
        ]["schema"],
    )

    parse_file_schema = parse_request_schema["properties"]["file"]

    assert ("Supported extensions" in parse_file_schema["description"])

    chunk_operation = schema["paths"]["/api/v1/documents/parse-and-chunk"]["post"]

    assert (chunk_operation["summary"] == "Parse and chunk an uploaded document")

    assert ("overlapping chunks" in chunk_operation["description"])

    assert (chunk_operation["responses"]["200"]["description"]
        == "Parsed document metadata and generated chunks.")

    chunk_request_schema = resolve_openapi_schema(
        schema,
        chunk_operation["requestBody"]["content"][
            "multipart/form-data"
        ]["schema"],
    )

    chunk_file_schema = chunk_request_schema["properties"]["file"]

    assert ("Supported extensions" in chunk_file_schema["description"])

def test_index_document_operation_includes_swagger_metadata() -> None:
    schema = app.openapi()

    operation = schema["paths"][
        "/api/v1/retrieval/index-document"
    ]["post"]

    assert operation["summary"] == "Index an uploaded document"

    assert (
        "generate embeddings"
        in operation["description"]
    )

    assert (
        operation["responses"]["200"]["description"]
        == "Document parsing and vector-indexing statistics."
    )

    request_schema = resolve_openapi_schema(
        schema,
        operation["requestBody"]["content"][
            "multipart/form-data"
        ]["schema"],
    )

    file_schema = request_schema["properties"]["file"]

    assert "parse, chunk, embed, and index" in file_schema[
        "description"
    ]
