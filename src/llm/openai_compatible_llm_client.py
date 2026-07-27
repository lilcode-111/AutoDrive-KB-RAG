import os
from typing import  Any, Dict, Optional

from openai import OpenAI

from src.llm.llm_client import LLMClient

class OpenAICompatibleLLMClient(LLMClient):
    """
    LLM client backed by an OpenAI-compatible Chat Completions API.

    Configuration can be passed directly or loaded from environment
    variables:

    - OPENAI_API_KEY
    - OPENAI_MODEL
    - OPENAI_BASE_URL (optional)
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: float = 60.0,
            client: Optional[Any] = None,
    )->None:
        resolved_model = (
            model
            if model is not None
            else os.getenv("OPENAI_MODEL","")
        )
    
        if not isinstance(resolved_model,str):
            raise TypeError("model must be a string")

        cleaned_model = resolved_model.strip()

        if not cleaned_model:
            raise ValueError("model must not be blank")

        self.model = cleaned_model

        if client is not None:
            self.client = client
            return

        resolved_api_key = (
            api_key
            if api_key is not None
            else os.getenv("OPENAI_API_KEY", "")
        )

        if not isinstance(resolved_api_key,str):
            raise TypeError("api_key must be a string")
    
        cleaned_api_key = resolved_api_key.strip()

        if not cleaned_api_key:
            raise ValueError("OPENAI_API_KEY must not be blank")

        resolved_base_url = (
            base_url
            if base_url is not None
            else os.getenv("OPENAI_BASE_URL", "")
        )

        if not isinstance(resolved_base_url,str):
            raise TypeError("base_url must be a string")

        client_options: Dict[str,Any] = {
            "api_key": cleaned_api_key,
            "timeout": timeout,
        }
    
        cleaned_base_url = resolved_base_url.strip()

        if cleaned_base_url:
            client_options["base_url"] = cleaned_base_url

        self.client = OpenAI(**client_options)
    
    def generate(self, prompt: str) -> str:
        """
        Generate an answer from a complete grounded RAG prompt.
        """
        
        if not isinstance(prompt,str):
            raise TypeError("prompt must be a string")
        
        cleaned_prompt = prompt.strip()
        
        if not cleaned_prompt:
            raise ValueError("prompt must not be blank")
        
        completion = self.client.chat.completions.create(
            model = self.model,
            messages=[
                {
                    "role": "user",
                    "content": cleaned_prompt,
                }
            ],
        )

        answer = completion.choices[0].message.content

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("LLM returned an empty answer")
        
        return answer.strip()