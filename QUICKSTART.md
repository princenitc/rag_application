# Quick Start Guide

Get your RAG application running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Python 3.8+ installed
- 8GB RAM available

## Step 1: Start Milvus (30 seconds)

```bash
# Use the provided script
./scripts/start_milvus.sh

# Or manually with docker-compose
docker-compose up -d
```

Wait for the message: "✓ Services are healthy!"

## Step 2: Install Ollama (2 minutes)

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull llama3 model
ollama pull llama3

# Start Ollama (in a new terminal)
ollama serve
```

## Step 3: Install Dependencies (1 minute)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure (30 seconds)

The application uses `config.toml` for configuration. The default settings should work, but you can customize:

```toml
# Edit config.toml
[ollama]
model = "llama3"  # Change if using different model

[server]
port = 8000       # API server port
```

## Step 5: Add Documents (30 seconds)

```bash
# Create data directory
mkdir -p data

# Add your documents (PDF, TXT, DOCX, or MD files)
# For testing, create a sample file:
echo "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data." > data/sample.txt
```

## Step 6: Check Status (Optional)

```bash
# Check if everything is running
rag status
```

## Step 7: Ingest Documents (1 minute)

```bash
# Ingest all documents
rag ingest ./data/
```

You should see:
```
✓ Documents processed
✓ Embeddings generated
✓ Stored in Milvus
```

## Step 8: Query! (Now!)

```bash
# Start interactive chat
rag query
```

Try asking:
```
You: What is machine learning?
```

Or use single query mode:
```bash
rag query -q "What is machine learning?"
```

## Troubleshooting

### Milvus container exits immediately?

**Solution:** Use Docker Compose (it includes all dependencies)
```bash
./scripts/start_milvus.sh
```

See [docs/MILVUS_SETUP.md](docs/MILVUS_SETUP.md) for detailed troubleshooting.

### Connection refused?

**Check if services are running:**
```bash
# Check Milvus
docker-compose ps

# Check Ollama
curl http://localhost:11434/api/tags
```

### Out of memory?

**Increase Docker memory:**
- Docker Desktop → Settings → Resources
- Set Memory to at least 8GB

## Verification

Test everything is working:

```bash
# Test Milvus
curl http://localhost:9091/healthz
# Should return: OK

# Test Ollama
curl http://localhost:11434/api/tags
# Should return: JSON with models including llama3

# Test Python connection
python -c "from src.rag_app.core.milvus_manager import MilvusManager; m = MilvusManager(); m.connect(); print('✓ Connected!')"
```

## Using Different Ollama Models

The default is `llama3`, but you can use other models:

```bash
# Pull other models
ollama pull mistral
ollama pull codellama
ollama pull llama2

# Update .env file
OLLAMA_MODEL=mistral
```

Available models:
- `llama3` (default, recommended)
- `llama2` (older version)
- `mistral` (fast and efficient)
- `codellama` (for code-related queries)
- `phi` (lightweight)

## Bonus: Try the API Server!

```bash
# Start the API server
rag-server

# In another terminal, try the API
curl "http://localhost:8000/status"
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'

# Visit interactive docs
open http://localhost:8000/docs
```

## Next Steps

- Try the **API Server**: `rag-server` for REST API access
- Read [API Documentation](docs/API_DOCUMENTATION.md) for API reference
- Check [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for architecture
- See [examples/example_usage.py](examples/example_usage.py) for programmatic usage
- Read [README.md](README.md) for complete documentation

## Quick Commands

```bash
# CLI Mode
python main.py cli status                    # Check system status
python main.py cli ingest ./data/           # Ingest documents
python main.py cli query                     # Interactive chat
python main.py cli query -q "your question" # Single question
python main.py cli reset                     # Reset collection

# Server Mode
python main.py server                        # Start API server
python main.py server --port 8080           # Custom port

# Milvus Management
./scripts/start_milvus.sh                   # Start Milvus
./scripts/stop_milvus.sh                    # Stop Milvus
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Container exits | Use `docker-compose up -d` |
| Connection refused | Wait 30-60s for startup |
| Out of memory | Increase Docker RAM to 8GB |
| Port in use | Stop conflicting services |
| Ollama not found | Install and run `ollama serve` |
| Model not found | Run `ollama pull llama3` |

## Getting Help

1. Check [docs/MILVUS_SETUP.md](docs/MILVUS_SETUP.md)
2. View logs: `docker-compose logs standalone`
3. Check issues on GitHub

---

**That's it! You're ready to use your RAG application with Llama3! 🚀**