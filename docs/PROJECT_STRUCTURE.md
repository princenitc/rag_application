# Project Structure

This document describes the organization of the RAG application codebase.

## Directory Layout

```
rag_application/
├── src/
│   └── rag_app/                    # Main application package
│       ├── __init__.py             # Package initialization
│       ├── config.py               # Configuration management
│       ├── core/                   # Core functionality modules
│       │   ├── __init__.py
│       │   ├── embedding_manager.py    # Embedding generation
│       │   ├── document_processor.py   # Document loading & chunking
│       │   ├── milvus_manager.py       # Vector database operations
│       │   └── rag_pipeline.py         # RAG query pipeline
│       ├── scripts/                # CLI scripts
│       │   ├── __init__.py
│       │   ├── ingest.py           # Document ingestion script
│       │   └── query.py            # Query interface script
│       └── utils/                  # Utility functions
│           └── __init__.py
├── tests/                          # Unit tests
│   ├── __init__.py
│   └── test_embedding_manager.py
├── examples/                       # Example usage scripts
│   └── example_usage.py
├── docs/                           # Documentation
│   ├── README.md                   # Main documentation
│   ├── setup_guide.md              # Setup instructions
│   └── PROJECT_STRUCTURE.md        # This file
├── data/                           # Data directory (for documents)
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup configuration
└── MANIFEST.in                     # Package manifest

```

## Module Descriptions

### Core Modules (`src/rag_app/core/`)

#### `embedding_manager.py`
- **Purpose**: Generate embeddings for text using sentence-transformers
- **Key Classes**: `EmbeddingManager`
- **Responsibilities**:
  - Load and manage embedding models
  - Generate embeddings for single or multiple texts
  - Normalize embeddings for similarity search

#### `document_processor.py`
- **Purpose**: Load and process documents into chunks
- **Key Classes**: `DocumentProcessor`, `DocumentChunk`
- **Responsibilities**:
  - Load documents (TXT, PDF, DOCX, MD)
  - Split text into chunks with overlap
  - Preserve document metadata
  - Handle directory processing

#### `milvus_manager.py`
- **Purpose**: Manage Milvus vector database operations
- **Key Classes**: `MilvusManager`
- **Responsibilities**:
  - Connect to Milvus server
  - Create and manage collections
  - Insert document embeddings
  - Perform similarity search
  - Manage indexes

#### `rag_pipeline.py`
- **Purpose**: Implement the RAG query pipeline
- **Key Classes**: `RAGPipeline`
- **Responsibilities**:
  - Retrieve relevant context from Milvus
  - Format context for LLM
  - Generate responses using Ollama
  - Handle streaming responses
  - Provide interactive chat interface

### Configuration (`src/rag_app/config.py`)

Centralized configuration management using environment variables:
- Milvus connection settings
- Embedding model configuration
- Ollama settings
- Document processing parameters
- Retrieval settings

### Scripts (`src/rag_app/scripts/`)

#### `ingest.py`
- **Purpose**: CLI tool for document ingestion
- **Usage**: `python -m rag_app.scripts.ingest <path> [--reset]`
- **Features**:
  - Process single files or directories
  - Generate embeddings
  - Store in Milvus
  - Reset collection option

#### `query.py`
- **Purpose**: CLI tool for querying the system
- **Usage**: 
  - Interactive: `python -m rag_app.scripts.query`
  - Single query: `python -m rag_app.scripts.query --query "question"`
- **Features**:
  - Interactive chat mode
  - Single query mode
  - Configurable retrieval parameters
  - Context display option

### Tests (`tests/`)

Unit tests for core functionality:
- `test_embedding_manager.py`: Tests for embedding generation
- Additional test files can be added for other modules

### Examples (`examples/`)

Example scripts demonstrating programmatic usage:
- `example_usage.py`: Various usage patterns and examples

### Documentation (`docs/`)

- `README.md`: Main project documentation
- `setup_guide.md`: Detailed setup instructions
- `PROJECT_STRUCTURE.md`: This file

## Package Installation

The project can be installed as a package:

```bash
# Development installation
pip install -e .

# Regular installation
pip install .
```

After installation, CLI commands are available:
```bash
rag-ingest <path>
rag-query
```

## Import Patterns

### From within the package:
```python
from ..config import MILVUS_HOST
from .embedding_manager import EmbeddingManager
```

### From external code:
```python
from rag_app import EmbeddingManager, MilvusManager
from rag_app.core import DocumentProcessor, RAGPipeline
```

## Configuration Files

### `.env`
Environment-specific configuration (not in version control):
```env
MILVUS_HOST=localhost
OLLAMA_MODEL=llama2
# ... other settings
```

### `.env.example`
Template for environment variables (in version control)

### `requirements.txt`
Python package dependencies

### `setup.py`
Package metadata and installation configuration

## Data Flow

1. **Ingestion**:
   ```
   Documents → DocumentProcessor → EmbeddingManager → MilvusManager
   ```

2. **Query**:
   ```
   User Query → EmbeddingManager → MilvusManager (search) → RAGPipeline → Ollama → Response
   ```

## Best Practices

1. **Imports**: Use relative imports within the package
2. **Configuration**: Use environment variables via `config.py`
3. **Error Handling**: Implement proper exception handling
4. **Logging**: Use print statements or logging module
5. **Type Hints**: Include type hints for better code clarity
6. **Documentation**: Add docstrings to all classes and functions

## Adding New Features

### Adding a new core module:
1. Create file in `src/rag_app/core/`
2. Add imports to `src/rag_app/core/__init__.py`
3. Update `src/rag_app/__init__.py` if needed
4. Add tests in `tests/`

### Adding a new script:
1. Create file in `src/rag_app/scripts/`
2. Add entry point in `setup.py` if needed
3. Update documentation

### Adding utilities:
1. Create file in `src/rag_app/utils/`
2. Add imports to `src/rag_app/utils/__init__.py`

## Testing

Run tests:
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_embedding_manager.py

# Run with coverage
python -m pytest --cov=src/rag_app tests/
```

## Development Workflow

1. Create virtual environment
2. Install in development mode: `pip install -e .`
3. Make changes
4. Run tests
5. Update documentation
6. Commit changes

## Version Control

Files tracked in git:
- All source code
- Documentation
- Configuration templates
- Tests
- Setup files

Files ignored (`.gitignore`):
- Virtual environments
- `__pycache__`
- `.env` (actual config)
- `data/` (documents)
- IDE-specific files