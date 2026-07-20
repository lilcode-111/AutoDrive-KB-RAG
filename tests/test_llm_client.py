import pytest

from src.llm.fake_llm_client import FakeLLMClient
from src.llm.llm_client import LLMClient

def test_llm_client_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        LLMClient()

def test_fake_llm_client_returns_configured_response() -> None:
    client = FakeLLMClient(
        response="FN 表示真实目标存在，但系统没有检测到该目标。"
    )

    answer = client.generate(
        "请根据参考资料解释什么是 FN。"
    )

    assert answer == "FN 表示真实目标存在，但系统没有检测到该目标。"


def test_fake_llm_client_records_prompt_and_call_count() -> None:
    client = FakeLLMClient(response="测试答案")

    assert client.last_prompt is None
    assert client.call_count == 0

    answer = client.generate("   这是测试 Prompt。   ")

    assert answer == "测试答案"
    assert client.last_prompt == "这是测试 Prompt。"
    assert client.call_count == 1

@pytest.mark.parametrize(
    "invalid_prompt",
    [
        "",
        "   ",
        "\n\t",
    ],
)
def test_fake_llm_client_rejects_blank_prompt(
    invalid_prompt: str,
) -> None:
    client = FakeLLMClient(response="测试答案")

    with pytest.raises(
        ValueError,
        match="prompt must not be blank",
    ):
        client.generate(invalid_prompt)


def test_fake_llm_client_rejects_non_string_prompt() -> None:
    client = FakeLLMClient(response="测试答案")

    with pytest.raises(
        TypeError,
        match="prompt must be a string",
    ):
        client.generate(None)  # type: ignore[arg-type]


def test_fake_llm_client_rejects_blank_response() -> None:
    with pytest.raises(
        ValueError,
        match="response must not be blank",
    ):
        FakeLLMClient(response="   ")

