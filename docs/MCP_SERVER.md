# MCP Server Documentation

## Overview

The RAG Application now includes a Model Context Protocol (MCP) server that exposes RAG functionality through a standardized interface. This allows AI assistants and other MCP clients to interact with your RAG system programmatically.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It enables seamless integration between AI assistants and various data sources and tools.

## Features

The MCP server provides the following tools:

### 1. **query_rag**
Query the RAG system with a question and get an AI-generated answer based on indexed documents.

**Parameters:**
- `question` (required): The question to ask
- `top_k` (optional): Number of relevant documents to retrieve (default: 5)
- `show_sources` (optional): Include source documents in response (default: true)

**Example:**
```json
{
  "question": "What is machine learning?",
  "top_k": 3,
  "show_sources": true
}
```

### 2. **ingest_documents**
Ingest documents from a directory into the RAG system.

**Parameters:**
- `directory_path` (required): Path to directory containing documents
- `reset_collection` (optional): Reset collection before ingesting (default: false)

**Example:**
```json
{
  "directory_path": "./data/documents",
  "reset_collection": false
}
```

### 3. **get_status**
Get the current status of the RAG system.

**Returns:**
- Application version
- Milvus status and document count
- Ollama status and model information
- Embedding model information

### 4. **search_documents**
Search for relevant documents without generating an answer.

**Parameters:**
- `query` (required): The search query
- `top_k` (optional): Number of documents to retrieve (default: 5)

### 5. **get_collection_stats**
Get statistics about the document collection.

**Returns:**
- Collection name
- Total number of entities/chunks

### 6. **reset_collection**
Reset the Milvus collection (removes all documents).

**Parameters:**
- `confirm` (required): Must be true to proceed

**⚠️ Warning:** This operation is irreversible!

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the `mcp` package along with other dependencies.

### 2. Verify Installation

```bash
python -c "import mcp; print('MCP installed successfully')"
```

## Configuration

### MCP Configuration File

The `mcp_config.json` file configures how MCP clients connect to the server:

```json
{
  "mcpServers": {
    "rag-application": {
      "command": "python",
      "args": [
        "-m",
        "src.rag_app.mcp_server"
      ],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### Application Configuration

The MCP server uses the same `config.toml` file as the main application. Ensure your configuration is properly set up:

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
```

## Running the MCP Server

### Method 1: Direct Execution

```bash
python -m src.rag_app.mcp_server
```

### Method 2: Using MCP Client

If you're using Claude Desktop or another MCP-compatible client:

1. Copy `mcp_config.json` to your MCP client's configuration directory
2. Restart the client
3. The RAG server will be available as a tool

### Method 3: Programmatic Usage

```python
from src.rag_app.mcp_server import run_mcp_server

# Run the server
run_mcp_server()
```

## Usage Examples

### Example 1: Query the RAG System

Using an MCP client (like Claude Desktop):

```
Use the query_rag tool to ask: "What are the main features of the product?"
```

The assistant will:
1. Search for relevant documents
2. Generate a contextual answer
3. Provide source references

### Example 2: Ingest Documents

```
Use the ingest_documents tool with directory_path: "./data/new_docs"
```

This will:
1. Process all supported documents in the directory
2. Generate embeddings
3. Index them in Milvus

### Example 3: Check System Status

```
Use the get_status tool to check if the system is running properly
```

Returns:
- Milvus connectivity
- Ollama availability
- Document count
- Model information

## Integration with Claude Desktop

### Setup Steps

1. **Locate Claude Desktop Config Directory:**
   - macOS: `~/Library/Application Support/Claude/`
   - Windows: `%APPDATA%\Claude\`
   - Linux: `~/.config/Claude/`

2. **Add MCP Server Configuration:**

Create or edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-application": {
      "command": "python",
      "args": [
        "-m",
        "src.rag_app.mcp_server"
      ],
      "cwd": "/path/to/your/rag_application",
      "env": {
        "PYTHONPATH": "/path/to/your/rag_application"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Verify Connection:**
   - Open Claude Desktop
   - Look for the RAG tools in the available tools list
   - Try querying your documents

## Troubleshooting

### Server Won't Start

**Issue:** MCP server fails to start

**Solutions:**
1. Check if Milvus is running:
   ```bash
   docker ps | grep milvus
   ```

2. Verify Ollama is accessible:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Check Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Connection Errors

**Issue:** MCP client can't connect to server

**Solutions:**
1. Verify the working directory in config is correct
2. Check PYTHONPATH is set properly
3. Ensure no firewall is blocking the connection

### No Documents Found

**Issue:** Queries return no results

**Solutions:**
1. Check if documents are ingested:
   ```python
   # Use get_collection_stats tool
   ```

2. Verify document format is supported (.txt, .pdf, .docx, .md)

3. Re-ingest documents with reset_collection=true

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
pip install mcp>=1.0.0
```

## Best Practices

### 1. Document Organization
- Keep documents in organized directories
- Use descriptive filenames
- Maintain consistent formatting

### 2. Query Optimization
- Be specific in your questions
- Adjust `top_k` based on your needs
- Use `show_sources` to verify answers

### 3. Collection Management
- Regularly check collection stats
- Reset collection when updating document corpus
- Monitor Milvus storage usage

### 4. Performance
- Batch document ingestion when possible
- Use appropriate chunk sizes in config.toml
- Monitor embedding generation time

## Security Considerations

1. **Access Control:** The MCP server runs locally and doesn't include authentication. Ensure it's not exposed to untrusted networks.

2. **Data Privacy:** Documents are stored in Milvus and processed by Ollama locally. No data is sent to external services.

3. **File System Access:** The server can read files from specified directories. Ensure proper file permissions.

## Advanced Usage

### Custom Tool Integration

You can extend the MCP server with custom tools by modifying `src/rag_app/mcp_server.py`:

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="custom_tool",
            description="Your custom tool description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        )
    ]
```

### Monitoring and Logging

Enable detailed logging by modifying the server:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## API Reference

For detailed API documentation of the RAG components, see:
- [API Documentation](./API_DOCUMENTATION.md)
- [Project Structure](./PROJECT_STRUCTURE.md)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the main [README.md](../README.md)
3. Check Milvus and Ollama documentation

## License

This MCP server implementation is part of the RAG Application and follows the same license.

---

**Made with Bob** 🤖