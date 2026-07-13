from src.retrieval.retrieval_service import RetrievalService

def main() -> None:
    retrieval_service = RetrievalService()

    chunks = [
        {
            "chunk_id": "metric_doc_fp",
            "source": "metric_doc.md",
            "doc_type": "markdown",
            "text": "FP 误检表示系统错误地检测到了不存在的目标。",
            "text_length": len("FP 误检表示系统错误地检测到了不存在的目标。"),
            "metadata": {
                "metric": "FP",
                "chunk_strategy": "manual_demo",
            },
        },
        {
            "chunk_id": "metric_doc_fn",
            "source": "metric_doc.md",
            "doc_type": "markdown",
            "text": "FN 漏检表示真实存在的目标没有被系统检测出来。",
            "text_length": len("FN 漏检表示真实存在的目标没有被系统检测出来。"),
            "metadata": {
                "metric": "FN",
                "chunk_strategy": "manual_demo",
            },
        },
        {
            "chunk_id": "metric_doc_recall",
            "source": "metric_doc.md",
            "doc_type": "markdown",
            "text": "Recall 召回率等于 TP / (TP + FN)。",
            "text_length": len("Recall 召回率等于 TP / (TP + FN)。"),
            "metadata": {
                "metric": "Recall",
                "chunk_strategy": "manual_demo",
            },
        },
    ]

    index_result = retrieval_service.index_chunks(chunks)

    print("Index result:")
    print(index_result)

    query = "什么是 FN 漏检？"
    search_result = retrieval_service.search(query=query, top_k=3)

    print("\nSearch result:")
    print("query:", search_result["query"])
    print("top_k:", search_result["top_k"])
    print("result_count:", search_result["result_count"])

    print("\nTopK results:")
    for item in search_result["results"]:
        print(
            f"rank={item['rank']} "
            f"score={item['score']:.4f} "
            f"chunk_id={item['chunk_id']} "
            f"text={item['text']}"
        )

    
if __name__ == "__main__":
    main()