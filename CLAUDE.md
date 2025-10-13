# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal documentation repository that automatically mirrors and maintains offline copies of technical documentation from various sources. The repository uses GitHub Actions to fetch, convert, and update documentation daily, with GitHub Pages hosting a browsable version via Docsify.

## Architecture

### Two Documentation Pipelines

1. **Claude Code Documentation** (`claude/`)
   - Downloads markdown files directly from docs.claude.com's sitemap
   - Preserves original markdown format without conversion
   - Saves to `claude/docs/` with directory structure mirroring source URLs
   - Creates `manifest.json` tracking all downloaded files

2. **Reddit API Documentation** (`reddit/`)
   - Fetches HTML from reddit.com/dev/api
   - Converts HTML to Markdown using BeautifulSoup and html2text
   - Single output file: `reddit/reddit-api.md`
   - Custom HTML converter supports multiple output formats (JSON, text, markdown, structured)

### GitHub Pages Site (`docs/`)

- Powered by Docsify (client-side rendering, no build step)
- Uses symlinks to reference source directories:
  - `docs/claude` → `../claude`
  - `docs/reddit` → `../reddit`
- Configuration in `docs/index.html` and `docs/_sidebar.md`
- Custom styling in `docs/custom.css` (dark theme)

## Common Commands

### Running Documentation Downloaders

```bash
# Update Claude documentation
cd claude
python download_docs.py

# Update Reddit API documentation
cd reddit
curl https://www.reddit.com/dev/api -H "user-agent:u/ArtisticKey4324" > reddit-api.html
python html_converter.py reddit-api.html --format markdown -o reddit-api.md
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

### Claude Documentation Downloader (`claude/download_docs.py`)

- Fetches sitemap.xml from docs.claude.com
- Filters URLs containing `/en/docs/`
- Appends `.md` to URLs to get markdown versions
- Uses rate limiting (0.5s delay between requests)
- Skips already-downloaded files for efficiency
- Saves sitemap cache to `sitemap_cache.xml`

### HTML Converter (`reddit/html_converter.py`)

- Multi-format converter supporting JSON, text, markdown, and structured output
- Structured format extracts: headings, links, images, tables, lists, paragraphs
- Falls back to basic markdown conversion if html2text is unavailable
- CLI tool: `python html_converter.py input.html -f markdown -o output.md`

### GitHub Actions Workflows

Both workflows (`.github/workflows/`):
- Run daily at 2:00 AM UTC via cron
- Support manual triggering via `workflow_dispatch`
- Only commit if changes detected (`git diff --exit-code`)
- Use `github-actions[bot]` for commits
- Require `contents: write` permission

## Python Dependencies

- **Claude downloader**: `requests` only
- **Reddit converter**: `beautifulsoup4`, `html2text`, `lxml` (see `reddit/requirements.txt`)
- **Python version**: 3.11+ (3.x for Reddit workflow)

## Directory Structure Notes

- The `docs/` directory for GitHub Pages is separate from documentation source directories
- Symlinks in `docs/` allow Docsify to serve content from `claude/` and `reddit/` without duplication
- Git tracks the symlinks themselves, not their targets
- All actual documentation lives in `claude/docs/` (110+ files) and `reddit/reddit-api.md`