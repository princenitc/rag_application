"""
Document Ingestion Script
Loads documents, generates embeddings, and stores them in Milvus
"""
import argparse
import sys
from pathlib import Path
from tqdm import tqdm
from .. import config
from ..core.document_processor import DocumentProcessor
from ..core.embedding_manager import EmbeddingManager
from ..core.milvus_manager import MilvusManager


def ingest_documents(data_path: str, reset: bool = False):
    """
    Ingest documents into the RAG system
    
    Args:
        data_path: Path to documents or directory
        reset: Whether to reset the collection before ingesting
    """
    print("="*60)
    print("Document Ingestion Pipeline")
    print("="*60)
    
    # Initialize components
    print("\n1. Initializing components...")
    doc_processor = DocumentProcessor()
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    
    # Connect to Milvus
    print("\n2. Connecting to Milvus...")
    milvus_manager.connect()
    
    # Reset collection if requested
    if reset:
        print("\n3. Resetting collection...")
        milvus_manager.drop_collection()
    
    # Create or load collection
    print("\n4. Setting up collection...")
    milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
    milvus_manager.load_collection()
    
    # Process documents
    print(f"\n5. Processing documents from: {data_path}")
    path = Path(data_path)
    
    if path.is_file():
        chunks = doc_processor.process_document(str(path))
    elif path.is_dir():
        chunks = doc_processor.process_directory(str(path))
    else:
        print(f"Error: {data_path} is not a valid file or directory")
        sys.exit(1)
    
    if not chunks:
        print("No documents to process!")
        sys.exit(1)
    
    # Generate embeddings
    print(f"\n6. Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)
    
    # Prepare metadata
    sources = [chunk.metadata['source'] for chunk in chunks]
    chunk_indices = [chunk.metadata['chunk_index'] for chunk in chunks]
    
    # Insert into Milvus
    print("\n7. Inserting documents into Milvus...")
    milvus_manager.insert_documents(
        embeddings=embeddings,
        texts=texts,
        sources=sources,
        chunk_indices=chunk_indices
    )
    
    # Show statistics
    print("\n8. Collection Statistics:")
    stats = milvus_manager.get_collection_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)
    print("Ingestion completed successfully!")
    print("="*60)
    
    # Disconnect
    milvus_manager.disconnect()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Ingest documents into the RAG system"
    )
    parser.add_argument(
        "data_path",
        type=str,
        help="Path to document file or directory containing documents"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the collection before ingesting (deletes existing data)"
    )
    
    args = parser.parse_args()
    
    try:
        ingest_documents(args.data_path, args.reset)
    except KeyboardInterrupt:
        print("\n\nIngestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
