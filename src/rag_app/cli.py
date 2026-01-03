"""
Unified CLI interface for RAG application
"""
import sys
import argparse
from pathlib import Path
from .core.document_processor import DocumentProcessor
from .core.embedding_manager import EmbeddingManager
from .core.milvus_manager import MilvusManager
from .core.rag_pipeline import RAGPipeline
from . import config


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              RAG Application with Llama3                  ║
    ║         Powered by MilvusDB & Ollama                      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_services():
    """Check if required services are running"""
    import subprocess
    
    print("\n🔍 Checking services...")
    
    # Check Milvus
    try:
        import requests
        response = requests.get(f"http://{config.MILVUS_HOST}:9091/healthz", timeout=2)
        if response.status_code == 200:
            print("✓ Milvus is running")
        else:
            print("✗ Milvus is not responding properly")
            return False
    except Exception:
        print("✗ Milvus is not running")
        print("  Run: ./scripts/start_milvus.sh")
        return False
    
    # Check Ollama
    try:
        import requests
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama is running")
        else:
            print("✗ Ollama is not responding properly")
            return False
    except Exception:
        print("✗ Ollama is not running")
        print("  Run: ollama serve")
        return False
    
    return True


def cmd_ingest(args):
    """Ingest documents command"""
    print_banner()
    
    if not check_services():
        sys.exit(1)
    
    print(f"\n📂 Ingesting documents from: {args.path}")
    
    # Initialize components
    doc_processor = DocumentProcessor()
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    milvus_manager.connect()
    
    # Reset if requested
    if args.reset:
        print("\n⚠️  Resetting collection...")
        milvus_manager.drop_collection()
    
    # Create/load collection
    milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
    milvus_manager.load_collection()
    
    # Process documents
    path = Path(args.path)
    if path.is_file():
        chunks = doc_processor.process_document(str(path))
    elif path.is_dir():
        chunks = doc_processor.process_directory(str(path))
    else:
        print(f"❌ Error: {args.path} is not a valid file or directory")
        sys.exit(1)
    
    if not chunks:
        print("❌ No documents to process!")
        sys.exit(1)
    
    # Generate embeddings
    print(f"\n🔄 Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)
    
    # Prepare metadata
    sources = [chunk.metadata['source'] for chunk in chunks]
    chunk_indices = [chunk.metadata['chunk_index'] for chunk in chunks]
    
    # Insert into Milvus
    print("\n💾 Storing in Milvus...")
    milvus_manager.insert_documents(
        embeddings=embeddings,
        texts=texts,
        sources=sources,
        chunk_indices=chunk_indices
    )
    
    # Show statistics
    stats = milvus_manager.get_collection_stats()
    print("\n✅ Ingestion completed!")
    print(f"   Total documents: {stats['num_entities']}")
    print(f"   Collection: {stats['name']}")
    
    milvus_manager.disconnect()


def cmd_query(args):
    """Query command"""
    print_banner()
    
    if not check_services():
        sys.exit(1)
    
    # Initialize components
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect
    milvus_manager.connect()
    milvus_manager.load_collection()
    
    # Show stats
    stats = milvus_manager.get_collection_stats()
    print(f"\n📊 Collection: {stats['name']}")
    print(f"   Documents: {stats['num_entities']}")
    
    # Create RAG pipeline
    rag = RAGPipeline(embedding_manager, milvus_manager)
    
    if args.question:
        # Single query mode
        print(f"\n❓ Question: {args.question}\n")
        result = rag.query(args.question, top_k=args.top_k, stream=True)
        print(f"\n\n📚 Sources: {', '.join(set(result['sources']))}")
    else:
        # Interactive mode
        rag.chat(stream=True)
    
    milvus_manager.disconnect()


def cmd_status(args):
    """Show system status"""
    print_banner()
    
    print("\n📊 System Status\n")
    
    # Check Milvus
    try:
        import requests
        response = requests.get(f"http://{config.MILVUS_HOST}:9091/healthz", timeout=2)
        if response.status_code == 200:
            print("✓ Milvus: Running")
            
            # Get collection stats
            try:
                milvus_manager = MilvusManager()
                milvus_manager.connect()
                milvus_manager.load_collection()
                stats = milvus_manager.get_collection_stats()
                print(f"  - Collection: {stats['name']}")
                print(f"  - Documents: {stats['num_entities']}")
                print(f"  - Dimension: {stats['dimension']}")
                milvus_manager.disconnect()
            except Exception as e:
                print(f"  - Collection: Not initialized")
        else:
            print("✗ Milvus: Not responding")
    except Exception:
        print("✗ Milvus: Not running")
    
    # Check Ollama
    try:
        import requests
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama: Running")
            models = response.json().get('models', [])
            if models:
                print(f"  - Models: {', '.join([m['name'] for m in models])}")
            print(f"  - Active model: {config.OLLAMA_MODEL}")
        else:
            print("✗ Ollama: Not responding")
    except Exception:
        print("✗ Ollama: Not running")
    
    # Configuration
    print("\n⚙️  Configuration")
    print(f"  - Embedding model: {config.EMBEDDING_MODEL}")
    print(f"  - Chunk size: {config.CHUNK_SIZE}")
    print(f"  - Top K: {config.TOP_K}")


def cmd_reset(args):
    """Reset the collection"""
    print_banner()
    
    if not args.confirm:
        response = input("\n⚠️  This will delete all documents. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    print("\n🗑️  Resetting collection...")
    
    milvus_manager = MilvusManager()
    milvus_manager.connect()
    milvus_manager.drop_collection()
    
    print("✅ Collection reset complete!")
    milvus_manager.disconnect()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RAG Application - Retrieval-Augmented Generation with Milvus & Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rag ingest ./data/              # Ingest all documents
  rag query                        # Interactive chat
  rag query -q "What is AI?"      # Single question
  rag status                       # Check system status
  rag reset                        # Reset collection
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents')
    ingest_parser.add_argument('path', help='Path to document or directory')
    ingest_parser.add_argument('--reset', action='store_true', help='Reset collection before ingesting')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the system')
    query_parser.add_argument('-q', '--question', help='Single question (interactive mode if not provided)')
    query_parser.add_argument('--top-k', type=int, default=config.TOP_K, help='Number of documents to retrieve')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset the collection')
    reset_parser.add_argument('--confirm', action='store_true', help='Skip confirmation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'ingest':
            cmd_ingest(args)
        elif args.command == 'query':
            cmd_query(args)
        elif args.command == 'status':
            cmd_status(args)
        elif args.command == 'reset':
            cmd_reset(args)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
