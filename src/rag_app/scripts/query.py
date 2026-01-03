"""
Query Script for RAG Application
Interactive and single-query modes
"""
import argparse
import sys
from .. import config
from ..core.embedding_manager import EmbeddingManager
from ..core.milvus_manager import MilvusManager
from ..core.rag_pipeline import RAGPipeline


def run_single_query(query: str, top_k: int = None, show_context: bool = False):
    """
    Run a single query
    
    Args:
        query: User query
        top_k: Number of documents to retrieve
        show_context: Whether to show retrieved context
    """
    # Initialize components
    print("Initializing RAG system...")
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Create RAG pipeline
    rag_pipeline = RAGPipeline(embedding_manager, milvus_manager)
    
    # Process query
    result = rag_pipeline.query(query, top_k=top_k, show_context=show_context)
    
    # Display results
    print("\n" + "="*60)
    print("QUERY RESULT")
    print("="*60)
    print(f"\nQuery: {result['query']}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nSources ({result['num_sources']}):")
    for source in set(result['sources']):
        print(f"  - {source}")
    
    if show_context and 'retrieved_documents' in result:
        print("\n" + "-"*60)
        print("RETRIEVED CONTEXT")
        print("-"*60)
        for i, doc in enumerate(result['retrieved_documents'], 1):
            print(f"\n[Document {i}]")
            print(f"Source: {doc['source']}")
            print(f"Score: {doc['score']:.3f}")
            print(f"Text: {doc['text'][:200]}...")
    
    print("\n" + "="*60)
    
    # Disconnect
    milvus_manager.disconnect()


def run_interactive_mode(top_k: int = None):
    """
    Run interactive chat mode
    
    Args:
        top_k: Number of documents to retrieve
    """
    # Initialize components
    print("Initializing RAG system...")
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Show collection stats
    stats = milvus_manager.get_collection_stats()
    print(f"\nCollection: {stats['name']}")
    print(f"Documents: {stats['num_entities']}")
    print(f"Dimension: {stats['dimension']}")
    
    # Create RAG pipeline
    rag_pipeline = RAGPipeline(embedding_manager, milvus_manager)
    
    # Start chat
    try:
        rag_pipeline.chat(stream=True)
    finally:
        milvus_manager.disconnect()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Query the RAG system"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Single query to process (if not provided, enters interactive mode)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=config.TOP_K,
        help=f"Number of documents to retrieve (default: {config.TOP_K})"
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Show retrieved context (only for single query mode)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.query:
            # Single query mode
            run_single_query(args.query, args.top_k, args.show_context)
        else:
            # Interactive mode
            run_interactive_mode(args.top_k)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
