from typing import Optional
from src.llm.llm_client import LLMClient

class FakeLLMClient(LLMClient):
    """
    Deterministic LLM client for unit tests and local development.

    It does not access the network or call a real language model.
    """
    def __init__(self,response:str = "This is a fake LLM answer.",) -> None:
        if not isinstance(response,str):
            raise TypeError("response must be a string")
        
        cleaned_response = response.strip()

        if not cleaned_response:
            raise ValueError("response must not be blank")
        
        self.response = cleaned_response
        self.last_prompt : Optional[str] = None
        self.call_count: int = 0

    def generate(self, prompt: str) -> str:
        if not isinstance(prompt,str):
            raise TypeError("prompt must be a string")
        
        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            raise ValueError("prompt must not be blank")
        
        self.last_prompt = cleaned_prompt
        self.call_count += 1

        return self.response