# Documentation Vector Search

Semantic search for your documentation using Google Gemini embeddings and ChromaDB.

## Overview

This system provides vector-based semantic search across Claude AI documentation and Reddit API documentation. It uses:

- **Google Gemini** (`text-embedding-004`) for embeddings (free tier: 1500 requests/day)
- **ChromaDB** for vector storage (local, no infrastructure needed)
- **LangChain** for intelligent markdown chunking
- **FastAPI** for REST API

## Features

- Semantic search across 110+ documentation files
- Header-aware chunking preserves document structure
- Filters by content type (code, paragraphs, tables, etc.)
- Source attribution with direct links to original docs
- Local storage, no cloud dependencies
- Free tier embeddings from Google

## Setup

### 1. Install Dependencies

```bash
cd vector_search
pip install -r requirements.txt
```

### 2. Get Google API Key

1. Visit https://aistudio.google.com/apikey
2. Create a new API key
3. Copy the key

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
CHROMA_DB_PATH=./chroma_db
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Index Documentation

Run the indexer to process and embed all documentation:

```bash
python index_documents.py
```

This will:
- Process 110+ Claude documentation files
- Process Reddit API documentation
- Generate embeddings using Gemini
- Store vectors in ChromaDB
- Takes ~10-15 minutes on first run

**Options:**

```bash
# Reset and reindex everything
python index_documents.py --reset

# Run a test search after indexing
python index_documents.py --test-search "how do I use embeddings"
```

### 5. Start the API Server

```bash
python api.py
```

Or with uvicorn directly:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000

## API Usage

### Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Endpoints

#### POST /search

Search documentation:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how do I use embeddings with Claude",
    "n_results": 5
  }'
```

**Request Body:**

```json
{
  "query": "your search query",
  "n_results": 5,
  "content_type": "code_block",  // optional: paragraph, code_block, table, list, heading
  "source": "claude"  // optional: filter by source file path
}
```

**Response:**

```json
{
  "query": "how do I use embeddings with Claude",
  "results": [
    {
      "content": "# Embeddings\n\nEmbeddings represent text as numerical vectors...",
      "source_url": "https://docs.claude.com/en/docs/build-with-claude/embeddings",
      "source_file": "/path/to/claude/docs/build-with-claude/embeddings.md",
      "section_path": "Build with Claude > Embeddings",
      "content_type": "paragraph",
      "keywords": ["embeddings", "vectors", "semantic"],
      "similarity_score": 0.8542,
      "token_count": 512
    }
  ],
  "total_results": 5
}
```

#### GET /health

Check API health:

```bash
curl "http://localhost:8000/health"
```

#### GET /stats

Get collection statistics:

```bash
curl "http://localhost:8000/stats"
```

Returns:

```json
{
  "total_documents": 850,
  "content_types": {
    "paragraph": 450,
    "code_block": 200,
    "list": 150,
    "table": 30,
    "heading": 20
  },
  "sources": {
    "claude": 800,
    "reddit": 50
  }
}
```

## Python Client Example

```python
import requests

# Search for documentation
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "how to use tool calling",
        "n_results": 3,
        "content_type": "paragraph"
    }
)

results = response.json()

for i, result in enumerate(results["results"]):
    print(f"\nResult {i + 1}:")
    print(f"Score: {result['similarity_score']}")
    print(f"Source: {result['source_url']}")
    print(f"Section: {result['section_path']}")
    print(f"Preview: {result['content'][:200]}...")
```

## JavaScript/Docsify Integration

Add to your Docsify site:

```javascript
// In docs/index.html or custom.js
async function searchDocs(query) {
  const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      n_results: 5
    })
  });

  const data = await response.json();
  return data.results;
}

