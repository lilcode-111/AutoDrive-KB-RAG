import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.chunking.simple_chunker import chunk_files

def main():
    sample_files = [
        ROOT_DIR/"data"/"samples"/"metric_doc.md",
        ROOT_DIR / "data" / "samples" / "evaluation_result.json",
        ROOT_DIR / "data" / "samples" / "accident_case.md",
    ]

    chunks = chunk_files([str(path) for path in sample_files])

    output_path = ROOT_DIR/"data"/"processed"/"day2_chunks.json"
    output_path.write_text(
        json.dumps(chunks,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )
    print(f"Total chunks: {len(chunks)}")
    print(f"Saved to: {output_path}")
    print()
    for chunk in chunks:
        print("=" * 80)
        print(f"chunk_id: {chunk['chunk_id']}")
        print(f"source: {chunk['source']}")
        print(f"doc_type: {chunk['doc_type']}")
        print(f"metadata: {chunk['metadata']}")
        print("-" * 80)
        print(chunk["text"][:500])
        print()

if __name__ == "__main__":
    main()