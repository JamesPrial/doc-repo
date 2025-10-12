#!/usr/bin/env python3
"""
Script to download all Claude documentation pages as Markdown files.

This script:
1. Downloads the sitemap.xml from docs.claude.com
2. Parses it to extract ALL documentation URLs under /en/docs/
3. Downloads each page by appending .md to the URL
4. Saves files locally with the proper directory structure
"""

import os
import re
import time
import json
import xml.etree.ElementTree as ET
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
        self.base_url = "https://docs.claude.com"
        self.sitemap_url = f"{self.base_url}/sitemap.xml"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Documentation Downloader)'
        })
        self.downloaded = []
        self.failed = []

    def download_sitemap(self) -> str:
        """Download the sitemap.xml file."""
        print(f"Downloading sitemap from {self.sitemap_url}...")
        try:
            response = self.session.get(self.sitemap_url, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully downloaded sitemap ({len(response.text)} chars)")
            return response.text
        except requests.RequestException as e:
            print(f"✗ Failed to download sitemap: {e}")
            raise

    def extract_urls_from_sitemap(self, sitemap_content: str) -> List[str]:
        """Extract all documentation URLs from the sitemap XML."""
        print("\nExtracting documentation URLs from sitemap...")

        try:
            # Parse XML
            root = ET.fromstring(sitemap_content)

            # Handle XML namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            urls = []
            for url_elem in root.findall('.//ns:url', namespace):
                loc = url_elem.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    url = loc.text.strip()

                    # Include ALL URLs under /en/docs/ (no filtering)
                    if '/en/docs/' in url:
                        # Convert to .md URL
                        if not url.endswith('.md'):
                            url = f"{url}.md"
                        urls.append(url)

            # Remove duplicates while preserving order
            urls = list(dict.fromkeys(urls))

            print(f"✓ Found {len(urls)} documentation pages")
            return urls

        except ET.ParseError as e:
            print(f"✗ Failed to parse sitemap XML: {e}")
            raise

    def get_local_path(self, url: str) -> Path:
        """Convert a URL to a local file path."""
        # Extract path after /en/docs/
        match = re.search(r'/en/docs/(.+)$', url)
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
        print("Claude Documentation Downloader")
        print("="*60 + "\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {self.output_dir.absolute()}\n")

        # Download and parse sitemap
        sitemap_content = self.download_sitemap()
        urls = self.extract_urls_from_sitemap(sitemap_content)

        # Save the sitemap itself
        sitemap_path = self.output_dir.parent / "sitemap_cache.xml"
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print(f"\n✓ Saved sitemap cache to: {sitemap_path}")

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
