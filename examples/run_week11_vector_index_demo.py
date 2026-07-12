from src.embeddings.sentence_transformer_client import SentenceTransformerEmbeddingClient
from src.retrieval.vector_index import InMemoryVectorIndex

def main() ->None:
    embedding_client = SentenceTransformerEmbeddingClient()
    vector_index = InMemoryVectorIndex()

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

    texts = [chunk["text"] for chunk in chunks]
    vectors = embedding_client.embed_texts(texts)

    vector_index.add_chunks(chunks=chunks,vectors=vectors)

    query = "什么是 FN 漏检？"
    query_vector = embedding_client.embed_query(query)

    results = vector_index.search(query_vector=query_vector,top_k=3)

    print("index_chunk_count:", vector_index.count())
    print("query:", query)
    print("\nTopK results:")

    for item in results:
        print(
            f"rank={item['rank']} "
            f"score={item['score']:.4f} "
            f"chunk_id={item['chunk_id']} "
            f"text={item['text']}"
        )

if __name__ == "__main__":
    main()