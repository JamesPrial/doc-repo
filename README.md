# Documentation Repository

This is my personal collection of documentation formatted in Markdown for easy reference and offline access.

## What This Repository Contains

I maintain personal copies of various documentation sets, including:
- **Claude Code**: Official documentation from Anthropic's [Claude Code](https://claude.com/claude-code)
- **Reddit API**: Documentation for Reddit's API endpoints and functionality

All documentation is stored in Markdown format for easy reading, searching, and version control.

## How I Keep It Updated

I use **GitHub Actions** to automatically keep the documentation up to date:

1. **Scheduled Updates**: A GitHub Actions workflow runs daily at 2 AM UTC to check for new documentation
2. **Automatic Fetching**: The workflow downloads the latest documentation from official sources
3. **Format Conversion**: Content is converted to clean Markdown format
4. **Auto-commit**: Any changes are automatically committed and pushed to this repository
5. **Manual Triggers**: I can also manually trigger updates from the Actions tab when needed

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
