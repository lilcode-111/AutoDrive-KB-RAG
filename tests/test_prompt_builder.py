import pytest

from src.prompt.prompt_builder import (
    build_rag_prompt,
    format_evidence_chunks,
)


def make_retrieved_chunks():
    return [
        {
            "rank": 1,
            "score": 0.91,
            "chunk_id": "scenario_001",
            "source": "evaluation_result.json",
            "doc_type": "json",
            "text": (
                "scenario_001 中真实标签包含一名行人，"
                "但检测结果中没有对应行人目标。"
            ),
            "metadata": {
                "scenario_id": "scenario_001",
                "failure_type": "FN",
            },
        },
        {
            "rank": 2,
            "score": 0.84,
            "chunk_id": "metric_fn",
            "source": "metric_doc.md",
            "doc_type": "markdown",
            "text": (
                "FN 表示真实目标存在，"
                "但检测系统没有检测到该目标。"
            ),
            "metadata": {
                "metric_name": "FN",
            },
        },
    ]


def test_format_evidence_chunks_contains_retrieval_fields() -> None:
    evidence = format_evidence_chunks(make_retrieved_chunks())

    assert "[S1]" in evidence
    assert "[S2]" in evidence
    assert "evaluation_result.json" in evidence
    assert "metric_doc.md" in evidence
    assert "scenario_001" in evidence
    assert "0.9100" in evidence
    assert "0.8400" in evidence


def test_build_rag_prompt_contains_query_and_context() -> None:
    prompt = build_rag_prompt(
        query="scenario_001 为什么被判定为 FN？",
        retrieved_chunks=make_retrieved_chunks(),
    )

    assert "scenario_001 为什么被判定为 FN？" in prompt
    assert "真实标签包含一名行人" in prompt
    assert "FN 表示真实目标存在" in prompt
    assert "只能依据" in prompt
    assert "根据当前资料无法确定" in prompt


def test_build_rag_prompt_preserves_retrieval_order() -> None:
    prompt = build_rag_prompt(
        query="什么是 FN？",
        retrieved_chunks=make_retrieved_chunks(),
    )

    first_position = prompt.index("evaluation_result.json")
    second_position = prompt.index("metric_doc.md")

    assert first_position < second_position


@pytest.mark.parametrize(
    "invalid_query",
    [
        "",
        "   ",
        "\n\t",
    ],
)
def test_build_rag_prompt_rejects_blank_query(
    invalid_query: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="query must not be blank",
    ):
        build_rag_prompt(
            query=invalid_query,
            retrieved_chunks=make_retrieved_chunks(),
        )


def test_build_rag_prompt_rejects_empty_chunks() -> None:
    with pytest.raises(
        ValueError,
        match="retrieved_chunks must not be empty",
    ):
        build_rag_prompt(
            query="什么是 FN？",
            retrieved_chunks=[],
        )