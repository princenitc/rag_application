# MCP Server Setup Guide for RAG Application

## ✅ Current Status

Your RAG application now has a **fully functional MCP (Model Context Protocol) server** implementation! This guide will help you set it up and use it with AI assistants like Claude Desktop.

## 🎯 What's Already Implemented

Your MCP server provides 6 powerful tools:

1. **query_rag** - Ask questions and get AI-generated answers from your documents
2. **ingest_documents** - Add new documents to the knowledge base
3. **search_documents** - Search for relevant documents without generating answers
4. **get_status** - Check system health (Milvus, Ollama, document count)
5. **get_collection_stats** - View collection statistics
6. **reset_collection** - Clear all documents (with confirmation)

## 📋 Prerequisites

Before using the MCP server, ensure you have:

- ✅ Python 3.8+ installed
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ Milvus running (for vector storage)
- ✅ Ollama running with a model (e.g., llama3)

## 🚀 Quick Start

### Step 1: Verify Installation

```bash
# Check if MCP is installed
python -c "import mcp.server; print('✅ MCP installed')"

# Check if all dependencies are available
python -c "from src.rag_app.mcp_server import app; print('✅ MCP server ready')"
```

### Step 2: Start Required Services

**Start Milvus:**
```bash
docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest
```

**Start Ollama:**
```bash
# If not already running
ollama serve

# Pull a model if needed
ollama pull llama3
```

### Step 3: Test the MCP Server

```bash
# Run the MCP server (it will wait for stdio input)
python -m src.rag_app.mcp_server
```

The server will initialize and display:
```
🚀 Initializing RAG components for MCP server...
✓ Connected to Milvus
✅ RAG components initialized successfully!
🚀 Starting RAG MCP Server...
```

## 🔌 Integration with Claude Desktop

### ⚠️ IMPORTANT: Use Absolute Paths!

Claude Desktop runs as a **separate application**, so it needs **absolute paths** (not relative paths) to find your MCP server.

### macOS Setup (Your System)

1. **Locate Claude Desktop Config:**
   ```bash
   cd ~/Library/Application\ Support/Claude/
   ```

2. **Create or Edit `claude_desktop_config.json`:**
   
   **Use ABSOLUTE paths:**
   ```json
   {
     "mcpServers": {
       "rag-application": {
         "command": "python",
         "args": [
           "-m",
           "src.rag_app.mcp_server"
         ],
         "cwd": "/Users/prince/IKC/learning/rag_application",
         "env": {
           "PYTHONPATH": "/Users/prince/IKC/learning/rag_application"
         }
       }
     }
   }
   ```
   
   **Note:** Replace `/Users/prince/IKC/learning/rag_application` with your actual project path if different.

3. **Verify Your Paths:**
   ```bash
   # Check if directory exists
   ls -la /Users/prince/IKC/learning/rag_application
   
   # Check if MCP server exists
   ls -la /Users/prince/IKC/learning/rag_application/src/rag_app/mcp_server.py
   ```

4. **Restart Claude Desktop** (Quit completely with Cmd+Q, then reopen)

5. **Verify Connection:**
   - Open Claude Desktop
   - Look for the 🔌 icon or tools menu
   - You should see "rag-application" with 6 available tools

### Windows Setup

1. **Config Location:** `%APPDATA%\Claude\claude_desktop_config.json`

2. **Use ABSOLUTE paths in config:**
   ```json
   {
     "mcpServers": {
       "rag-application": {
         "command": "python",
         "args": ["-m", "src.rag_app.mcp_server"],
         "cwd": "C:\\Users\\YourUsername\\path\\to\\rag_application",
         "env": {
           "PYTHONPATH": "C:\\Users\\YourUsername\\path\\to\\rag_application"
         }
       }
     }
   }
   ```
   
   **Note:** Use double backslashes `\\` in Windows paths.

### Linux Setup

1. **Config Location:** `~/.config/Claude/claude_desktop_config.json`

2. **Use ABSOLUTE paths in config:**
   ```json
   {
     "mcpServers": {
       "rag-application": {
         "command": "python",
         "args": ["-m", "src.rag_app.mcp_server"],
         "cwd": "/home/username/path/to/rag_application",
         "env": {
           "PYTHONPATH": "/home/username/path/to/rag_application"
         }
       }
     }
   }
   ```

