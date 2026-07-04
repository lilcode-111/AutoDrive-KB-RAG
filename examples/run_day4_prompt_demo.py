import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.retrieval.toy_retriever import ToyRetriever,load_chunks
from src.prompt.prompt_builder import build_rag_prompt

def main():
    chunk_path = ROOT_DIR/"data"/"processed"/"day2_chunks.json"
    chunks = load_chunks(str(chunk_path))
    retriever = ToyRetriever(chunks)

    queries = [
        "什么是FP误检?",
        "Recall怎么计算?",
        "scenario_001 为什么被判定为 FN",
        "scenario_002 为什么被判定为 FP",
    ]

    for query in queries:
        retrieved_chunks = retriever.search(query=query,top_k=3)
        prompt = build_rag_prompt(query=query,retrieved_chunks=retrieved_chunks)

        print("=" * 120)
        print(f"Query: {query}")
        print("=" * 120)
        print(prompt)
        print("\n\n")

if __name__ == "__main__":
    main()