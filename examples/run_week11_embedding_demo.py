import numpy as np
from src.embeddings.sentence_transformer_client import SentenceTransformerEmbeddingClient

def cosine_score(vec_a,vec_b)->float:
    return float(np.dot(np.array(vec_a),np.array(vec_b)))

def main()->None:
    client = SentenceTransformerEmbeddingClient()

    texts = [
        "FP 误检表示系统错误地检测到了不存在的目标。",
        "FN 漏检表示真实存在的目标没有被系统检测出来。",
        "Recall 召回率等于 TP / (TP + FN)。",
    ]

    query = "什么是FN漏检?"

    text_vectors = client.embed_texts(texts)
    query_vector = client.embed_query(query)

    print("model_name:", client.model_name)
    print("embedding_dimension:", client.get_embedding_dimension())
    print("num_text_vectors:", len(text_vectors))
    print("query_vector_dimension:", len(query_vector))

    print("\nSimilarity scores:")

    for idx,text_vector in enumerate(text_vectors):
        score = cosine_score(query_vector,text_vector)
        print(f"rank_candidate = {idx} score = {score:.4f} text = {texts[idx]}")

if __name__ == "__main__":
    main()