"""
Index documentation into ChromaDB using Google Gemini embeddings.
"""

import os
import time
from pathlib import Path
from typing import List, Optional
import argparse

import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv

from document_processor import MarkdownDocumentProcessor, DocumentChunk


class DocumentIndexer:
    """Index documents into ChromaDB with Gemini embeddings."""

    def __init__(
        self,
        api_key: str,
        chroma_db_path: str = "./chroma_db",
        collection_name: str = "documentation",
        embedding_model: str = "models/text-embedding-004",
        batch_size: int = 100,
        rate_limit_delay: float = 0.5,
    ):
        """
        Initialize the document indexer.

        Args:
            api_key: Google API key for Gemini
            chroma_db_path: Path to ChromaDB storage
            collection_name: Name of the collection
            embedding_model: Gemini embedding model to use
            batch_size: Number of documents to embed per batch
            rate_limit_delay: Delay between API calls (seconds)
        """
        self.api_key = api_key
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Technical documentation search"},
        )

        print(f"✓ ChromaDB initialized at: {chroma_db_path}")
        print(f"✓ Collection: {collection_name}")
        print(f"✓ Existing documents: {self.collection.count()}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Gemini.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
            )
            return result['embedding']
        except Exception as e:
            print(f"  ✗ Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i, text in enumerate(texts):
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)

                # Rate limiting
                if i < len(texts) - 1:
                    time.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"  ✗ Error on text {i}: {e}")
                # Use zero vector as fallback
                embeddings.append([0.0] * 768)

        return embeddings

    def index_chunks(self, chunks: List[DocumentChunk], show_progress: bool = True):
        """
        Index document chunks into ChromaDB.

        Args:
            chunks: List of DocumentChunk objects
            show_progress: Whether to show progress updates
        """
        if not chunks:
            print("No chunks to index")
            return

        print(f"\nIndexing {len(chunks)} chunks...")

        # Process in batches
        for batch_start in range(0, len(chunks), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(chunks))
            batch = chunks[batch_start:batch_end]

            if show_progress:
                print(f"\nBatch {batch_start // self.batch_size + 1}: "
                      f"Processing chunks {batch_start + 1}-{batch_end}")

            # Prepare data for ChromaDB
            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.content for chunk in batch]
            metadatas = [
                {
                    "source_file": chunk.source_file,
                    "source_url": chunk.source_url,
                    "h1": chunk.hierarchy.get("h1", ""),
                    "h2": chunk.hierarchy.get("h2", ""),
                    "h3": chunk.hierarchy.get("h3", ""),
                    "content_type": chunk.content_type,
                    "token_count": chunk.token_count,
                    "section_path": chunk.section_path,
                    "keywords": ",".join(chunk.keywords),
                }
                for chunk in batch
            ]

            # Generate embeddings
            if show_progress:
                print(f"  → Generating embeddings...")

            embeddings = self.generate_embeddings_batch(documents)

            # Add to ChromaDB
            if show_progress:
                print(f"  → Adding to ChromaDB...")

            try:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                )
                if show_progress:
                    print(f"  ✓ Added {len(batch)} chunks")
            except Exception as e:
                print(f"  ✗ Error adding batch: {e}")
                continue

        print(f"\n✓ Indexing complete!")
        print(f"✓ Total documents in collection: {self.collection.count()}")

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Search the indexed documentation.

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            Search results from ChromaDB
        """
        # Generate query embedding
        query_embedding = genai.embed_content(
            model=self.embedding_model,
            content=query,
            task_type="retrieval_query",
        )['embedding']

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
        )

        return results

    def reset_collection(self):
        """Delete and recreate the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Technical documentation search"},
        )
        print(f"✓ Collection reset: {self.collection_name}")


def main():
    """Main indexing script."""
    parser = argparse.ArgumentParser(description="Index documentation into vector database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the collection before indexing",
    )
    parser.add_argument(
        "--test-search",
        type=str,
        help="Run a test search after indexing",
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        print("Get your API key from: https://aistudio.google.com/apikey")
        return

    chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # Initialize indexer
    print("Initializing Document Indexer...")
    indexer = DocumentIndexer(
        api_key=api_key,
        chroma_db_path=chroma_db_path,
    )

    # Reset collection if requested
    if args.reset:
        print("\nResetting collection...")
        indexer.reset_collection()

    # Initialize document processor
    print("\nInitializing Document Processor...")
    processor = MarkdownDocumentProcessor(target_chunk_size=1024)

    # Get repository root
    repo_root = Path(__file__).parent.parent

    # Process Claude documentation
    claude_dir = repo_root / "docs" / "claude"
    claude_chunks = []
    if claude_dir.exists():
        print(f"\n{'='*80}")
        print("Processing Claude Documentation")
        print(f"{'='*80}")
        claude_chunks = processor.process_directory(claude_dir)

    # Process Reddit documentation
    reddit_dir = repo_root / "docs" / "reddit"
    reddit_chunks = []
    if reddit_dir.exists():
        print(f"\n{'='*80}")
        print("Processing Reddit API Documentation")
        print(f"{'='*80}")
        reddit_chunks = processor.process_directory(reddit_dir, pattern="*.md")

    # Combine all chunks
    all_chunks = claude_chunks + reddit_chunks

    if not all_chunks:
        print("\nNo documents found to index!")
        return

    # Index all chunks
    print(f"\n{'='*80}")
    print("Indexing Documents")
    print(f"{'='*80}")
    indexer.index_chunks(all_chunks)

    # Test search if requested
    if args.test_search:
        print(f"\n{'='*80}")
        print(f"Test Search: '{args.test_search}'")
        print(f"{'='*80}")

        results = indexer.search(args.test_search, n_results=3)

        print(f"\nFound {len(results['ids'][0])} results:\n")
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0],
        )):
            print(f"Result {i + 1} (similarity: {1 - distance:.3f}):")
            print(f"  Source: {metadata['source_url']}")
            print(f"  Section: {metadata['section_path']}")
            print(f"  Type: {metadata['content_type']}")
            print(f"  Preview: {doc[:150]}...")
            print()


if __name__ == "__main__":
    main()
