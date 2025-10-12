# Claude Code Documentation Repository

This repository automatically downloads and maintains the latest [Claude Code](https://claude.com/claude-code) documentation from Anthropic.

## What It Does

This project uses GitHub Actions to automatically fetch the latest Claude Code documentation from Anthropic's official documentation site on a daily schedule. The documentation is downloaded in Markdown format and stored in the `claude/docs/` directory.

## How It Works

1. **Automated Downloads**: A GitHub Actions workflow runs daily at 2 AM UTC (or can be triggered manually)
2. **Documentation Extraction**: The workflow fetches all documentation pages from the Claude Code docs sitemap
3. **Local Storage**: Documentation is saved as Markdown files in the `claude/docs/` directory
4. **Version Control**: Changes are automatically committed and pushed to the repository

## Directory Structure

```
claude/
├── docs/                  # Downloaded documentation files
├── download_docs.py       # Python script that fetches the documentation
└── sitemap_cache.xml      # Cached sitemap from docs.claude.com
```

## Usage

The documentation updates automatically through GitHub Actions. To manually trigger an update:

1. Go to the "Actions" tab in this repository
2. Select "Update Claude Documentation"
3. Click "Run workflow"

## Credits

All documentation content is © Anthropic and is sourced from the official [Claude Code documentation](https://docs.claude.com/en/docs/claude-code). This repository simply mirrors the documentation for offline access and reference.

Claude Code is developed by [Anthropic](https://www.anthropic.com/).

## Requirements

- Python 3.11+
- `requests` library (for running the downloader script manually)

## License

The documentation downloader script is provided as-is. All Claude Code documentation content remains the intellectual property of Anthropic.
