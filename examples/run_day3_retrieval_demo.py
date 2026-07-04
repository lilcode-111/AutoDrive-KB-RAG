import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from week9_autoDrive_RAG.src.retrieval.toy_retriever import ToyRetriever, load_chunks


def print_result(query:str,results):
    print("="*100)
    print(f"Query: {query}")
    print("="*100)

    for idx, result in enumerate(results,start=1):
        print(f"\nTop {idx}")
        print(f"score:{result['score']:.4f}")
        print(f"chunk_id:{result['chunk_id']}")
        print(f"doc_type:{result['doc_type']}")
        print(f"metadata:{result['metadata']}")
        print("-"*100)
        print(result["text"][:600])
        print()

def main():
    chunks_path = ROOT_DIR/"data"/"processed"/"day2_chunks.json"

    chunks = load_chunks(str(chunks_path))
    retriever = ToyRetriever(chunks)

    queries = [
        "什么是 FP 误检?",
        "什么是 FN 误检?",
        "Recall 怎么计算?",
        "scenario_001 为什么被判定为 FN?",
        "scenario_002 为什么是FP",
    ]

    for query in queries:
        results = retriever.search(query=query, top_k=3)
        print_result(query,results)

if __name__ == "__main__":
    main()