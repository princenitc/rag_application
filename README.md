# RAG Application with MilvusDB and Ollama

A production-ready, end-to-end Retrieval-Augmented Generation (RAG) application built with Python, using MilvusDB for vector storage and Ollama for language model inference.

## 🌟 Features

- 📄 **Multi-format Document Support**: TXT, PDF, DOCX, and Markdown
- 🔍 **Efficient Vector Search**: Powered by MilvusDB with IVF_FLAT indexing
- 🤖 **Local LLM Integration**: Uses Ollama for privacy-focused inference
- 💬 **Interactive Chat Interface**: Command-line chat with streaming responses
- 🎯 **Flexible Querying**: Single query or interactive modes
- ⚙️ **Easy Configuration**: Environment-based settings
- 📦 **Installable Package**: Install via pip with CLI commands
- 🧪 **Unit Tests**: Comprehensive test coverage

## 📁 Project Structure

```
rag_application/
├── src/rag_app/              # Main application package
│   ├── core/                 # Core functionality
│   │   ├── embedding_manager.py
│   │   ├── document_processor.py
│   │   ├── milvus_manager.py
│   │   └── rag_pipeline.py
│   ├── scripts/              # CLI scripts
│   │   ├── ingest.py
│   │   └── query.py
│   ├── utils/                # Utilities
│   └── config.py             # Configuration
├── tests/                    # Unit tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
│   ├── README.md
│   ├── setup_guide.md
│   ├── USAGE.md
│   └── PROJECT_STRUCTURE.md
├── requirements.txt          # Dependencies
└── setup.py                  # Package setup
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **MilvusDB** (via Docker)
3. **Ollama** with a model installed

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd rag_application

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Setup Services

**Start MilvusDB:**
```bash
docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest
```

**Start Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Start server
ollama serve
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### Usage

**Ingest Documents:**
```bash
# Create data directory and add documents
mkdir data
# Add your PDF, TXT, DOCX, or MD files

# Ingest documents
rag-ingest ./data/
```

**Query the System:**
```bash
# Interactive chat
rag-query

# Single query
rag-query --query "What is machine learning?"
```

## 📚 Documentation

- **[Quick Start](QUICKSTART.md)**: Get started in 5 minutes
- **[Milvus Setup](docs/MILVUS_SETUP.md)**: Milvus installation and troubleshooting
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Codebase organization

## 🔧 Configuration Options

Key environment variables in `.env`:

```env
# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
COLLECTION_NAME=rag_documents

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
```

## 💻 Programmatic Usage

```python
from rag_app import EmbeddingManager, MilvusManager, RAGPipeline

# Initialize components
embedding_manager = EmbeddingManager()
milvus_manager = MilvusManager()
milvus_manager.connect()
milvus_manager.load_collection()

# Create RAG pipeline
rag = RAGPipeline(embedding_manager, milvus_manager)

# Query
result = rag.query("What is AI?", top_k=5)
print(result['response'])
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src/rag_app tests/
```

## 🏗️ Architecture

```
┌─────────────┐
│  Documents  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Document        │
│ Processor       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Embedding       │
│ Generator       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ MilvusDB        │
│ (Vector Store)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐     ┌─────────────┐
│ RAG Pipeline    │────▶│   Ollama    │
└─────────────────┘     └─────────────┘
       │
       ▼
┌─────────────────┐
│   Response      │
└─────────────────┘
```

## 🛠️ Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## 📦 Dependencies

- `pymilvus`: Milvus Python SDK
- `sentence-transformers`: Embedding generation
- `ollama`: Ollama Python client
- `pypdf`: PDF processing
- `python-docx`: DOCX processing
- `langchain`: Document utilities

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [MilvusDB](https://milvus.io/) for vector storage
- [Ollama](https://ollama.ai/) for local LLM inference
- [Sentence-Transformers](https://www.sbert.net/) for embeddings
- [LangChain](https://python.langchain.com/) for document processing

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🗺️ Roadmap

- [ ] Web interface
- [ ] Conversation history
- [ ] Multiple collection support
- [ ] Advanced filtering
- [ ] Batch processing optimization
- [ ] Docker Compose setup
- [ ] API server

---

**Built with ❤️ for the AI community**