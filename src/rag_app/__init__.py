"""
RAG Application Package
A complete Retrieval-Augmented Generation system using MilvusDB and Ollama
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.embedding_manager import EmbeddingManager
from .core.milvus_manager import MilvusManager
from .core.document_processor import DocumentProcessor
from .core.rag_pipeline import RAGPipeline

__all__ = [
    "EmbeddingManager",
    "MilvusManager",
    "DocumentProcessor",
    "RAGPipeline",
]

# Made with Bob
