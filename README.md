# RAG Application with MilvusDB and Ollama

A production-ready, end-to-end Retrieval-Augmented Generation (RAG) application built with Python, using MilvusDB for vector storage and Ollama for language model inference.

## 🌟 Features

- 📄 **Multi-format Document Support**: TXT, PDF, DOCX, and Markdown
- 🔍 **Efficient Vector Search**: Powered by MilvusDB with IVF_FLAT indexing
- 🤖 **Local LLM Integration**: Uses Ollama (Llama3) for privacy-focused inference
- 💬 **Dual Interface**: CLI and REST API server modes
- 🌐 **REST API**: FastAPI server with interactive documentation
- 🎯 **Flexible Querying**: Single query, interactive chat, or API calls
- ⚙️ **TOML Configuration**: Clean, readable configuration file
- 📦 **Installable Package**: Install via pip with CLI commands
- 🧪 **Unit Tests**: Comprehensive test coverage
- 🔄 **Streaming Support**: Real-time response streaming

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

# Install dependencies
pip install -r requirements.txt
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

Edit `config.toml` to customize settings:

```toml
[ollama]
model = "llama3"  # Change model here

[server]
port = 8000       # Change server port
```

### Usage

#### CLI Mode

**Check Status:**
```bash
python main.py cli status
```

**Ingest Documents:**
```bash
# Create data directory and add documents
mkdir data
# Add your PDF, TXT, DOCX, or MD files

# Ingest documents
python main.py cli ingest ./data/
```

**Query the System:**
```bash
# Interactive chat
python main.py cli query

# Single question
python main.py cli query -q "What is machine learning?"
```

#### Server Mode

**Start the API Server:**
```bash
python main.py server
```

**Access the API:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Example API Calls:**
```bash
# Query via API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "top_k": 5}'

# Upload document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"

# Ingest documents
curl -X POST "http://localhost:8000/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{"reset": false}'
```

## 📚 Documentation

- **[Quick Start](QUICKSTART.md)**: Get started in 5 minutes
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference
- **[Milvus Setup](docs/MILVUS_SETUP.md)**: Milvus installation and troubleshooting
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Codebase organization

## 🔧 Configuration

Configuration is managed via `config.toml`:

```toml
[milvus]
host = "localhost"
port = 19530
collection_name = "rag_documents"

[embedding]
model = "sentence-transformers/all-MiniLM-L6-v2"
dimension = 384

[ollama]
base_url = "http://localhost:11434"
model = "llama3"

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
## 📚 Documentation

### Quick Start Guides
- **[MCP_FINAL_SETUP.md](MCP_FINAL_SETUP.md)**: ✅ **START HERE** - Complete working MCP setup
- **[QUICK_START_MCP.md](QUICK_START_MCP.md)**: 5-minute MCP quick start
- **[QUICKSTART.md](QUICKSTART.md)**: General application quick start

### MCP Server Documentation
- **[HOW_TO_USE_MCP.md](HOW_TO_USE_MCP.md)**: Complete MCP usage guide with examples
- **[CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)**: Detailed Claude Desktop setup
- **[MCP_SETUP_GUIDE.md](MCP_SETUP_GUIDE.md)**: General MCP information
- **[docs/MCP_SERVER.md](docs/MCP_SERVER.md)**: Technical MCP API documentation

### General Documentation
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete REST API reference
- **[Milvus Setup](docs/MILVUS_SETUP.md)**: Milvus installation and troubleshooting
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Codebase organization

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