### 📖 Detailed Setup Guide

For a comprehensive step-by-step guide with troubleshooting, see:
**[CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)**

## 💡 Usage Examples

### Example 1: Ingest Documents

In Claude Desktop, you can say:

```
Use the ingest_documents tool to add documents from ./data/my_documents
```

Claude will:
1. Process all supported files (.txt, .pdf, .docx, .md)
2. Generate embeddings
3. Store them in Milvus
4. Report the number of documents and chunks processed

### Example 2: Query Your Documents

```
Use the query_rag tool to ask: "What are the main features of the product?"
```

Claude will:
1. Search for relevant document chunks
2. Generate a contextual answer using Ollama
3. Provide source references

### Example 3: Check System Status

```
Use the get_status tool to check if everything is running
```

Returns:
- Milvus connection status
- Number of indexed documents
- Ollama availability
- Model information

### Example 4: Search Without Generating Answer

```
Use the search_documents tool to find information about "machine learning"
```

Returns raw document chunks matching your query.

## 🛠️ Configuration

Your MCP server uses `config.toml` for settings:

```toml
[milvus]
host = "localhost"
port = 19530
collection_name = "rag_documents"

[ollama]
base_url = "http://localhost:11434"
model = "llama3"

[embedding]
model = "sentence-transformers/all-MiniLM-L6-v2"
dimension = 384

[document_processing]
chunk_size = 1000
chunk_overlap = 200
```

## 🔍 Troubleshooting

### Issue: MCP Server Won't Start

**Solution:**
```bash
# Check if Milvus is running
docker ps | grep milvus

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Verify Python dependencies
pip install -r requirements.txt
```

### Issue: Claude Desktop Can't Connect

**Solutions:**
1. Verify the `cwd` path in config is correct
2. Ensure PYTHONPATH is set correctly
3. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### Issue: "No module named 'mcp'"

**Solution:**
```bash
pip install mcp>=1.0.0
```

### Issue: Import Errors

**Solution:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Testing the MCP Server

### Test 1: Verify Tools Are Listed

Create a test script `test_mcp.py`:

```python
import asyncio
from src.rag_app.mcp_server import app

async def test_tools():
    tools = await app.list_tools()
    print(f"✅ Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

asyncio.run(test_tools())
```

Run it:
```bash
python test_mcp.py
```

### Test 2: Check Status Tool

Once connected to Claude Desktop:
```
Use the get_status tool
```

Expected output:
```
**RAG System Status**

- App: RAG Application v1.0.0
- Milvus: ✅ running
- Documents indexed: 0
- Ollama: ✅ running
- LLM Model: llama3
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
```

## 🎓 Advanced Usage

### Custom Tool Integration

You can extend the MCP server by adding custom tools in `src/rag_app/mcp_server.py`:

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="custom_analysis",
            description="Perform custom analysis on documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string"}
                }
            }
        )
    ]
```

### Monitoring and Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server.log'
)
```

## 📚 Additional Resources

- **MCP Documentation:** [docs/MCP_SERVER.md](docs/MCP_SERVER.md)
- **API Documentation:** [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Project Structure:** [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- **Milvus Setup:** [docs/MILVUS_SETUP.md](docs/MILVUS_SETUP.md)

## 🎉 Success Checklist

- [ ] Dependencies installed
- [ ] Milvus running
- [ ] Ollama running with a model
- [ ] MCP server starts without errors
- [ ] Claude Desktop config updated
- [ ] Tools visible in Claude Desktop
- [ ] Successfully ingested test documents
- [ ] Successfully queried documents

## 🤝 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in `mcp_server.log`
3. Verify all services are running
4. Check the configuration in `config.toml`

## 🎯 Next Steps

1. **Ingest Your Documents:**
   ```bash
   # Via CLI
   python main.py cli ingest ./your_documents/
   
   # Or via MCP in Claude Desktop
   "Use ingest_documents tool with ./your_documents/"
   ```

2. **Start Querying:**
   ```
   "Use query_rag to ask: What is [your topic]?"
   ```

3. **Explore Advanced Features:**
   - Try different top_k values for retrieval
   - Experiment with different Ollama models
   - Adjust chunk sizes in config.toml

---

**Your MCP server is ready to use! 🚀**

Made with Bob 🤖