#!/usr/bin/env python3
"""
HTML Converter - Convert HTML files to machine-readable formats

Supported formats:
- JSON: Tree structure representation
- Text: Clean plain text extraction
- Markdown: Markdown conversion
- Structured: Extract specific elements (headings, links, tables, etc.)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from bs4 import BeautifulSoup
    from bs4.element import NavigableString, Tag
except ImportError:
    print("Error: beautifulsoup4 is required. Install it with: pip install beautifulsoup4")
    sys.exit(1)

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False


class HTMLConverter:
    """Convert HTML to various machine-readable formats"""

    def __init__(self, html_content: str):
        """Initialize converter with HTML content"""
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def to_json(self) -> Dict[str, Any]:
        """Convert HTML to JSON tree structure"""

        def parse_element(element) -> Optional[Dict[str, Any]]:
            """Recursively parse HTML element to dictionary"""
            if isinstance(element, NavigableString):
                text = str(element).strip()
                return {"type": "text", "content": text} if text else None

            if isinstance(element, Tag):
                node = {
                    "type": "element",
                    "tag": element.name,
                    "attributes": dict(element.attrs) if element.attrs else {},
                    "children": []
                }

                # Process children
                for child in element.children:
                    parsed = parse_element(child)
                    if parsed:
                        node["children"].append(parsed)

                return node

            return None

        return {
            "document": parse_element(self.soup.body if self.soup.body else self.soup),
            "metadata": {
                "title": self.soup.title.string if self.soup.title else None,
                "meta": self._extract_meta_tags()
            }
        }

    def to_text(self) -> str:
        """Extract clean plain text from HTML"""
        # Remove script and style elements
        for script in self.soup(["script", "style"]):
            script.decompose()

        # Get text
        text = self.soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def to_markdown(self) -> str:
        """Convert HTML to Markdown"""
        if not HAS_HTML2TEXT:
            # Fallback to basic conversion
            return self._basic_markdown_conversion()

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # Don't wrap lines

        return h.handle(str(self.soup))

    def _basic_markdown_conversion(self) -> str:
        """Basic Markdown conversion without html2text library"""
        result = []

        def process_element(element, level=0):
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    result.append(text)
                return

            if isinstance(element, Tag):
                # Handle different tags
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level_num = int(element.name[1])
                    result.append(f"\n{'#' * level_num} {element.get_text().strip()}\n")

                elif element.name == 'p':
                    result.append(f"\n{element.get_text().strip()}\n")

                elif element.name == 'a':
                    text = element.get_text().strip()
                    href = element.get('href', '')
                    result.append(f"[{text}]({href})")

                elif element.name == 'strong' or element.name == 'b':
                    result.append(f"**{element.get_text().strip()}**")

                elif element.name == 'em' or element.name == 'i':
                    result.append(f"*{element.get_text().strip()}*")

                elif element.name == 'code':
                    result.append(f"`{element.get_text().strip()}`")

                elif element.name == 'pre':
                    result.append(f"\n```\n{element.get_text().strip()}\n```\n")

                elif element.name == 'ul':
                    for li in element.find_all('li', recursive=False):
                        result.append(f"- {li.get_text().strip()}\n")

                elif element.name == 'ol':
                    for i, li in enumerate(element.find_all('li', recursive=False), 1):
                        result.append(f"{i}. {li.get_text().strip()}\n")

                elif element.name == 'br':
                    result.append("\n")

                elif element.name == 'hr':
                    result.append("\n---\n")

                else:
                    # Process children for other tags
                    for child in element.children:
                        process_element(child, level)

        process_element(self.soup.body if self.soup.body else self.soup)
        return ''.join(result)

    def to_structured(self) -> Dict[str, Any]:
        """Extract structured data from HTML"""
        return {
            "title": self.soup.title.string if self.soup.title else None,
            "metadata": self._extract_meta_tags(),
            "headings": self._extract_headings(),
            "links": self._extract_links(),
            "images": self._extract_images(),
            "tables": self._extract_tables(),
            "lists": self._extract_lists(),
            "paragraphs": self._extract_paragraphs()
        }

    def _extract_meta_tags(self) -> Dict[str, str]:
        """Extract meta tags"""
        meta = {}
        for tag in self.soup.find_all('meta'):
            name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
            content = tag.get('content')
            if name and content:
                meta[name] = content
        return meta

    def _extract_headings(self) -> List[Dict[str, Any]]:
        """Extract all headings"""
        headings = []
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                "level": int(tag.name[1]),
                "text": tag.get_text().strip(),
                "id": tag.get('id')
            })
        return headings

    def _extract_links(self) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        for a in self.soup.find_all('a', href=True):
            links.append({
                "text": a.get_text().strip(),
                "href": a['href'],
                "title": a.get('title')
            })
        return links

    def _extract_images(self) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        for img in self.soup.find_all('img'):
            images.append({
                "src": img.get('src'),
                "alt": img.get('alt'),
                "title": img.get('title')
            })
        return images

    def _extract_tables(self) -> List[Dict[str, Any]]:
        """Extract all tables"""
        tables = []
        for table in self.soup.find_all('table'):
            headers = []
            rows = []

            # Extract headers
            for th in table.find_all('th'):
                headers.append(th.get_text().strip())

            # Extract rows
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all('td')]
                if cells:
                    rows.append(cells)

            tables.append({
                "headers": headers,
                "rows": rows
            })
        return tables

    def _extract_lists(self) -> List[Dict[str, Any]]:
        """Extract all lists"""
        lists = []
        for ul in self.soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li', recursive=False)]
            lists.append({
                "type": "ordered" if ul.name == 'ol' else "unordered",
                "items": items
            })
        return lists

    def _extract_paragraphs(self) -> List[str]:
        """Extract all paragraphs"""
        return [p.get_text().strip() for p in self.soup.find_all('p')]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert HTML files to machine-readable formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.html --format json -o output.json
  %(prog)s input.html --format text -o output.txt
  %(prog)s input.html --format markdown -o output.md
  %(prog)s input.html --format structured -o output.json
  %(prog)s input.html --format json  # Output to stdout
        """
    )

    parser.add_argument('input', type=str, help='Input HTML file path')
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'text', 'markdown', 'structured'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    # Read input file
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)

        html_content = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert HTML
    try:
        converter = HTMLConverter(html_content)

        if args.format == 'json':
            output = json.dumps(
                converter.to_json(),
                indent=2 if args.pretty else None,
                ensure_ascii=False
            )
        elif args.format == 'text':
            output = converter.to_text()
        elif args.format == 'markdown':
            output = converter.to_markdown()
        elif args.format == 'structured':
            output = json.dumps(
                converter.to_structured(),
                indent=2 if args.pretty else None,
                ensure_ascii=False
            )
        else:
            print(f"Error: Unknown format '{args.format}'", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error converting HTML: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"Output written to: {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
