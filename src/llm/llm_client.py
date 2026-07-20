from abc import ABC,abstractmethod

class LLMClient(ABC):
    """
    Abstract interface for text generation models.

    Different LLM providers should implement this interface so that
    RAGService does not depend on a specific SDK or model provider.
    """
    @abstractmethod
    def generate(self, prompt:str)->str:
        """
        Generate an answer from a complete prompt.

        Args:
            prompt: Prompt containing the user query, retrieved context,
                    and answer constraints.

        Returns:
            Generated answer text.
        """
        raise NotImplementedError
    