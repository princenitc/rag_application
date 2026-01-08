#!/usr/bin/env python3
"""
MCP Server for RAG Application
Exposes RAG functionality through Model Context Protocol
"""
import asyncio
import json
import sys
import os
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pathlib import Path

# CRITICAL: Redirect ALL stdout to stderr BEFORE any imports
# This prevents any print() statements from breaking MCP JSON protocol
_original_stdout = sys.stdout
sys.stdout = sys.stderr

# Also suppress progress bars and other output
os.environ['TQDM_DISABLE'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

from .config_loader import get_config
from .core.document_processor import DocumentProcessor
from .core.embedding_manager import EmbeddingManager
from .core.milvus_manager import MilvusManager
from .core.rag_pipeline import RAGPipeline

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    force=True
)
logger = logging.getLogger(__name__)

# Suppress warnings from third-party libraries
import warnings
warnings.filterwarnings('ignore')


# Load configuration
config = get_config()

# Global instances
doc_processor = None
embedding_manager = None
milvus_manager = None
rag_pipeline = None


def initialize_components():
    """Initialize RAG components"""
    global doc_processor, embedding_manager, milvus_manager, rag_pipeline
    
    logger.info("Initializing RAG components for MCP server...")
    
    # Initialize document processor
    doc_processor = DocumentProcessor(
        chunk_size=config.document_processing['chunk_size'],
        chunk_overlap=config.document_processing['chunk_overlap']
    )
    
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        model_name=config.embedding['model']
    )
    
    # Initialize Milvus manager
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
        logger.info("Connected to Milvus")
    except Exception as e:
        logger.warning(f"Could not connect to Milvus: {e}")
    
    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(
        embedding_manager=embedding_manager,
        milvus_manager=milvus_manager,
        ollama_model=config.ollama['model'],
        ollama_base_url=config.ollama['base_url']
    )
    
    logger.info("RAG components initialized successfully!")


# Create MCP server instance
app = Server("rag-application")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="query_rag",
            description="Query the RAG system with a question. Returns an AI-generated answer based on the indexed documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the RAG system"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant documents to retrieve (default: 5)",
                        "default": 5
                    },
                    "show_sources": {
                        "type": "boolean",
                        "description": "Include source documents in the response (default: true)",
                        "default": True
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="ingest_documents",
            description="Ingest documents from a directory into the RAG system. Processes and indexes documents for retrieval.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing documents to ingest"
                    },
                    "reset_collection": {
                        "type": "boolean",
                        "description": "Reset the collection before ingesting (default: false)",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="get_status",
            description="Get the current status of the RAG system, including Milvus and Ollama connectivity, and document count.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_documents",
            description="Search for relevant documents without generating an answer. Returns raw document chunks matching the query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of documents to retrieve (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_collection_stats",
            description="Get statistics about the document collection, including total documents and chunks.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="reset_collection",
            description="Reset the Milvus collection, removing all indexed documents. Use with caution!",
            inputSchema={
                "type": "object",
                "properties": {
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true to proceed)",
                        "default": False
                    }
                },
                "required": ["confirm"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    
    try:
        if name == "query_rag":
            question = arguments.get("question")
            if not question:
                raise ValueError("Question is required")
            
            top_k = arguments.get("top_k", 5)
            show_sources = arguments.get("show_sources", True)
            
            # Query the RAG system
            result = rag_pipeline.query(
                query=question,
                top_k=top_k,
                stream=False,
                show_context=False
            )
            
            # Format response
            response_text = f"**Answer:**\n{result['response']}\n"
            
            if show_sources and result['sources']:
                response_text += f"\n**Sources ({result['num_sources']}):**\n"
                for i, source in enumerate(set(result['sources']), 1):
                    response_text += f"{i}. {source}\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "ingest_documents":
            directory_path = arguments.get("directory_path")
            if not directory_path:
                raise ValueError("Directory path is required")
            
            reset_collection = arguments.get("reset_collection", False)
            
            # Validate directory
            dir_path = Path(directory_path)
            if not dir_path.exists():
                raise ValueError(f"Directory not found: {directory_path}")
            if not dir_path.is_dir():
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            # Reset if requested
            if reset_collection:
                milvus_manager.drop_collection()
                milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
                milvus_manager.load_collection()
            
            # Process documents
            chunks = doc_processor.process_directory(str(dir_path))
            
            if not chunks:
                return [TextContent(type="text", text="No valid documents found in the directory.")]
            
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
            unique_docs = len(set(sources))
            
            response_text = f"✅ **Ingestion Complete**\n\n"
            response_text += f"- Documents processed: {unique_docs}\n"
            response_text += f"- Chunks created: {len(chunks)}\n"
            response_text += f"- Collection reset: {reset_collection}\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "get_status":
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
                    milvus_status = "✅ running"
                    stats = milvus_manager.get_collection_stats()
                    milvus_docs = stats['num_entities']
            except Exception:
                milvus_status = "❌ not running"
            
            # Check Ollama
            ollama_status = "unknown"
            try:
                response = requests.get(
                    f"{config.ollama['base_url']}/api/tags",
                    timeout=2
                )
                if response.status_code == 200:
                    ollama_status = "✅ running"
            except Exception:
                ollama_status = "❌ not running"
            
            status_text = f"**RAG System Status**\n\n"
            status_text += f"- App: {config.app['name']} v{config.app['version']}\n"
            status_text += f"- Milvus: {milvus_status}\n"
            status_text += f"- Documents indexed: {milvus_docs}\n"
            status_text += f"- Ollama: {ollama_status}\n"
            status_text += f"- LLM Model: {config.ollama['model']}\n"
            status_text += f"- Embedding Model: {config.embedding['model']}\n"
            
            return [TextContent(type="text", text=status_text)]
        
        elif name == "search_documents":
            query = arguments.get("query")
            if not query:
                raise ValueError("Query is required")
            
            top_k = arguments.get("top_k", 5)
            
            # Search documents
            results = rag_pipeline.retrieve_context(query, top_k)
            
            if not results:
                return [TextContent(type="text", text="No relevant documents found.")]
            
            # Format results
            response_text = f"**Search Results ({len(results)} documents):**\n\n"
            for i, result in enumerate(results, 1):
                response_text += f"**{i}. {result['source']}** (Score: {result['score']:.3f})\n"
                response_text += f"{result['text'][:300]}...\n\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "get_collection_stats":
            stats = milvus_manager.get_collection_stats()
            
            stats_text = f"**Collection Statistics**\n\n"
            stats_text += f"- Collection: {stats['collection_name']}\n"
            stats_text += f"- Total entities: {stats['num_entities']}\n"
            
            return [TextContent(type="text", text=stats_text)]
        
        elif name == "reset_collection":
            confirm = arguments.get("confirm", False)
            
            if not confirm:
                return [TextContent(
                    type="text",
                    text="⚠️ Collection reset requires confirmation. Set 'confirm' to true to proceed."
                )]
            
            # Reset collection
            milvus_manager.drop_collection()
            milvus_manager.create_collection(dimension=embedding_manager.get_dimension())
            milvus_manager.load_collection()
            
            return [TextContent(
                type="text",
                text="✅ Collection has been reset. All documents have been removed."
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


async def main():
    """Main entry point for MCP server"""
    # Initialize components
    initialize_components()
    
    # Restore stdout for MCP protocol communication
    sys.stdout = _original_stdout
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run_mcp_server():
    """Run the MCP server"""
    logger.info("Starting RAG MCP Server...")
    asyncio.run(main())


if __name__ == "__main__":
    run_mcp_server()

# Made with Bob