import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Article records and their generated retrieval chunks are stored under Data/.
DATA_DIR = PROJECT_ROOT / "Data"
OUTPUT_PATH = DATA_DIR / "output.json"
CHUNKS_PATH = DATA_DIR / "chunks.json"


def chunking(articles: dict, max_per_chunk: int) -> list[dict]:
    #Split article paragraphs into word-limited records for vector indexing.
    chunks=[]
    current=[]
    for url, article in articles.items():
        current_wordcount=0
        for p in article['paragraphs']:
            if(current_wordcount+len(p.split())>max_per_chunk):
                chunks.append({"text":" ".join(item['paragraphs'] for item in current) ,
                               "domain":article['domain'],
                               "url": url,
                               "date_of_processing":article['date'],
                               "chunk_id":len(chunks)
                              })
                current=[]
                current_wordcount=0
            current.append({"paragraphs":p,
                            "url": url})
            current_wordcount+=len(p.split())
        if current:
            chunks.append({"text":" ".join(item['paragraphs'] for item in current),
                        "domain":article['domain'],
                        "url": url,
                        "date_of_processing":article['date'],
                        "chunk_id":len(chunks)
                        })
            current=[]
    
    return chunks


def main() -> None:
    """Read scraped articles and write the corresponding chunks JSON file."""
    if not OUTPUT_PATH.exists() or OUTPUT_PATH.stat().st_size == 0:
        raise FileNotFoundError(f"Missing article data: {OUTPUT_PATH}")

    data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    chunks = chunking(data, 200)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(chunks)} chunks to {CHUNKS_PATH}.")


if __name__ == "__main__":
    main()
