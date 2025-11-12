# Adding New Documentation Sources

Quick guide to add new documentation sources to this repository.

## Quick Overview

The system has 3 main parts:
1. **Downloader Script** - Fetches documentation
2. **GitHub Actions Workflow** - Automates daily updates
3. **Vector Search Integration** - Makes docs searchable

---

## Step-by-Step Guide

### Step 1: Create Script Directory

```bash
mkdir -p scripts/your-docs
cd scripts/your-docs
```

### Step 2: Create Downloader Script

Example for downloading markdown files:

```python
# scripts/your-docs/download_docs.py
import requests
from pathlib import Path
import time

def download_docs():
    """Download documentation from source."""
    BASE_URL = "https://docs.example.com"
    OUTPUT_DIR = Path("../../docs/your-docs")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get your list of doc URLs (from sitemap, API, etc.)
    doc_urls = [
        f"{BASE_URL}/getting-started.md",
        f"{BASE_URL}/api-reference.md",
        # ... more URLs
    ]

    for url in doc_urls:
        response = requests.get(url)
        if response.status_code == 200:
            # Save file
            filename = url.split("/")[-1]
            (OUTPUT_DIR / filename).write_text(response.text)
            print(f"Downloaded: {filename}")

        time.sleep(0.5)  # Rate limiting

if __name__ == "__main__":
    download_docs()
```

### Step 3: Create requirements.txt

```bash
# scripts/your-docs/requirements.txt
requests>=2.31.0
```

### Step 4: Create GitHub Actions Workflow

Create `.github/workflows/update-your-docs.yml`:

```yaml
name: Update Your Docs

on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-docs:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        working-directory: scripts/your-docs
        run: pip install -r requirements.txt

      - name: Download documentation
        working-directory: scripts/your-docs
        run: python download_docs.py

      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet docs/your-docs/; then
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "changed=true" >> $GITHUB_OUTPUT
          fi

      - name: Commit changes
        if: steps.changes.outputs.changed == 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/your-docs/ scripts/your-docs/
          git commit -m "docs: update Your Docs documentation"
          git push
```

### Step 5: Integrate with Vector Search

#### A. Add URL mapping

Edit `vector_search/document_processor.py`, find the `file_to_url` method (around line 158):

```python
def file_to_url(self, file_path: str) -> str:
    """Convert file path to documentation URL."""
    file_path = str(file_path)

    # Claude documentation
    if "docs/claude/" in file_path:
        match = re.search(r'docs/claude/(.+)\.md$', file_path)
        if match:
            doc_path = match.group(1)
            return f"https://docs.claude.com/en/docs/{doc_path}"

    # Reddit documentation
    if "docs/reddit/reddit-api.md" in file_path:
        return "https://www.reddit.com/dev/api"

    # YOUR NEW DOCS - Add this block:
    if "docs/your-docs/" in file_path:
        match = re.search(r'docs/your-docs/(.+)\.md$', file_path)
        if match:
            doc_path = match.group(1)
            return f"https://docs.example.com/{doc_path}"

    return file_path
```

#### B. Add to indexing

Edit `vector_search/index_documents.py`, find the `main()` function (around line 273):

```python
def main():
    # ... existing code ...

    # Process Claude documentation
    claude_dir = repo_root / "docs" / "claude"
    claude_chunks = []
    if claude_dir.exists():
        print("Processing Claude Documentation")
        claude_chunks = processor.process_directory(claude_dir)

    # Process Reddit documentation
    reddit_dir = repo_root / "docs" / "reddit"
    reddit_chunks = []
    if reddit_dir.exists():
        print("Processing Reddit API Documentation")
        reddit_chunks = processor.process_directory(reddit_dir, pattern="*.md")

    # YOUR NEW DOCS - Add this block:
    your_docs_dir = repo_root / "docs" / "your-docs"
    your_docs_chunks = []
    if your_docs_dir.exists():
        print("Processing Your Documentation")
        your_docs_chunks = processor.process_directory(your_docs_dir)

    # Combine all chunks
    all_chunks = claude_chunks + reddit_chunks + your_docs_chunks
```

### Step 6: Update Deployment Workflow

Edit `.github/workflows/deploy-vector-db.yml` to trigger on your new docs:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'docs/claude/**'
      - 'docs/reddit/*.md'
      - 'docs/your-docs/**'  # Add this line
      - 'vector_search/**'
```

And update the change detection step:

```yaml
- name: Detect documentation changes
  id: detect-changes
  run: |
    if git diff --name-only HEAD~1 HEAD | grep -qE '^(docs/claude/|docs/reddit/.*\.md|docs/your-docs/)'; then
      echo "docs_changed=true" >> $GITHUB_OUTPUT
    else
      echo "docs_changed=false" >> $GITHUB_OUTPUT
    fi
```

### Step 7: Add to GitHub Pages (Optional)

If you want docs browsable on GitHub Pages, edit `docs/_sidebar.md`:

```markdown
- Claude Documentation
  - [Overview](/claude/README.md)

