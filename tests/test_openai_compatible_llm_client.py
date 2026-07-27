from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from src.llm.openai_compatible_llm_client import (
    OpenAICompatibleLLMClient,
)


class FakeCompletions:
    def __init__(
        self,
        response_text: str,
    ) -> None:
        self.response_text = response_text
        self.last_request: Dict[str, Any] | None = None
        self.call_count = 0

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
    ) -> Any:
        self.last_request = {
            "model": model,
            "messages": messages,
        }
        self.call_count += 1

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=self.response_text,
                    )
                )
            ]
        )


class FakeOpenAIClient:
    def __init__(
        self,
        response_text: str,
    ) -> None:
        self.completions = FakeCompletions(response_text)

        self.chat = SimpleNamespace(
            completions=self.completions,
        )


def test_openai_client_generates_answer() -> None:
    sdk_client = FakeOpenAIClient(
        response_text="  FN 表示漏检。[S1]  "
    )

    llm_client = OpenAICompatibleLLMClient(
        model="test-model",
        client=sdk_client,
    )

    answer = llm_client.generate(
        "请根据资料解释 FN。"
    )

    assert answer == "FN 表示漏检。[S1]"
    assert sdk_client.completions.call_count == 1

    assert sdk_client.completions.last_request == {
        "model": "test-model",
        "messages": [
            {
                "role": "user",
                "content": "请根据资料解释 FN。",
            }
        ],
    }


@pytest.mark.parametrize(
    "invalid_prompt",
    [
        "",
        "   ",
        "\n\t",
    ],
)
def test_openai_client_rejects_blank_prompt(
    invalid_prompt: str,
) -> None:
    llm_client = OpenAICompatibleLLMClient(
        model="test-model",
        client=FakeOpenAIClient(response_text="测试答案"),
    )

    with pytest.raises(
        ValueError,
        match="prompt must not be blank",
    ):
        llm_client.generate(invalid_prompt)


def test_openai_client_rejects_blank_model() -> None:
    with pytest.raises(
        ValueError,
        match="model must not be blank",
    ):
        OpenAICompatibleLLMClient(
            model="   ",
            client=FakeOpenAIClient(response_text="测试答案"),
        )


def test_openai_client_rejects_empty_answer() -> None:
    llm_client = OpenAICompatibleLLMClient(
        model="test-model",
        client=FakeOpenAIClient(response_text="   "),
    )

    with pytest.raises(
        RuntimeError,
        match="LLM returned an empty answer",
    ):
        llm_client.generate("测试 Prompt")