// Example usage
searchDocs("embeddings API").then(results => {
  results.forEach(result => {
    console.log(result.source_url, result.similarity_score);
  });
});
```

## Architecture

### Document Processing Pipeline

1. **Markdown Chunking** (`document_processor.py`)
   - Splits by headers (H1, H2, H3)
   - Preserves code blocks, tables, lists
   - Target: 1024 tokens per chunk
   - 15% overlap between chunks
   - Extracts metadata (hierarchy, content type, keywords)

2. **Embedding Generation** (`index_documents.py`)
   - Uses Google Gemini `text-embedding-004`
   - Rate limiting (0.5s between requests)
   - Batch processing (100 chunks per batch)
   - Progress tracking

3. **Vector Storage** (ChromaDB)
   - Local persistent storage
   - Metadata filtering support
   - Fast similarity search
   - No server required

4. **Search API** (`api.py`)
   - FastAPI REST service
   - CORS enabled
   - Content type filtering
   - Source file filtering

### Chunking Strategy

The system uses a hybrid approach:

- **Primary:** Split by markdown headers (H2, H3)
- **Secondary:** If chunk > 1024 tokens, split on sentence boundaries
- **Never split:** Code blocks, tables, numbered lists
- **Overlap:** 15% character overlap to preserve context

### Metadata Stored

Each chunk includes:

```python
{
  "source_file": "/path/to/file.md",
  "source_url": "https://docs.claude.com/...",
  "h1": "Main Section",
  "h2": "Subsection",
  "h3": "Sub-subsection",
  "content_type": "paragraph",
  "token_count": 512,
  "section_path": "Main Section > Subsection",
  "keywords": "api,embeddings,vector"
}
```

## Cost Considerations

### Google Gemini Embeddings

- **Free Tier:** 1,500 requests per day
- **Paid Tier:** $0.15 per 1M input tokens
- **Initial indexing:** ~900 requests (under free tier)
- **Incremental updates:** Only new/changed docs
- **Search queries:** 1 request per search (well within free tier)

### Storage

- **ChromaDB:** Free, local storage
- **Disk usage:** ~50MB for 800-1000 chunks (embeddings + metadata)

## Updating Documentation

When documentation changes:

```bash
# 1. Update source docs (run your downloaders)
cd claude && python download_docs.py
cd ../reddit && ./update.sh

# 2. Reindex everything
cd ../vector_search
python index_documents.py --reset

# Or just add new docs (ChromaDB will skip existing IDs)
python index_documents.py
```

## Troubleshooting

### "Collection not found"

Run the indexer first:

```bash
python index_documents.py
```

### "GOOGLE_API_KEY not found"

1. Check `.env` file exists
2. Verify API key is set
3. Restart the API server

### Slow indexing

- **Normal:** First run takes 10-15 minutes for 110+ files
- **Free tier rate limits:** 0.5s delay between requests is intentional
- **Skip existing:** Re-running indexer skips already-indexed chunks

### Low quality results

Try:

1. **More specific queries:** "how to use embeddings API" vs "embeddings"
2. **Filter by content type:** Set `content_type: "code_block"` for code examples
3. **Increase results:** Set `n_results: 10` to see more matches

## Development

### Test the document processor

```bash
python document_processor.py
```

### Test the indexer

```bash
python index_documents.py --test-search "your query here"
```

### Run API in development mode

```bash
uvicorn api:app --reload
```

## File Structure

```
vector_search/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your config (git-ignored)
├── .gitignore           # Git ignore rules
├── document_processor.py # Markdown chunking
├── index_documents.py    # Indexing script
├── api.py               # FastAPI service
└── chroma_db/           # Vector database (git-ignored)
```

## Future Enhancements

Potential improvements:

1. **GitHub Actions:** Auto-reindex when docs update
2. **Caching:** Cache embeddings to avoid regeneration
3. **Better chunking:** Semantic chunking based on content similarity
4. **Hybrid search:** Combine vector search with keyword search
5. **Query expansion:** Automatically expand queries with synonyms
6. **Analytics:** Track popular queries and results
7. **Qdrant migration:** Scale to cloud if dataset grows significantly

## License

Same as parent repository.

## Support

For issues or questions, check:

- API docs: http://localhost:8000/docs
- ChromaDB docs: https://docs.trychroma.com/
- Gemini API docs: https://ai.google.dev/gemini-api/docs/embeddings
