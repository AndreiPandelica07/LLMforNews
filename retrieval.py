import chromadb
from FlagEmbedding import BGEM3FlagModel
from pathlib import Path


MODEL_NAME = "BAAI/bge-m3"
# Resolve the database beside this project file, independent of the launch directory.
DB_PATH = Path(__file__).resolve().parent / "newsDB_bge_m3"
COLLECTION_NAME = "news-bge-m3"
# Chroma returns cosine distances; candidates above this limit are discarded.
MAX_DISTANCE = 0.53

# Load the query encoder and existing Chroma collection once at startup.
model = BGEM3FlagModel(MODEL_NAME, use_fp16=False)
client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_collection(COLLECTION_NAME)


def embeddQuery(query: str) -> list:
    """Encode one user question into the dense BGE-M3 vector space."""
    return model.encode([query])['dense_vecs'][0].tolist()




def returnMatches(query_embeddings : list, max_results: int)-> list[dict]:
    """Return the nearest passages that pass the configured distance cutoff."""
    result = collection.query(
        query_embeddings=[query_embeddings],
        n_results=min(max_results, collection.count()),
    )
    distances=result["distances"][0]
    metadatas=result["metadatas"][0]
    ranked_matches = []
    # Chroma orders results from the smallest (closest) distance upward.
    for index, distance in enumerate(distances):
        if distance>MAX_DISTANCE:
            continue
        ranked_matches.append({
            "ids": [[result["ids"][0][index]]],
            "documents": [[result["documents"][0][index]]],
            "metadatas": [[metadatas[index]]],
            "distances": [[distance]],
        })

    return ranked_matches


    
