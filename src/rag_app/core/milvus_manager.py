"""
Milvus Manager for vector database operations
"""
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from typing import List, Dict, Tuple
import numpy as np
from .. import config


class MilvusManager:
    """Manages Milvus vector database operations"""
    
    def __init__(self, host: str = None, port: str = None, collection_name: str = None):
        """
        Initialize Milvus manager
        
        Args:
            host: Milvus server host
            port: Milvus server port
            collection_name: Name of the collection
        """
        self.host = host or config.MILVUS_HOST
        self.port = port or config.MILVUS_PORT
        self.collection_name = collection_name or config.COLLECTION_NAME
        self.collection = None
        self.dimension = config.EMBEDDING_DIMENSION
        
    def connect(self):
        """Connect to Milvus server"""
        print(f"Connecting to Milvus at {self.host}:{self.port}")
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )
        print("Connected to Milvus successfully")
    
    def create_collection(self, dimension: int = None):
        """
        Create a collection for storing document embeddings
        
        Args:
            dimension: Embedding dimension
        """
        if dimension:
            self.dimension = dimension
            
        # Check if collection already exists
        if utility.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' already exists")
            self.collection = Collection(self.collection_name)
            return
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="chunk_index", dtype=DataType.INT64)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="RAG document collection"
        )
        
        # Create collection
        print(f"Creating collection '{self.collection_name}' with dimension {self.dimension}")
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # Create index for vector field
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        
        print("Creating index...")
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        print("Collection created successfully")
    
    def load_collection(self):
        """Load collection into memory"""
        if self.collection is None:
            self.collection = Collection(self.collection_name)
        
        print(f"Loading collection '{self.collection_name}'...")
        self.collection.load()
        print("Collection loaded")
    
    def insert_documents(self, embeddings: np.ndarray, texts: List[str], 
                        sources: List[str], chunk_indices: List[int]):
        """
        Insert documents into the collection
        
        Args:
            embeddings: Document embeddings
            texts: Document texts
            sources: Source file paths
            chunk_indices: Chunk indices
        """
        if self.collection is None:
            self.load_collection()
        
        data = [
            embeddings.tolist(),
            texts,
            sources,
            chunk_indices
        ]
        
        print(f"Inserting {len(texts)} documents...")
        self.collection.insert(data)
        self.collection.flush()
        print("Documents inserted successfully")
    
    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of search results with text and metadata
        """
        if self.collection is None:
            self.load_collection()
        
        top_k = top_k or config.TOP_K
        
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        results = self.collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text", "source", "chunk_index"]
        )
        
        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "text": hit.entity.get("text"),
                    "source": hit.entity.get("source"),
                    "chunk_index": hit.entity.get("chunk_index"),
                    "distance": hit.distance,
                    "score": 1 / (1 + hit.distance)  # Convert distance to similarity score
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        if self.collection is None:
            self.load_collection()
        
        stats = {
            "name": self.collection_name,
            "num_entities": self.collection.num_entities,
            "dimension": self.dimension
        }
        return stats
    
    def drop_collection(self):
        """Drop the collection"""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' dropped")
        else:
            print(f"Collection '{self.collection_name}' does not exist")
    
    def disconnect(self):
        """Disconnect from Milvus"""
        connections.disconnect("default")
        print("Disconnected from Milvus")

# Made with Bob
