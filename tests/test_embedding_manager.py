"""
Unit tests for EmbeddingManager
"""
import unittest
import numpy as np
from src.rag_app.core.embedding_manager import EmbeddingManager


class TestEmbeddingManager(unittest.TestCase):
    """Test cases for EmbeddingManager"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.embedding_manager = EmbeddingManager()
    
    def test_initialization(self):
        """Test EmbeddingManager initialization"""
        self.assertIsNotNone(self.embedding_manager.model)
        self.assertGreater(self.embedding_manager.dimension, 0)
    
    def test_generate_single_embedding(self):
        """Test generating a single embedding"""
        text = "This is a test sentence."
        embedding = self.embedding_manager.generate_embedding(text)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding.shape), 1)
        self.assertEqual(embedding.shape[0], self.embedding_manager.dimension)
    
    def test_generate_multiple_embeddings(self):
        """Test generating multiple embeddings"""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = self.embedding_manager.generate_embeddings(texts)
        
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape[0], len(texts))
        self.assertEqual(embeddings.shape[1], self.embedding_manager.dimension)
    
    def test_empty_text(self):
        """Test handling of empty text"""
        embeddings = self.embedding_manager.generate_embeddings([])
        self.assertEqual(len(embeddings), 0)
    
    def test_get_dimension(self):
        """Test getting embedding dimension"""
        dimension = self.embedding_manager.get_dimension()
        self.assertIsInstance(dimension, int)
        self.assertGreater(dimension, 0)


if __name__ == "__main__":
    unittest.main()

# Made with Bob
