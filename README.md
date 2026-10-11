
# LLMnews

The following project represents a pipeline made to fact check( or answer to questions ) about Romanian news from the sites included (digi24, stirilekanaltv, protv)- considered as "safer information providers" by me.

CRAWLER

The integrated crawler scans the "new" news section of each of the mentioned domains, extracting all href link information.
Upon removing any duplicates or unuseful paths, the crawler prepares the links and "ships" them for scraping.

SCRAPER 

The scraper then extracts all paragraphs within the HTML body of all passed articles that fit our criteria. 
ALL LINKS can be scraped again within 24 hours(considered that's the window for updates on them, don't take this as a fact) of their first instance. (to label them by a date - forgot to scrape the article data as well)----- This information is stored within "known_data.json".

RAGPROCESSING

This script chunks by a max amount of words/chunk. It restricts any chunks having content about two different topics by creating a new chunk each time we iterate through the articles found.

EMBEDDING OF THE CHUNKS AND DATABASE

After chunking, the entire data gets embedded and added to a local Chroma collection. This vector database will be interrogated whenever the user inputs a prompt, using cosine similarity (HNSW algorithm through the Chroma framework).

MODEL RECOMMENDATIONS

The final model chosen is "Qwen.3:8b", locally run through Ollama servers. The model can be a bit heavy, make sure your machine has enough GPU power and RAM to support it. 
Through experimentation I unfortunately haven't gotten any smaller model to successfully complete the tasks needed for the project. 
Have experimented with: Llama-3:1B/Qwen 2.5:3B/Qwen 3:1b/Qwen 3:4B. All of the above models hallucinated often, couldn't compose grammatically correct Romanian sentences and lacked when it came to context for answers. I have considered that the lower-end models lacked the capacity, but feel free to play along with other models.




## Requirements

- Python 3.10 or later
- Ollama installed and running
- The Ollama model `qwen3:8b`
- Python packages: `beautifulsoup4`, `requests`, `chromadb`, `FlagEmbedding`, `ollama`, and `torch`
- The BGE-M3 model (`BAAI/bge-m3`), downloaded by FlagEmbedding on first use

Install Python packages from the project root:

```bash
python -m pip install -r requirements.txt
```

Download the LLM once and make sure Ollama is running:

```bash
ollama pull qwen3:8b
ollama serve
```

If Ollama is already running as a background service, the `ollama serve` command may report that the port is in use; in that case, leave the existing service running.

## Build the local data and search index

Generated article data and the Chroma database are excluded from Git. On a fresh checkout, run the pipeline below to create them before starting the app:

```bash
python Crawler_Scraper/mainCrawler.py
python Rag/RAGprocessing.py
python bge_m3.py
```

The crawler writes article data to `Data/`, the RAG processor creates `Data/chunks.json`, and `bge_m3.py` builds the `news-bge-m3` collection under `newsDB_bge_m3/`.

## Run the question-answering app

From the project root, run:

```bash
python App.py
```

Enter a question when prompted. The app embeds the question with BGE-M3, retrieves up to seven nearby passages from the Chroma collection, and sends the passages and question to Qwen 3 8B. It prints the answer and the retrieved source passages. Run it from the project root so the module imports resolve as expected.

The app expects a database at `newsDB_bge_m3` with a collection named `news-bge-m3`. Build the index first by following the steps above.

## Refresh the news data and search index

The pipeline scripts are run from the project root, in this order:

```bash
python Crawler_Scraper/mainCrawler.py
python Rag/RAGprocessing.py
python bge_m3.py
```

- The crawler reads site URLs from `Crawler_Scraper/domainsToScan.csv` and writes crawl state and article records to `Data/`.
- The RAG processor reads `Data/output.json` and writes article passages to `Data/chunks.json`.
- The BGE-M3 indexer embeds those passages and stores them in `newsDB_bge_m3`.

**Rebuilding the index replaces the existing `news-bge-m3` Chroma collection.** Run `bge_m3.py` only when you intend to refresh that collection.

## Project layout

```text
LLMnews/
├── App.py                       # Interactive question-answering entry point
├── model.py                     # Prompt construction and Ollama calls
├── retrieval.py                 # BGE-M3 query embeddings and Chroma retrieval
├── bge_m3.py                    # Build or replace the BGE-M3 Chroma index
├── Crawler_Scraper/
│   ├── crawler.py               # Discover and filter article links
│   ├── scraper.py               # Extract article text and save crawl data
│   ├── mainCrawler.py           # Run the configured crawl
│   └── domainsToScan.csv        # News section URLs
├── Rag/
│   └── RAGprocessing.py         # Convert scraped articles into passages
├── Data/
│   ├── known_data.json          # Crawl tracking data
│   ├── output.json              # Scraped article records
│   └── chunks.json              # Passages used for semantic search
└── newsDB_bge_m3/               # Generated ChromaDB index (not committed)
```

## Notes

- The scripts resolve data and database paths relative to their files, so the crawl and indexing pipeline can be launched from the project root without manually changing directories.
- The crawler depends on the page structure of the configured news sites; site changes may require updates to its parsing rules.
- LLM responses can still contain unsupported claims. Check the retrieved passages printed by the app when evaluating an answer.
- `used.txt` lists the project's Python packages and local model runtime requirements.
