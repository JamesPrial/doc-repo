#!/usr/bin/env python3
"""
Script to download all Claude Code documentation pages as Markdown files.

This script:
1. Downloads the docs map from claude_code_docs_map.md
2. Parses it to extract all documentation URLs
3. Downloads each page by appending .md to the URL
4. Saves files locally with the proper directory structure
"""

import os
import re
import time
import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install it with: pip install requests")
    exit(1)


class ClaudeDocsDownloader:
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.base_url = "https://docs.claude.com/en/docs/claude-code"
        self.docs_map_url = f"{self.base_url}/claude_code_docs_map.md"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Documentation Downloader)'
        })
        self.downloaded = []
        self.failed = []

    def download_docs_map(self) -> str:
        """Download the documentation map file."""
        print(f"Downloading docs map from {self.docs_map_url}...")
        try:
            response = self.session.get(self.docs_map_url, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully downloaded docs map ({len(response.text)} chars)")
            return response.text
        except requests.RequestException as e:
            print(f"✗ Failed to download docs map: {e}")
            raise

    def extract_urls_from_map(self, docs_map: str) -> List[str]:
        """Extract all documentation URLs from the docs map markdown."""
        print("\nExtracting URLs from docs map...")

        # Pattern to match markdown links: [text](url)
        url_pattern = r'\[([^\]]+)\]\((https://docs\.claude\.com/en/docs/claude-code/[^\)]+)\)'
        matches = re.findall(url_pattern, docs_map)

        urls = []
        for title, url in matches:
            # Convert URL to .md format if not already
            if not url.endswith('.md'):
                url = f"{url}.md"
            urls.append(url)

        # Also extract any standalone URLs
        standalone_pattern = r'https://docs\.claude\.com/en/docs/claude-code/[^\s\)\]"]+'
        standalone_urls = re.findall(standalone_pattern, docs_map)

        for url in standalone_urls:
            if not url.endswith('.md'):
                url = f"{url}.md"
            if url not in urls:
                urls.append(url)

        # Remove duplicates while preserving order
        urls = list(dict.fromkeys(urls))

        # Filter out SDK URLs and other obsolete pages
        original_count = len(urls)
        skip_patterns = ['/sdk/', 'ide-integrations.md']
        urls = [url for url in urls if not any(pattern in url for pattern in skip_patterns)]
        skipped_count = original_count - len(urls)

        if skipped_count > 0:
            print(f"  ⊙ Skipping {skipped_count} obsolete/moved URLs")

        print(f"✓ Found {len(urls)} unique documentation pages")
        return urls

    def get_local_path(self, url: str) -> Path:
        """Convert a URL to a local file path."""
        # Extract path after /claude-code/
        match = re.search(r'/claude-code/(.+)$', url)
        if match:
            relative_path = match.group(1)
            # Ensure it ends with .md
            if not relative_path.endswith('.md'):
                relative_path = f"{relative_path}.md"
            return self.output_dir / relative_path
        return self.output_dir / "unknown.md"

    def download_page(self, url: str) -> bool:
        """Download a single documentation page."""
        local_path = self.get_local_path(url)

        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Skip if already exists
        if local_path.exists():
            print(f"  ⊙ Skipping (already exists): {local_path.name}")
            self.downloaded.append(str(local_path))
            return True

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Save the content
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"  ✓ Downloaded: {local_path.name}")
            self.downloaded.append(str(local_path))
            return True

        except requests.RequestException as e:
            print(f"  ✗ Failed: {url} - {e}")
            self.failed.append({"url": url, "error": str(e)})
            return False

    def download_all(self):
        """Download all documentation pages."""
        print("\n" + "="*60)
        print("Claude Code Documentation Downloader")
        print("="*60 + "\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir.absolute()}\n")

        # Download and parse docs map
        docs_map = self.download_docs_map()
        urls = self.extract_urls_from_map(docs_map)

        # Save the docs map itself
        map_path = self.output_dir / "claude_code_docs_map.md"
        with open(map_path, 'w', encoding='utf-8') as f:
            f.write(docs_map)
        print(f"\n✓ Saved docs map to: {map_path}")

        # Download each page
        print(f"\nDownloading {len(urls)} documentation pages...")
        print("-" * 60)

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            self.download_page(url)

            # Be respectful with rate limiting
            if i < len(urls):
                time.sleep(0.5)

        # Create manifest
        self.save_manifest()

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✓ Successfully downloaded: {len(self.downloaded)} files")
        if self.failed:
            print(f"✗ Failed: {len(self.failed)} files")
            print("\nFailed URLs:")
            for item in self.failed:
                print(f"  - {item['url']}: {item['error']}")
        print(f"\nAll files saved to: {self.output_dir.absolute()}")
        print("="*60 + "\n")

    def save_manifest(self):
        """Save a manifest of all downloaded files."""
        manifest = {
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": len(self.downloaded),
            "failed_downloads": len(self.failed),
            "files": self.downloaded,
            "failed": self.failed
        }

        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✓ Saved manifest to: {manifest_path}")


def main():
    """Main entry point."""
    downloader = ClaudeDocsDownloader(output_dir="docs")
    downloader.download_all()


if __name__ == "__main__":
    main()
