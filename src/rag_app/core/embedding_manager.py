"""
Embedding Manager for generating embeddings using sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from .. import config


class EmbeddingManager:
    """Manages embedding generation for documents and queries"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding manager
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension

# Made with Bob
