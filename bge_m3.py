

import json
from pathlib import Path

import chromadb
from FlagEmbedding import BGEM3FlagModel


MODEL_NAME = "BAAI/bge-m3"
# Keep generated chunks and the persistent index in their project folders.
PROJECT_ROOT = Path(__file__).resolve().parent
CHUNKS_PATH = PROJECT_ROOT / "Data" / "chunks.json"
DB_PATH = PROJECT_ROOT / "newsDB_bge_m3"
COLLECTION_NAME = "news-bge-m3"
CANDIDATE_COUNT = 10


def load_model() -> BGEM3FlagModel:
    """Create the BGE-M3 encoder used for article passages and questions."""
    return BGEM3FlagModel(MODEL_NAME, use_fp16=False)


def build_index() -> None:
    """Rebuild the Chroma collection from Data/chunks.json."""
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing {CHUNKS_PATH.resolve()}; run RAGprocessing.py first.")

    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError("chunks.json is empty")

    model = load_model()
    texts = [chunk["text"] for chunk in chunks]
    encoded = model.encode(texts, batch_size=8, max_length=8192)
    vectors = encoded["dense_vecs"].tolist()

    client = chromadb.PersistentClient(path=str(DB_PATH))

    # Replace the old collection so its vectors match the current chunks.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 128
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        collection.add(
            ids=[str(chunk["chunk_id"]) for chunk in batch],
            embeddings=vectors[start : start + batch_size],
            documents=[chunk["text"] for chunk in batch],
            metadatas=[
                {
                    "url": chunk["url"],
                    "domain": chunk["domain"],
                    "date_of_processing": chunk.get("date_of_processing", ""),
                }
                for chunk in batch
            ],
        )
    print(f"Indexed {collection.count()} chunks in {DB_PATH}/{COLLECTION_NAME}.")



def main() -> None:
    build_index()
   


if __name__ == "__main__":
    main()
