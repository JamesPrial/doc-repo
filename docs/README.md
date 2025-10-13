# Documentation Repository

> Personal collection of documentation formatted in Markdown for easy reference and offline access.

## What's Available

This repository contains curated documentation sets for:

### Claude Code Documentation
Over **110 markdown files** covering Claude Code features, tools, and best practices:
- Getting Started guides
- Tool usage (Bash, Web Search, Code Execution, etc.)
- Agent implementation
- Model Context Protocol (MCP)
- Build and test guides

### Reddit API Documentation
Complete reference for Reddit's API endpoints and functionality, automatically updated daily.

---

## Download Options

<div class="download-section">

### Option 1: Clone the Repository
```bash
git clone https://github.com/jamesprial/doc-repo.git
cd doc-repo
```

### Option 2: Download as ZIP
<a href="https://github.com/jamesprial/doc-repo/archive/refs/heads/main.zip" class="download-btn">
  📦 Download Entire Repository (ZIP)
</a>

### Option 3: Individual Documentation Sets

<div class="doc-downloads">

#### Claude Code Documentation
- Browse in sidebar → or [View on GitHub](https://github.com/jamesprial/doc-repo/tree/main/claude/docs)
- Download: [Claude Docs ZIP](https://github.com/jamesprial/doc-repo/archive/refs/heads/main.zip) (extract `claude/docs/`)

#### Reddit API Documentation
- [View reddit-api.md](../reddit/reddit-api.md) | [Raw File](https://raw.githubusercontent.com/jamesprial/doc-repo/main/reddit/reddit-api.md)
- Right-click → Save As to download

</div>

</div>

---

## Automatic Updates

All documentation is kept up-to-date automatically:

- **Scheduled Updates**: GitHub Actions runs daily at 2:00 AM UTC
- **Auto-commit**: Changes are automatically pushed to the repository
- **Manual Trigger**: Can be triggered manually from the [Actions tab](https://github.com/jamesprial/doc-repo/actions)

---

## How to Use This Site

### Navigation
- Use the **sidebar** (left) to browse Claude Code documentation
- Use the **search bar** (top) to find specific topics
- Click the **GitHub icon** (top-right) to visit the repository

### Reading Offline
1. Clone or download the repository
2. All files are in standard Markdown format
3. Open with any text editor or Markdown viewer
4. Or serve locally: `docsify serve docs` (requires [Docsify CLI](https://docsify.js.org/#/quickstart))

---

## Repository Structure

```
doc-repo/
├── claude/
│   ├── docs/                  # Claude Code documentation (110+ files)
│   ├── download_docs.py       # Automated fetcher script
│   └── sitemap_cache.xml      # Cached sitemap
├── reddit/
│   ├── reddit-api.md          # Reddit API documentation
│   ├── html_converter.py      # HTML to Markdown converter
│   └── requirements.txt       # Python dependencies
└── docs/                      # GitHub Pages site (this site)
```

---

## Technical Details

**Languages**: Python 3.11+
**Format**: Markdown
**Automation**: GitHub Actions
**Site Generator**: [Docsify](https://docsify.js.org/)

### Requirements for Scripts
```bash
pip install -r requirements.txt
```

---

## Credits

- **Claude Code Documentation**: © [Anthropic](https://www.anthropic.com/) - [Official Docs](https://docs.claude.com/en/docs/claude-code)
- **Reddit API Documentation**: © Reddit - [Official API Docs](https://www.reddit.com/dev/api)

All documentation content remains the intellectual property of its respective owners. This repository mirrors documentation for offline access and reference only.

---

<div class="footer">
  <p>Last updated: Check the <a href="https://github.com/jamesprial/doc-repo/commits/main">commit history</a> for the latest updates.</p>
  <p>Found an issue? <a href="https://github.com/jamesprial/doc-repo/issues">Report it here</a></p>
</div>