- Reddit API
  - [API Reference](/reddit/reddit-api.md)

- Your Docs
  - [Getting Started](/your-docs/getting-started.md)
```

Note: Documentation files are already in `docs/your-docs/` from the downloader script, no symlinking needed.

---

## Testing Your Setup

### 1. Test the downloader locally

```bash
cd scripts/your-docs
pip install -r requirements.txt
python download_docs.py

# Verify files downloaded
ls -lah ../../docs/your-docs/
```

### 2. Test vector search indexing

```bash
cd vector_search

# Make sure .env has GOOGLE_API_KEY
echo "GOOGLE_API_KEY=your_key_here" > .env

# Re-index with new docs
python index_documents.py --reset

# Test search
python index_documents.py --test-search "something from your new docs"
```

### 3. Test GitHub Actions workflow

```bash
# Trigger manually
gh workflow run update-your-docs.yml

# Or via GitHub UI: Actions → Update Your Docs → Run workflow
```

---

## Real Example: Adding Python Documentation

Here's a complete working example:

### 1. Create the downloader

```python
# scripts/python-docs/download_docs.py
import requests
from pathlib import Path

def download_python_docs():
    OUTPUT_DIR = Path("../../docs/python-docs")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Python tutorial pages
    base = "https://docs.python.org/3/tutorial"
    pages = ["introduction.html", "interpreter.html", "controlflow.html"]

    for page in pages:
        url = f"{base}/{page}"
        response = requests.get(url)

        if response.status_code == 200:
            # Save as .html or convert to .md
            (OUTPUT_DIR / page).write_text(response.text)
            print(f"Downloaded: {page}")

if __name__ == "__main__":
    download_python_docs()
```

### 2. Update vector search

```python
# In document_processor.py, file_to_url method:
if "docs/python-docs/" in file_path:
    match = re.search(r'docs/python-docs/(.+)\.html$', file_path)
    if match:
        doc_path = match.group(1)
        return f"https://docs.python.org/3/tutorial/{doc_path}.html"

# In index_documents.py, main function:
python_docs_dir = repo_root / "docs" / "python-docs"
python_docs_chunks = []
if python_docs_dir.exists():
    print("Processing Python Documentation")
    python_docs_chunks = processor.process_directory(python_docs_dir, pattern="*.html")

all_chunks = claude_chunks + reddit_chunks + python_docs_chunks
```

Done!

---

## Checklist

When adding new docs, make sure you:

- [ ] Created `scripts/your-docs/` directory
- [ ] Created `scripts/your-docs/download_docs.py`
- [ ] Created `scripts/your-docs/requirements.txt`
- [ ] Created `.github/workflows/update-your-docs.yml`
- [ ] Updated `vector_search/document_processor.py` (file_to_url method)
- [ ] Updated `vector_search/index_documents.py` (main function)
- [ ] Updated `.github/workflows/deploy-vector-db.yml` (paths trigger)
- [ ] Tested downloader locally
- [ ] Tested vector search indexing
- [ ] Updated `CLAUDE.md` to document new source

---

## Common Patterns

### HTML to Markdown Conversion

```python
# scripts/your-docs/download_docs.py
import requests
import html2text
from pathlib import Path

def download_and_convert():
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0

    response = requests.get("https://docs.example.com")
    markdown = h.handle(response.text)

    Path("../../docs/your-docs/index.md").write_text(markdown)
```

### API-Based Documentation

```python
def fetch_from_api():
    response = requests.get(
        "https://api.example.com/docs",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    docs = response.json()

    output_dir = Path("../../docs/your-docs")
    output_dir.mkdir(parents=True, exist_ok=True)

    for doc in docs:
        filename = f"{doc['slug']}.md"
        (output_dir / filename).write_text(doc['content'])
```

### Git Clone Approach

```yaml
# In GitHub Actions workflow
- name: Clone documentation
  run: |
    git clone --depth 1 https://github.com/org/docs.git temp
    mkdir -p docs/your-docs
    cp -r temp/content/* docs/your-docs/
    rm -rf temp
```

---

## Troubleshooting

**Docs not being indexed?**
- Check file paths in `index_documents.py` match your directory structure
- Verify glob pattern (`*.md` vs `**/*.md` vs `*.html`)
- Run indexing with `--reset` flag

**URLs wrong in search results?**
- Check `file_to_url` method in `document_processor.py`
- Make sure path matching logic is correct
- Test with `python index_documents.py --test-search "your query"`

**Workflow not triggering?**
- Verify workflow file is in `.github/workflows/`
- Check YAML syntax is valid
- Try manual trigger first: `gh workflow run update-your-docs.yml`

---

## Need Help?

Check existing implementations:
- **Claude Docs**: `scripts/claude/download_docs.py` - Markdown from sitemap
- **Reddit API**: `scripts/reddit/html_converter.py` - HTML to Markdown
