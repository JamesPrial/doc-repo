"""
Document processing pipeline for chunking markdown documentation.
Implements hybrid header-based + token-limited chunking strategy.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import hashlib

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
import tiktoken


@dataclass
class DocumentChunk:
    """Represents a processed document chunk with metadata."""
    chunk_id: str
    content: str
    source_file: str
    source_url: str
    hierarchy: Dict[str, str]  # h1, h2, h3 headers
    content_type: str  # paragraph, code_block, table, list, heading
    token_count: int
    char_count: int
    keywords: List[str]
    section_path: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)


class MarkdownDocumentProcessor:
    """Process markdown documents into searchable chunks."""

    def __init__(
        self,
        target_chunk_size: int = 1024,  # tokens
        overlap_percentage: float = 0.15,  # 15% overlap
        encoding_name: str = "cl100k_base",  # OpenAI's tokenizer (good approximation)
    ):
        """
        Initialize the document processor.

        Args:
            target_chunk_size: Target size in tokens (default 1024)
            overlap_percentage: Percentage of overlap between chunks (default 0.15)
            encoding_name: Tiktoken encoding name for token counting
        """
        self.target_chunk_size = target_chunk_size
        self.overlap_percentage = overlap_percentage

        # Initialize tokenizer
        self.encoding = tiktoken.get_encoding(encoding_name)

        # Calculate character-based approximations
        # Rough estimate: 1 token ~= 4 characters for English text
        self.target_chunk_chars = target_chunk_size * 4
        self.overlap_chars = int(self.target_chunk_chars * overlap_percentage)

        # Headers to split on (preserve hierarchy)
        self.headers_to_split = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]

        # Initialize markdown header splitter
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split,
            strip_headers=False,  # Keep headers in content
        )

        # Initialize recursive character splitter for oversized chunks
        self.char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.target_chunk_chars,
            chunk_overlap=self.overlap_chars,
            length_function=len,
            separators=[
                "\n\n",  # Paragraphs
                "\n",    # Lines
                ". ",    # Sentences
                " ",     # Words
                "",      # Characters
            ],
        )

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))

    def generate_chunk_id(self, content: str, source_file: str) -> str:
        """Generate unique chunk ID from content and source."""
        hash_input = f"{source_file}:{content}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def detect_content_type(self, content: str) -> str:
        """
        Detect the primary content type of a chunk.

        Returns: paragraph, code_block, table, list, or heading
        """
        content_stripped = content.strip()

        # Check for code blocks
        if content_stripped.startswith("```") and content_stripped.endswith("```"):
            return "code_block"

        # Check for tables (markdown pipe syntax)
        if "|" in content and re.search(r'\|[\s\-:]+\|', content):
            return "table"

        # Check for lists
        if re.match(r'^[\s]*[-*+]\s', content, re.MULTILINE) or \
           re.match(r'^[\s]*\d+\.\s', content, re.MULTILINE):
            return "list"

        # Check for headings
        if content_stripped.startswith("#"):
            return "heading"

        return "paragraph"

    def extract_keywords(self, content: str, hierarchy: Dict[str, str]) -> List[str]:
        """
        Extract simple keywords from content and headers.
        Uses basic word extraction (can be enhanced with NLP).
        """
        keywords = set()

        # Add header text as keywords
        for header_text in hierarchy.values():
            if header_text:
                # Split on spaces and common punctuation
                words = re.findall(r'\b\w+\b', header_text.lower())
                keywords.update(word for word in words if len(word) > 3)

        # Extract code-related keywords
        code_keywords = re.findall(r'`([^`]+)`', content)
        keywords.update(kw.lower() for kw in code_keywords if len(kw) > 2)

        # Limit to top keywords
        return sorted(list(keywords))[:10]

    def build_section_path(self, hierarchy: Dict[str, str]) -> str:
        """Build hierarchical section path from headers."""
        path_parts = []
        for level in ["h1", "h2", "h3"]:
            if hierarchy.get(level):
                path_parts.append(hierarchy[level])
        return " > ".join(path_parts) if path_parts else "Root"

    def file_to_url(self, file_path: str) -> str:
        """
        Convert file path to documentation URL.
        Supports Claude and Reddit docs.
        """
        file_path = str(file_path)

        # Claude documentation
        if "claude/docs/" in file_path:
            # Extract path after claude/docs/
            match = re.search(r'claude/docs/(.+)\.md$', file_path)
            if match:
                doc_path = match.group(1)
                return f"https://docs.claude.com/en/docs/{doc_path}"

        # Reddit documentation
        if "reddit/reddit-api.md" in file_path:
            return "https://www.reddit.com/dev/api"

        # Fallback
        return file_path

    def process_document(self, file_path: Path) -> List[DocumentChunk]:
        """
        Process a markdown document into chunks.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of DocumentChunk objects
        """
        # Read file
        content = file_path.read_text(encoding='utf-8')

        # Split by headers first
        header_splits = self.header_splitter.split_text(content)

        chunks = []

        for split in header_splits:
            # Extract metadata from the split
            metadata = split.metadata if hasattr(split, 'metadata') else {}
            chunk_content = split.page_content if hasattr(split, 'page_content') else str(split)

            # Build hierarchy from metadata
            hierarchy = {
                "h1": metadata.get("h1", ""),
                "h2": metadata.get("h2", ""),
                "h3": metadata.get("h3", ""),
            }

            # Count tokens
            token_count = self.count_tokens(chunk_content)

            # If chunk exceeds target size, split further
            if token_count > self.target_chunk_size:
                # Use character splitter for oversized chunks
                sub_chunks = self.char_splitter.split_text(chunk_content)

                for i, sub_chunk in enumerate(sub_chunks):
                    chunk = self._create_chunk(
                        content=sub_chunk,
                        source_file=str(file_path),
                        hierarchy=hierarchy,
                        sequence=i,
                    )
                    chunks.append(chunk)
            else:
                # Use chunk as-is
                chunk = self._create_chunk(
                    content=chunk_content,
                    source_file=str(file_path),
                    hierarchy=hierarchy,
                )
                chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        content: str,
        source_file: str,
        hierarchy: Dict[str, str],
        sequence: int = 0,
    ) -> DocumentChunk:
        """Create a DocumentChunk with all metadata."""
        token_count = self.count_tokens(content)
        char_count = len(content)
        content_type = self.detect_content_type(content)
        keywords = self.extract_keywords(content, hierarchy)
        section_path = self.build_section_path(hierarchy)
        source_url = self.file_to_url(source_file)

        # Generate unique ID
        chunk_id = self.generate_chunk_id(content, source_file)
        if sequence > 0:
            chunk_id += f"_{sequence}"

        return DocumentChunk(
            chunk_id=chunk_id,
            content=content,
            source_file=source_file,
            source_url=source_url,
            hierarchy=hierarchy,
            content_type=content_type,
            token_count=token_count,
            char_count=char_count,
            keywords=keywords,
            section_path=section_path,
        )

    def process_directory(self, directory: Path, pattern: str = "**/*.md") -> List[DocumentChunk]:
        """
        Process all markdown files in a directory.

        Args:
            directory: Directory to process
            pattern: Glob pattern for files (default: **/*.md)

        Returns:
            List of all chunks from all files
        """
        all_chunks = []

        md_files = list(directory.glob(pattern))
        print(f"Found {len(md_files)} markdown files in {directory}")

        for file_path in md_files:
            try:
                print(f"Processing: {file_path.relative_to(directory)}")
                chunks = self.process_document(file_path)
                all_chunks.extend(chunks)
                print(f"  → Generated {len(chunks)} chunks")
            except Exception as e:
                print(f"  ✗ Error processing {file_path}: {e}")
                continue

        print(f"\nTotal chunks generated: {len(all_chunks)}")
        return all_chunks


if __name__ == "__main__":
    # Test the processor
    from pathlib import Path

    processor = MarkdownDocumentProcessor(target_chunk_size=1024)

    # Test on Claude docs
    claude_dir = Path(__file__).parent.parent / "claude" / "docs"
    if claude_dir.exists():
        chunks = processor.process_directory(claude_dir)

        # Show sample chunk
        if chunks:
            print("\n" + "="*80)
            print("SAMPLE CHUNK:")
            print("="*80)
            sample = chunks[0]
            print(f"ID: {sample.chunk_id}")
            print(f"Source: {sample.source_file}")
            print(f"URL: {sample.source_url}")
            print(f"Hierarchy: {sample.hierarchy}")
            print(f"Section: {sample.section_path}")
            print(f"Type: {sample.content_type}")
            print(f"Tokens: {sample.token_count}")
            print(f"Keywords: {sample.keywords}")
            print(f"\nContent preview:\n{sample.content[:200]}...")
