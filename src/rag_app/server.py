"""
FastAPI server for RAG application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import shutil
from pathlib import Path
import asyncio
import json

from .config_loader import get_config
from .core.document_processor import DocumentProcessor
from .core.embedding_manager import EmbeddingManager
from .core.milvus_manager import MilvusManager
from .core.rag_pipeline import RAGPipeline


# Load configuration
config = get_config()

# Initialize FastAPI app
app = FastAPI(
    title=config.app['name'],
    version=config.app['version'],
    description="RAG Application API with Milvus and Ollama"
)

# Global instances (initialized on startup)
doc_processor = None
embedding_manager = None
milvus_manager = None
rag_pipeline = None


# Pydantic models
class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask")
    top_k: Optional[int] = Field(None, description="Number of documents to retrieve")
    stream: bool = Field(False, description="Stream the response")


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    num_sources: int


class IngestRequest(BaseModel):
    reset: bool = Field(False, description="Reset collection before ingesting")


class IngestResponse(BaseModel):
    status: str
    num_chunks: int
    num_documents: int
    message: str


class StatusResponse(BaseModel):
    app_name: str
    version: str
    milvus_status: str
    milvus_documents: int
    ollama_status: str
    ollama_model: str
    embedding_model: str


class DocumentInfo(BaseModel):
    filename: str
    size: int
    type: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global doc_processor, embedding_manager, milvus_manager, rag_pipeline
    
    print("🚀 Starting RAG Application Server...")
    
    # Create upload directory
    upload_dir = Path(config.paths['upload_dir'])
    upload_dir.mkdir(exist_ok=True)
    
    # Initialize components
    doc_processor = DocumentProcessor(
        chunk_size=config.document_processing['chunk_size'],
        chunk_overlap=config.document_processing['chunk_overlap']
    )
    
    embedding_manager = EmbeddingManager(
        model_name=config.embedding['model']
    )
    
    milvus_manager = MilvusManager(
        host=config.milvus['host'],
        port=str(config.milvus['port']),
        collection_name=config.milvus['collection_name']
    )
    
    # Connect to Milvus
    try:
        milvus_manager.connect()
        milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
        milvus_manager.load_collection()
        print("✓ Connected to Milvus")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Milvus: {e}")
    
    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(
        embedding_manager=embedding_manager,
        milvus_manager=milvus_manager,
        ollama_model=config.ollama['model'],
        ollama_base_url=config.ollama['base_url']
    )
    
    print("✅ Server started successfully!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if milvus_manager:
        milvus_manager.disconnect()
    print("👋 Server shutdown complete")


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Application API",
        "version": config.app['version'],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Status endpoint
@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    import requests
    
    # Check Milvus
    milvus_status = "unknown"
    milvus_docs = 0
    try:
        response = requests.get(
            f"http://{config.milvus['host']}:9091/healthz",
            timeout=2
        )
        if response.status_code == 200:
            milvus_status = "running"
            stats = milvus_manager.get_collection_stats()
            milvus_docs = stats['num_entities']
    except Exception:
        milvus_status = "not running"
    
    # Check Ollama
    ollama_status = "unknown"
    try:
        response = requests.get(
            f"{config.ollama['base_url']}/api/tags",
            timeout=2
        )
        if response.status_code == 200:
            ollama_status = "running"
    except Exception:
        ollama_status = "not running"
    
    return StatusResponse(
        app_name=config.app['name'],
        version=config.app['version'],
        milvus_status=milvus_status,
        milvus_documents=milvus_docs,
        ollama_status=ollama_status,
        ollama_model=config.ollama['model'],
        embedding_model=config.embedding['model']
    )


# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system"""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        result = rag_pipeline.query(
            query=request.question,
            top_k=request.top_k or config.retrieval['top_k'],
            stream=False
        )
        
        return QueryResponse(
            question=result['query'],
            answer=result['response'],
            sources=result['sources'],
            num_sources=result['num_sources']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Streaming query endpoint
@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """Query with streaming response"""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    async def generate():
        try:
            # Retrieve context
            results = rag_pipeline.retrieve_context(
                request.question,
                request.top_k or config.retrieval['top_k']
            )
            context = rag_pipeline.format_context(results)
            prompt = rag_pipeline.generate_prompt(request.question, context)
            
            # Stream response
            stream_response = rag_pipeline.client.chat(
                model=config.ollama['model'],
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            for chunk in stream_response:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Send sources at the end
            sources = [r['source'] for r in results]
            yield f"data: {json.dumps({'sources': sources, 'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# Upload document endpoint
@app.post("/documents/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in config.document_processing['supported_extensions']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {config.document_processing['supported_extensions']}"
        )
    
    # Save file
    upload_dir = Path(config.paths['upload_dir'])
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = file_path.stat().st_size
    
    return DocumentInfo(
        filename=file.filename,
        size=file_size,
        type=file_ext
    )


# Ingest documents endpoint
@app.post("/documents/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """Ingest uploaded documents"""
    upload_dir = Path(config.paths['upload_dir'])
    
    if not any(upload_dir.iterdir()):
        raise HTTPException(status_code=400, detail="No documents to ingest")
    
    try:
        # Reset if requested
        if request.reset:
            milvus_manager.drop_collection()
            milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
            milvus_manager.load_collection()
        
        # Process documents
        chunks = doc_processor.process_directory(str(upload_dir))
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid documents found")
        
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
        
        # Get stats
        stats = milvus_manager.get_collection_stats()
        
        # Count unique documents
        unique_docs = len(set(sources))
        
        return IngestResponse(
            status="success",
            num_chunks=len(chunks),
            num_documents=unique_docs,
            message=f"Successfully ingested {unique_docs} documents ({len(chunks)} chunks)"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List documents endpoint
@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List uploaded documents"""
    upload_dir = Path(config.paths['upload_dir'])
    
    documents = []
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            documents.append(DocumentInfo(
                filename=file_path.name,
                size=file_path.stat().st_size,
                type=file_path.suffix
            ))
    
    return documents


# Delete document endpoint
@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete an uploaded document"""
    upload_dir = Path(config.paths['upload_dir'])
    file_path = upload_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path.unlink()
    return {"message": f"Document {filename} deleted"}


# Reset collection endpoint
@app.post("/collection/reset")
async def reset_collection():
    """Reset the Milvus collection"""
    try:
        milvus_manager.drop_collection()
        milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
        milvus_manager.load_collection()
        return {"message": "Collection reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Collection stats endpoint
@app.get("/collection/stats")
async def get_collection_stats():
    """Get collection statistics"""
    try:
        stats = milvus_manager.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for server"""
    import uvicorn
    uvicorn.run(
        "rag_app.server:app",
        host=config.server['host'],
        port=config.server['port'],
        reload=config.server['reload']
    )


if __name__ == "__main__":
    main()

# Made with Bob
