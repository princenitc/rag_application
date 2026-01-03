"""
Example usage of the RAG application
Demonstrates how to use the components programmatically
"""
from src.rag_app.core.embedding_manager import EmbeddingManager
from src.rag_app.core.milvus_manager import MilvusManager
from src.rag_app.core.document_processor import DocumentProcessor
from src.rag_app.core.rag_pipeline import RAGPipeline


def example_basic_usage():
    """Basic example of using the RAG system"""
    print("="*60)
    print("Example 1: Basic RAG Usage")
    print("="*60)
    
    # Initialize components
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Create RAG pipeline
    rag = RAGPipeline(embedding_manager, milvus_manager)
    
    # Query
    result = rag.query(
        "What is artificial intelligence?",
        top_k=3,
        show_context=True
    )
    
    print(f"\nQuery: {result['query']}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nSources: {result['sources']}")
    
    # Cleanup
    milvus_manager.disconnect()


def example_document_processing():
    """Example of processing documents"""
    print("\n" + "="*60)
    print("Example 2: Document Processing")
    print("="*60)
    
    # Initialize document processor
    doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
    
    # Process a single document
    chunks = doc_processor.process_document("path/to/document.txt")
    
    print(f"\nProcessed document into {len(chunks)} chunks")
    print(f"\nFirst chunk:")
    print(f"Text: {chunks[0].text[:200]}...")
    print(f"Metadata: {chunks[0].metadata}")


def example_custom_retrieval():
    """Example of custom retrieval with filtering"""
    print("\n" + "="*60)
    print("Example 3: Custom Retrieval")
    print("="*60)
    
    # Initialize components
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Generate query embedding
    query = "machine learning algorithms"
    query_embedding = embedding_manager.generate_embedding(query)
    
    # Search with custom top_k
    results = milvus_manager.search(query_embedding, top_k=10)
    
    print(f"\nQuery: {query}")
    print(f"\nTop {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Source: {result['source']}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Cleanup
    milvus_manager.disconnect()


def example_batch_ingestion():
    """Example of batch document ingestion"""
    print("\n" + "="*60)
    print("Example 4: Batch Document Ingestion")
    print("="*60)
    
    # Initialize components
    doc_processor = DocumentProcessor()
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    milvus_manager.connect()
    milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
    milvus_manager.load_collection()
    
    # Process documents from directory
    chunks = doc_processor.process_directory("./data")
    
    if chunks:
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_manager.generate_embeddings(texts)
        
        # Prepare metadata
        sources = [chunk.metadata['source'] for chunk in chunks]
        chunk_indices = [chunk.metadata['chunk_index'] for chunk in chunks]
        
        # Insert into Milvus
        milvus_manager.insert_documents(
            embeddings=embeddings,
            texts=texts,
            sources=sources,
            chunk_indices=chunk_indices
        )
        
        print(f"\nIngested {len(chunks)} chunks")
        
        # Show stats
        stats = milvus_manager.get_collection_stats()
        print(f"\nCollection stats: {stats}")
    
    # Cleanup
    milvus_manager.disconnect()


def example_streaming_response():
    """Example of streaming response"""
    print("\n" + "="*60)
    print("Example 5: Streaming Response")
    print("="*60)
    
    # Initialize components
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Create RAG pipeline
    rag = RAGPipeline(embedding_manager, milvus_manager)
    
    # Query with streaming
    print("\nQuery: Explain neural networks")
    print("\nStreaming response:")
    result = rag.query(
        "Explain neural networks",
        stream=True
    )
    
    # Cleanup
    milvus_manager.disconnect()


if __name__ == "__main__":
    print("\nRAG Application - Example Usage\n")
    
    # Run examples (comment out as needed)
    try:
        # example_basic_usage()
        # example_document_processing()
        # example_custom_retrieval()
        # example_batch_ingestion()
        # example_streaming_response()
        
        print("\n" + "="*60)
        print("Examples completed!")
        print("="*60)
        print("\nNote: Uncomment the examples you want to run in the main block")
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()

# Made with Bob
