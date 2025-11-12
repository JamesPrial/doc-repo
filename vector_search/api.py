"""
FastAPI service for searching documentation using vector embeddings.
"""

import os
from typing import List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Pydantic models
class ContentType(str, Enum):
    """Content type filter options."""
    paragraph = "paragraph"
    code_block = "code_block"
    table = "table"
    list = "list"
    heading = "heading"


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query text", min_length=1)
    n_results: int = Field(5, description="Number of results to return", ge=1, le=20)
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    source: Optional[str] = Field(None, description="Filter by source file (partial match)")


class SearchResult(BaseModel):
    """Single search result."""
    content: str = Field(..., description="Chunk content")
    source_url: str = Field(..., description="Source documentation URL")
    source_file: str = Field(..., description="Source file path")
    section_path: str = Field(..., description="Document section hierarchy")
    content_type: str = Field(..., description="Type of content")
    keywords: List[str] = Field(..., description="Extracted keywords")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    token_count: int = Field(..., description="Token count of chunk")


class SearchResponse(BaseModel):
    """Search response model."""
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Number of results returned")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    collection_name: str
    document_count: int


# Initialize FastAPI app
app = FastAPI(
    title="Documentation Search API",
    description="Vector-based semantic search for technical documentation",
    version="1.0.0",
)

# Add CORS middleware for Docsify integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global state
class AppState:
    """Application state."""
    chroma_client: Optional[chromadb.ClientAPI] = None
    collection: Optional[chromadb.Collection] = None
    api_key: Optional[str] = None
    embedding_model: str = "models/text-embedding-004"


state = AppState()


@app.on_event("startup")
async def startup_event():
    """Initialize ChromaDB and Gemini API on startup."""
    # Get configuration from environment
    state.api_key = os.getenv("GOOGLE_API_KEY")
    if not state.api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in environment")

    chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection_name = os.getenv("COLLECTION_NAME", "documentation")

    # Configure Gemini API
    genai.configure(api_key=state.api_key)

    # Initialize ChromaDB
    state.chroma_client = chromadb.PersistentClient(
        path=chroma_db_path,
        settings=Settings(anonymized_telemetry=False),
    )

    # Get collection (must exist - run indexer first)
    try:
        state.collection = state.chroma_client.get_collection(name=collection_name)
        print(f"✓ Connected to ChromaDB collection: {collection_name}")
        print(f"✓ Document count: {state.collection.count()}")
    except Exception as e:
        print(f"✗ Error loading collection: {e}")
        print("  → Run index_documents.py first to create the collection")
        raise RuntimeError(f"Collection '{collection_name}' not found. Run indexer first.")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Documentation Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/search (POST)",
            "docs": "/docs",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if not state.collection:
        raise HTTPException(status_code=503, detail="Collection not initialized")

    return HealthResponse(
        status="healthy",
        collection_name=state.collection.name,
        document_count=state.collection.count(),
    )


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search documentation using vector similarity.

    Args:
        request: Search request with query and filters

    Returns:
        Search results with metadata and similarity scores
    """
    if not state.collection:
        raise HTTPException(status_code=503, detail="Collection not initialized")

    try:
        # Generate query embedding
        query_result = genai.embed_content(
            model=state.embedding_model,
            content=request.query,
            task_type="retrieval_query",
        )
        query_embedding = query_result['embedding']

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating query embedding: {str(e)}"
        )

    # Build metadata filter
    where_filter = {}
    if request.content_type:
        where_filter["content_type"] = request.content_type.value
    if request.source:
        # ChromaDB doesn't support partial matching directly
        # We'll filter in post-processing
        pass

    # Query ChromaDB
    try:
        results = state.collection.query(
            query_embeddings=[query_embedding],
            n_results=request.n_results,
            where=where_filter if where_filter else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying database: {str(e)}"
        )

    # Process results
    search_results = []

    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i]

            # Filter by source if specified (post-processing)
            if request.source and request.source.lower() not in metadata['source_file'].lower():
                continue

            # Convert distance to similarity score (1 - distance)
            similarity_score = max(0.0, 1.0 - distance)

            # Parse keywords
            keywords = metadata.get('keywords', '').split(',') if metadata.get('keywords') else []

            result = SearchResult(
                content=document,
                source_url=metadata['source_url'],
                source_file=metadata['source_file'],
                section_path=metadata['section_path'],
                content_type=metadata['content_type'],
                keywords=keywords,
                similarity_score=round(similarity_score, 4),
                token_count=metadata.get('token_count', 0),
            )
            search_results.append(result)

    return SearchResponse(
        query=request.query,
        results=search_results,
        total_results=len(search_results),
    )


@app.get("/stats", response_model=dict)
async def get_stats():
    """Get collection statistics."""
    if not state.collection:
        raise HTTPException(status_code=503, detail="Collection not initialized")

    # Get all documents to compute stats
    all_docs = state.collection.get(include=["metadatas"])

    # Compute statistics
    content_types = {}
    sources = {}

    for metadata in all_docs['metadatas']:
        # Count content types
        content_type = metadata.get('content_type', 'unknown')
        content_types[content_type] = content_types.get(content_type, 0) + 1

        # Count sources
        source_file = metadata.get('source_file', 'unknown')
        # Extract top-level directory (claude or reddit)
        if 'claude' in source_file:
            source = 'claude'
        elif 'reddit' in source_file:
            source = 'reddit'
        else:
            source = 'other'
        sources[source] = sources.get(source, 0) + 1

    return {
        "total_documents": state.collection.count(),
        "content_types": content_types,
        "sources": sources,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print(f"Starting Documentation Search API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
