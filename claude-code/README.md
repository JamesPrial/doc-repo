# Claude Code Documentation Downloader

A Python script to download all Claude Code documentation pages as Markdown files locally.

## Features

- Downloads the documentation map automatically
- Extracts all documentation URLs from the map
- Downloads each page in Markdown format (using `.md` extension)
- Creates local directory structure matching the docs organization
- Skips already-downloaded files (resume capability)
- Rate limiting to be respectful to the server
- Progress logging and error tracking
- Generates a manifest file with download results

## Requirements

- Python 3.7+
- `requests` library

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python download_docs.py
```

The script will:
1. Create a `docs/` directory
2. Download the documentation map
3. Extract all documentation URLs
4. Download each page as a `.md` file
5. Save a `manifest.json` with download results

## Output Structure

```
docs/
├── claude_code_docs_map.md
├── overview.md
├── quickstart.md
├── common-workflows.md
├── sub-agents.md
├── output-styles.md
└── manifest.json
```

## Customization

You can change the output directory by modifying the script:

```python
downloader = ClaudeDocsDownloader(output_dir="my-custom-dir")
```

## Features

- **Resume Support**: Already downloaded files are skipped
- **Error Handling**: Failed downloads are logged in the manifest
- **Rate Limiting**: 0.5 second delay between requests
- **Progress Tracking**: Shows download progress for each file
