from typing import Optional, List
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    sources: List[str] = Field(..., description="List of file paths, directories, or URLs to ingest")
    chunk_size: Optional[int] = Field(None, description="Override default chunk size")
    chunk_overlap: Optional[int] = Field(None, description="Override default chunk overlap")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    status: str = Field("success", description="Status of the operation")
    chunks_ingested: int = Field(..., description="Total number of document chunks ingested and stored")
    sources: List[str] = Field(..., description="The sources that were ingested")


class SourceMeta(BaseModel):
    """Metadata for a retrieved source document."""
    source: str = Field(..., description="Origin of the document (file path, URL)")
    page: Optional[int] = Field(None, description="Page number, if applicable")
    relevance_score: Optional[float] = Field(None, description="Similarity score from vector search")
    reranker_score: Optional[float] = Field(None, description="Cross-encoder relevance score")


class QueryRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., description="The question to ask the RAG system")
    top_k: Optional[int] = Field(None, description="Override default number of chunks to retrieve")
    use_hybrid: bool = Field(True, description="Whether to use hybrid (BM25 + Vector) retrieval")
    use_reranker: bool = Field(True, description="Whether to apply cross-encoder reranking")


class QueryResponse(BaseModel):
    """Response model for questions."""
    answer: str = Field(..., description="The generated answer from the LLM")
    sources: List[SourceMeta] = Field(default_factory=list, description="List of sources used to generate the answer")
    context_chunks: int = Field(0, description="Number of document chunks used as context")
