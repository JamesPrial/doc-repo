# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal documentation repository that automatically mirrors and maintains offline copies of technical documentation from various sources. The repository uses GitHub Actions to fetch, convert, and update documentation daily, with GitHub Pages hosting a browsable version via Docsify.

## Architecture

### Documentation Sources and Scripts

1. **Claude Code Documentation**
   - Downloader script: `scripts/claude/download_docs.py`
   - Downloads markdown files directly from docs.claude.com's sitemap
   - Preserves original markdown format without conversion
   - Saves to `docs/claude/` with directory structure mirroring source URLs
   - Creates `manifest.json` tracking all downloaded files
   - Cache stored in `scripts/claude/sitemap_cache.xml`

2. **Reddit API Documentation**
   - Converter script: `scripts/reddit/html_converter.py`
   - Fetches HTML from reddit.com/dev/api
   - Converts HTML to Markdown using BeautifulSoup and html2text
   - Output file: `docs/reddit/reddit-api.md`
   - Custom HTML converter supports multiple output formats (JSON, text, markdown, structured)
   - Reddit-specific filtering mode (`--reddit-mode`) removes navigation/header elements while preserving API endpoints TOC

### GitHub Pages Site (`docs/`)

- Powered by Docsify (client-side rendering, no build step)
- Contains all documentation content directly (no symlinks):
  - `docs/claude/` - Claude Code documentation (110+ files)
  - `docs/reddit/` - Reddit API documentation
- Configuration in `docs/index.html` and `docs/_sidebar.md`
- Custom styling in `docs/custom.css` (dark theme)

## Common Commands

### Running Documentation Downloaders

```bash
# Update Claude documentation
cd scripts/claude
python download_docs.py

# Update Reddit API documentation
cd scripts/reddit
curl https://www.reddit.com/dev/api -H "user-agent:u/ArtisticKey4324" > reddit-api.html
python html_converter.py reddit-api.html --format markdown --reddit-mode -o ../../docs/reddit/reddit-api.md
rm reddit-api.html
```

### Testing GitHub Pages Locally

```bash
# Install Docsify CLI if needed
npm install -g docsify-cli

# Serve the docs/ directory
docsify serve docs

# Access at http://localhost:3000
```

### Manual Workflow Triggers

ALWAYS PROACTIVELY use @agent-github-cli instead of gh cli commands yourself

## Key Implementation Details

### Claude Documentation Downloader (`scripts/claude/download_docs.py`)

- Fetches sitemap.xml from docs.claude.com
- Filters URLs containing `/en/docs/`
- Appends `.md` to URLs to get markdown versions
- Uses rate limiting (0.5s delay between requests)
- Skips already-downloaded files for efficiency
- Saves documentation to `docs/claude/`
- Saves sitemap cache to `scripts/claude/sitemap_cache.xml`

### HTML Converter (`scripts/reddit/html_converter.py`)

- Multi-format converter supporting JSON, text, markdown, and structured output
- Structured format extracts: headings, links, images, tables, lists, paragraphs
- Falls back to basic markdown conversion if html2text is unavailable
- Reddit-specific filtering mode (`--reddit-mode`):
  - Removes site header, navigation elements, login/signup prompts
  - Filters elements with `role="navigation"` or `role="banner"`
  - Preserves API endpoints table of contents
  - Reduces unwanted header content by ~70 lines
- CLI tool: `python html_converter.py input.html -f markdown -o output.md`
- With Reddit filtering: `python html_converter.py input.html -f markdown --reddit-mode -o output.md`

### GitHub Actions Workflows

Both workflows (`.github/workflows/`):
- Run daily at 2:00 AM UTC via cron
- Support manual triggering via `workflow_dispatch`
- Only commit if changes detected (`git diff --exit-code`)
- Use `github-actions[bot]` for commits
- Require `contents: write` permission

## Python Dependencies

