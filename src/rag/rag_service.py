import logging
from typing import Any,Dict
from src.llm.llm_client import LLMClient
from src.prompt.prompt_builder import build_rag_prompt
from src.retrieval.retrieval_service import RetrievalService

INSUFFICIENT_CONTEXT_ANSWER = "根据当前资料无法确定。"

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service layer for the Week12 RAG answer pipeline.

    RAGService connects:

    1. RetrievalService
    2. PromptBuilder
    3. LLMClient

    Pipeline:

    query
    -> retrieve TopK chunks
    -> build grounded prompt
    -> call LLM
    -> return answer and original sources
    """
    def __init__(self,
                 retrieval_service: RetrievalService,
                 llm_client: LLMClient,
                 ) -> None:
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client

    def answer(self,query: str,top_k: int = 5,)->Dict[str,Any]:
        """
        Answer a user question using retrieval-augmented generation.

        Args:
            query:
                User question.
            top_k:
                Number of chunks retrieved as context.

        Returns:
            A dictionary containing the answer and retrieval sources.

        Raises:
            TypeError:
                If query is not a string or top_k is not an integer.
            ValueError:
                If query is blank or top_k is not positive.
        """
        if not isinstance(query,str):
            raise TypeError("query must be a string")
        
        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("query must not be blank")
        
        if not isinstance(top_k, int):
            raise TypeError("top_k must be an integer")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        
        logger.info(
            "rag answer request top_k=%d query_length=%d",
            top_k,
            len(cleaned_query),
        )
        
        search_result = self.retrieval_service.search(
            query=cleaned_query,
            top_k=top_k,
        )

        retrieved_chunks = search_result.get("results") or []

        logger.info(
            "rag retrieval completed source_count=%d",
            len(retrieved_chunks),
        )

        if not retrieved_chunks:
            logger.warning("rag answer skipped because no context was retrieved")

            return {
                "query": cleaned_query,
                "answer": INSUFFICIENT_CONTEXT_ANSWER,
                "answer_status": "insufficient_context",
                "source_count": 0,
                "sources": [],
            }
        
        prompt = build_rag_prompt(
            query=cleaned_query,
            retrieved_chunks=retrieved_chunks
        )

        logger.debug("rag prompt built prompt_length=%d", len(prompt),)

        logger.info(
            "calling llm generation source_count=%d",
            len(retrieved_chunks),
        )

        generated_answer = self.llm_client.generate(prompt)

        logger.info("rag answer generated answer_length=%d", len(generated_answer),)

        return {
            "query": cleaned_query,
            "answer": generated_answer,
            "answer_status": "answered",
            "source_count": len(retrieved_chunks),
            "sources": retrieved_chunks,
        }
