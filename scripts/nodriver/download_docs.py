#!/usr/bin/env python3
"""
nodriver Documentation Downloader

Downloads nodriver documentation from RST source files and converts to Markdown.
Follows the same pattern as the Claude documentation downloader.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: requests is required. Install it with: pip install requests")
    sys.exit(1)

try:
    from docutils.core import publish_string
    from docutils.writers import html5_polyglot
except ImportError:
    print("Error: docutils is required. Install it with: pip install docutils")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 is required. Install it with: pip install beautifulsoup4")
    sys.exit(1)

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False
    print("Warning: html2text not found. Using basic HTML to Markdown conversion.")


class NodriverDocsDownloader:
    """Download and convert nodriver documentation from RST sources"""

    BASE_URL = "https://ultrafunkamsterdam.github.io/nodriver/"
    SEARCHINDEX_URL = BASE_URL + "searchindex.js"
    SOURCES_URL = BASE_URL + "_sources/"

    def __init__(self, output_dir: str, force: bool = False, delay: float = 0.5):
        """Initialize downloader

        Args:
            output_dir: Directory to save converted markdown files
            force: Force re-download even if files exist
            delay: Delay between requests in seconds (default: 0.5)
        """
        self.output_dir = Path(output_dir)
        self.force = force
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; DocBot/1.0; +https://github.com/JamesPrial/doc-repo)'
        })

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load existing manifest if it exists
        self.manifest_path = self.output_dir / 'manifest.json'
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load existing manifest file"""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load manifest: {e}")
        return {"files": []}

    def _save_manifest(self):
        """Save manifest file"""
        try:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.manifest, indent=2, fp=f, ensure_ascii=False)
            print(f"Manifest saved: {self.manifest_path}")
        except Exception as e:
            print(f"Error saving manifest: {e}")

    def _get_rst_files(self) -> List[str]:
        """Extract list of RST files from searchindex.js

        Returns:
            List of RST file paths (e.g., ['index', 'readme', 'nodriver/quickstart'])
        """
        print(f"Fetching searchindex.js from {self.SEARCHINDEX_URL}...")

        try:
            response = self.session.get(self.SEARCHINDEX_URL, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching searchindex.js: {e}")
            sys.exit(1)

        # Extract docnames array from JavaScript
        # Pattern: "docnames": ["index","readme",...] or docnames:["index","readme",...]
        content = response.text
        match = re.search(r'"?docnames"?\s*:\s*\[(.*?)\]', content)

        if not match:
            print("Error: Could not find docnames in searchindex.js")
            sys.exit(1)

        # Parse the docnames array
        docnames_str = match.group(1)
        # Extract quoted strings
        docnames = re.findall(r'"([^"]+)"', docnames_str)

        print(f"Found {len(docnames)} documentation files")
        return docnames

    def _rst_to_markdown(self, rst_content: str) -> str:
        """Convert RST content to Markdown

        Args:
            rst_content: RST formatted content

        Returns:
            Markdown formatted content
        """
        try:
            # Convert RST to HTML first using docutils
            html_content = publish_string(
                rst_content,
                writer=html5_polyglot.Writer(),
                settings_overrides={
                    'initial_header_level': 1,
                    'report_level': 5,  # Suppress warnings
                    'halt_level': 5,    # Don't halt on errors
                }
            ).decode('utf-8')

            # Convert HTML to Markdown
            if HAS_HTML2TEXT:
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                h.ignore_emphasis = False
                h.body_width = 0  # Don't wrap lines
                h.unicode_snob = True
                h.skip_internal_links = False
                markdown = h.handle(html_content)
            else:
                # Basic HTML to Markdown conversion using BeautifulSoup
                markdown = self._basic_html_to_markdown(html_content)

            return markdown

        except Exception as e:
            print(f"Error converting RST to Markdown: {e}")
            # Return original RST content as fallback
            return f"```rst\n{rst_content}\n```\n\n*Note: Automatic conversion failed. Original RST content shown above.*"

    def _basic_html_to_markdown(self, html_content: str) -> str:
        """Basic HTML to Markdown conversion without html2text"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()

        # Get text with some formatting preserved
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)

        return text

    def _download_rst_file(self, docname: str) -> bool:
        """Download and convert a single RST file

        Args:
            docname: Document name (e.g., 'index', 'nodriver/quickstart')

        Returns:
            True if successful, False otherwise
        """
        # Construct URLs and paths
        rst_url = urljoin(self.SOURCES_URL, f"{docname}.rst.txt")
        output_path = self.output_dir / f"{docname}.md"

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Skip if file exists and not forcing
        if output_path.exists() and not self.force:
            print(f"Skipping {docname}.md (already exists)")
            return True

        print(f"Downloading {docname}.rst.txt...")

        try:
            # Download RST file
            response = self.session.get(rst_url, timeout=30)
            response.raise_for_status()
            rst_content = response.text

            # Convert to Markdown
            print(f"Converting {docname}.rst to Markdown...")
            markdown_content = self._rst_to_markdown(rst_content)

            # Save to file
            output_path.write_text(markdown_content, encoding='utf-8')
            print(f"Saved: {output_path}")

            # Update manifest
            file_info = {
                "source_path": docname,
                "output_path": str(output_path.relative_to(self.output_dir.parent)),
                "source_url": rst_url,
                "format": "markdown"
            }

            # Update or add to manifest
            existing = [f for f in self.manifest["files"] if f["source_path"] == docname]
            if existing:
                idx = self.manifest["files"].index(existing[0])
                self.manifest["files"][idx] = file_info
            else:
                self.manifest["files"].append(file_info)

            return True

        except requests.RequestException as e:
            print(f"Error downloading {rst_url}: {e}")
            return False
        except Exception as e:
            print(f"Error processing {docname}: {e}")
            return False

    def download_all(self):
        """Download and convert all documentation files"""
        print("Starting nodriver documentation download...\n")

        # Get list of RST files
        rst_files = self._get_rst_files()

        # Download each file
        success_count = 0
        failed_count = 0

        for i, docname in enumerate(rst_files, 1):
            print(f"\n[{i}/{len(rst_files)}] Processing {docname}...")

            if self._download_rst_file(docname):
                success_count += 1
            else:
                failed_count += 1

            # Rate limiting
            if i < len(rst_files):
                time.sleep(self.delay)

        # Save manifest
        self._save_manifest()

        # Print summary
        print("\n" + "="*50)
        print(f"Download complete!")
        print(f"Successfully downloaded: {success_count} files")
        print(f"Failed: {failed_count} files")
        print(f"Output directory: {self.output_dir}")
        print(f"Manifest: {self.manifest_path}")
        print("="*50)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Download nodriver documentation from RST sources and convert to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Download to docs/nodriver/
  %(prog)s --output-dir /path/to/output      # Custom output directory
  %(prog)s --force                           # Force re-download all files
  %(prog)s --delay 1.0                       # Slower rate limiting (1 second delay)
        """
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='../../docs/nodriver',
        help='Output directory for markdown files (default: ../../docs/nodriver)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force re-download even if files exist'
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )

    args = parser.parse_args()

    # Resolve output directory relative to script location
    script_dir = Path(__file__).parent
    output_dir = (script_dir / args.output_dir).resolve()

    # Create downloader and run
    downloader = NodriverDocsDownloader(
        output_dir=str(output_dir),
        force=args.force,
        delay=args.delay
    )

    try:
        downloader.download_all()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