- **Claude downloader**: `requests` only
- **Reddit converter**: `beautifulsoup4`, `html2text`, `lxml` (see `scripts/reddit/requirements.txt`)
- **Python version**: 3.11+ (3.x for Reddit workflow)

## Vector Search System (`vector_search/`)

A semantic search system for querying documentation using embeddings:

- **Stack**: Google Gemini embeddings (`text-embedding-004`) + ChromaDB (local vector store)
- **API**: FastAPI service with CORS support for Docsify integration
- **Chunking**: Header-aware markdown chunking (1024 tokens, 15% overlap) via LangChain

### Setup and Usage

```bash
# Install dependencies
cd vector_search
pip install -r requirements.txt

# Configure API key (get from https://aistudio.google.com/apikey)
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Index all documentation (first run: ~10-15 min)
python index_documents.py

# Reset and reindex everything
python index_documents.py --reset

# Test search after indexing
python index_documents.py --test-search "your query"

# Start the API server
python api.py
# or: uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# API available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### Key Implementation Details

**Document Processor** (`document_processor.py`):
- Uses `MarkdownHeaderTextSplitter` to preserve document hierarchy
- Falls back to `RecursiveCharacterTextSplitter` for oversized chunks
- Detects content types: paragraph, code_block, table, list, heading
- Extracts keywords from headers and inline code
- Converts file paths to source URLs (Claude docs, Reddit API)
- Generates MD5 chunk IDs for deduplication

**Indexer** (`index_documents.py`):
- Processes `docs/claude/` (110+ files) and `docs/reddit/reddit-api.md`
- Generates embeddings via Gemini API (rate limited: 0.5s between requests)
- Batches processing (100 chunks per batch)
- Stores in ChromaDB with rich metadata (hierarchy, content type, keywords, URLs)
- Free tier: 1,500 requests/day (sufficient for initial indexing)

**Search API** (`api.py`):
- POST `/search`: Query with filters (content_type, source, n_results)
- GET `/health`: Collection status and document count
- GET `/stats`: Content type and source distribution
- Returns similarity scores, source URLs, section paths, keywords

### Dependencies

- `chromadb>=0.5.6`: Local vector database
- `google-generativeai>=0.8.0`: Gemini embeddings
- `langchain-text-splitters>=0.3.0`: Smart markdown chunking
- `tiktoken>=0.7.0`: Token counting
- `fastapi>=0.115.0`, `uvicorn[standard]>=0.32.0`: REST API
- `python-dotenv>=1.0.0`: Environment config

## Directory Structure

```
/docs/                          # GitHub Pages site with ALL documentation
├── claude/                     # Claude Code documentation (110+ files)
│   ├── manifest.json
│   └── [markdown files]
├── reddit/                     # Reddit API documentation
│   └── reddit-api.md
├── index.html                  # Docsify configuration
├── custom.css                  # Custom styling
├── _sidebar.md                 # Sidebar navigation
└── _navbar.md                  # Top navigation

/scripts/                       # All scripts and tools (separated from docs)
├── claude/
│   ├── download_docs.py        # Claude documentation downloader
│   └── sitemap_cache.xml       # Sitemap cache
└── reddit/
    ├── html_converter.py       # HTML to Markdown converter
    └── requirements.txt        # Python dependencies

/vector_search/                 # Vector search service (independent)
├── api.py                      # FastAPI server
├── document_processor.py       # Document processing
├── index_documents.py          # Indexing script
├── chroma_db/                  # Vector database (gitignored)
└── [other files]
```

### Key Points

- **Clean separation**: `/docs/` contains ONLY documentation content, `/scripts/` contains ONLY tools
- **No symlinks**: All documentation files are stored directly in their final locations
- **Scripts organized by source**: Each documentation source has its own script directory
- **Vector search remains independent**: `vector_search/` is a standalone service
- Git tracks all directories and files (except gitignored items like `chroma_db/`)