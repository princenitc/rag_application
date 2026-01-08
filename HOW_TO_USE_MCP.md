# How to Use MCP Server with Claude Desktop - Complete Guide

## 🎯 Overview

This guide shows you **exactly** how to set up and use your RAG MCP server with Claude Desktop, step by step.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Claude Desktop installed
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Docker installed (for Milvus)

## 🚀 Step-by-Step Setup

### Step 1: Start Required Services

Open a terminal and run these commands:

**1.1 Start Milvus (Vector Database):**
```bash
docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest
```

**Verify Milvus is running:**
```bash
docker ps | grep milvus
```
You should see a running container.

**1.2 Start Ollama (LLM Server):**
```bash
# Start Ollama server
ollama serve
```

**In a new terminal, verify Ollama:**
```bash
curl http://localhost:11434/api/tags
```

**If you don't have a model, pull one:**
```bash
ollama pull llama3
```

### Step 2: Test Your MCP Server Locally

Before connecting to Claude, test that your MCP server works:

```bash
cd /Users/prince/IKC/learning/rag_application

# Test the server starts without errors
timeout 3 python -m src.rag_app.mcp_server
```

You should see:
```
🚀 Initializing RAG components for MCP server...
✓ Connected to Milvus
✅ RAG components initialized successfully!
🚀 Starting RAG MCP Server...
```

Press `Ctrl+C` to stop (or it will timeout after 3 seconds).

### Step 3: Configure Claude Desktop

**3.1 Find Claude Desktop config directory:**
```bash
# Navigate to Claude config directory
cd ~/Library/Application\ Support/Claude/

# List files to see if config exists
ls -la
```

**3.2 Create or edit `claude_desktop_config.json`:**

```bash
# Open in your preferred editor
nano claude_desktop_config.json
# or
code claude_desktop_config.json
# or
open -a TextEdit claude_desktop_config.json
```

**3.3 Add this exact configuration:**

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

**3.4 Save the file** (Ctrl+O in nano, Cmd+S in TextEdit)

**3.5 Verify the JSON is valid:**
```bash
# Check for syntax errors
python -m json.tool claude_desktop_config.json
```

If valid, you'll see the formatted JSON. If invalid, you'll see an error.

### Step 4: Restart Claude Desktop

**4.1 Quit Claude Desktop completely:**
- Press `Cmd + Q` (not just close the window)
- Or right-click the Claude icon in the dock → Quit

**4.2 Wait 5 seconds**

**4.3 Open Claude Desktop again**

**4.4 Wait for initialization** (10-30 seconds)

### Step 5: Verify MCP Connection

**5.1 Look for the tools indicator:**
- Look for a 🔌 **plug icon** or 🔨 **hammer icon** in the Claude interface
- Usually in the bottom-left or top-right corner
- Click it to see available tools

**5.2 You should see 6 tools:**
- ✅ query_rag
- ✅ ingest_documents
- ✅ search_documents
- ✅ get_status
- ✅ get_collection_stats
- ✅ reset_collection

**If you don't see the tools, check the troubleshooting section below.**

### Step 6: Test the Connection

In Claude Desktop, type this message:

```
Use the get_status tool to check if the RAG system is working
```

**Expected Response:**
```
**RAG System Status**

- App: RAG Application v1.0.0
- Milvus: ✅ running
- Documents indexed: 0
- Ollama: ✅ running
- LLM Model: llama3
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
```

If you see this, **congratulations!** Your MCP server is working! 🎉

## 📚 How to Use Each Tool

### Tool 1: Ingest Documents

**Purpose:** Add documents to your RAG knowledge base

**Example 1 - Ingest from a directory:**
```
Use the ingest_documents tool to add documents from /Users/prince/Documents/my_docs
```

**Example 2 - Ingest with reset:**
```
Use the ingest_documents tool with:
- directory_path: /Users/prince/Documents/research_papers
- reset_collection: true
```

**What happens:**
1. Processes all .txt, .pdf, .docx, .md files
2. Splits them into chunks
3. Generates embeddings
4. Stores in Milvus
5. Reports number of documents and chunks processed

**Response example:**
```
✅ Ingestion Complete

- Documents processed: 5
- Chunks created: 127
- Collection reset: false
```

### Tool 2: Query RAG

**Purpose:** Ask questions and get AI-generated answers from your documents

**Example 1 - Simple query:**
```
Use the query_rag tool to ask: "What are the main features of the product?"
```

**Example 2 - Query with more context:**
```
Use the query_rag tool with:
- question: "Explain the machine learning algorithms mentioned"
- top_k: 10
- show_sources: true
```

**What happens:**
1. Searches for relevant document chunks
2. Sends them to Ollama with your question
3. Generates a contextual answer
4. Returns answer with source references

**Response example:**
```
**Answer:**
The product has three main features: automated data processing, 
real-time analytics, and cloud integration. These features work 
together to provide...

**Sources (3):**
1. product_overview.pdf
2. technical_specs.docx
3. user_guide.md
```

### Tool 3: Search Documents

**Purpose:** Find relevant documents without generating an answer

**Example:**
```
Use the search_documents tool to find information about "neural networks"
```

**What happens:**
1. Searches for relevant chunks
2. Returns raw document excerpts
3. No AI generation, just retrieval

**Response example:**
```
**Search Results (5 documents):**

**1. deep_learning.pdf** (Score: 0.892)
Neural networks are computational models inspired by biological...

**2. ai_basics.txt** (Score: 0.845)
A neural network consists of layers of interconnected nodes...
```

### Tool 4: Get Status

**Purpose:** Check if all services are running

**Example:**
```
Use the get_status tool
```

**Response shows:**
- Milvus connection status
- Number of indexed documents
- Ollama availability
- Model information

### Tool 5: Get Collection Stats

**Purpose:** View statistics about your document collection

**Example:**
```
Use the get_collection_stats tool
```

**Response example:**
```
**Collection Statistics**

- Collection: rag_documents
- Total entities: 1,247
```

### Tool 6: Reset Collection

**Purpose:** Delete all documents from the collection

**⚠️ WARNING:** This is irreversible!

**Example:**
```
Use the reset_collection tool with confirm: true
```

**Response:**
```
✅ Collection has been reset. All documents have been removed.
```

## 🎓 Complete Workflow Example

Here's a complete workflow from start to finish:

### Scenario: Building a Knowledge Base from Research Papers

**Step 1: Check system status**
```
Use the get_status tool
```

**Step 2: Ingest your documents**
```
Use the ingest_documents tool to add documents from /Users/prince/Documents/research_papers
```

**Step 3: Verify ingestion**
```
Use the get_collection_stats tool
```

**Step 4: Ask questions**
```
Use the query_rag tool to ask: "What are the key findings about climate change in these papers?"
```

**Step 5: Search for specific topics**
```
Use the search_documents tool to find information about "carbon emissions"
```

**Step 6: Ask follow-up questions**
```
Use the query_rag tool to ask: "What solutions are proposed for reducing emissions?"
```

## 🐛 Troubleshooting

### Problem: Tools Don't Appear in Claude Desktop

**Solution 1: Check Claude Desktop Logs**
```bash
# View logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

Look for errors related to "rag-application"

**Solution 2: Verify Configuration**
```bash
# Check config file exists
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Validate JSON
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Solution 3: Verify Services**
```bash
# Check Milvus
docker ps | grep milvus

# Check Ollama
curl http://localhost:11434/api/tags

# Test MCP server manually
cd /Users/prince/IKC/learning/rag_application
python -m src.rag_app.mcp_server
```

**Solution 4: Restart Everything**
```bash
# Restart Milvus
docker restart milvus_standalone

# Restart Ollama (if running as service)
# Otherwise, just run: ollama serve

# Quit and restart Claude Desktop
```

### Problem: "Module not found" Error

**Solution:**
```bash
cd /Users/prince/IKC/learning/rag_application
pip install -r requirements.txt

# Verify MCP is installed
python -c "import mcp; print('MCP installed')"
```

### Problem: Connection Timeout

**Solution:**
```bash
# Check if Milvus is accessible
curl http://localhost:9091/healthz

# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# Increase timeout in config (if needed)
```

### Problem: Wrong Python Environment

If you're using a virtual environment:

**Update config to use venv Python:**
```json
{
  "mcpServers": {
    "rag-application": {
      "command": "/Users/prince/IKC/learning/rag_application/venv/bin/python",
      "args": ["-m", "src.rag_app.mcp_server"],
      "cwd": "/Users/prince/IKC/learning/rag_application",
      "env": {
        "PYTHONPATH": "/Users/prince/IKC/learning/rag_application"
      }
    }
  }
}
```

## 💡 Pro Tips

### Tip 1: Keep Services Running
Create a startup script to launch services automatically:

```bash
#!/bin/bash
# save as start_rag_services.sh

# Start Milvus
docker start milvus_standalone || docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest

# Start Ollama
ollama serve &

echo "✅ Services started!"
```

### Tip 2: Organize Your Documents
```bash
# Create a documents directory
mkdir -p ~/Documents/rag_docs

# Organize by topic
mkdir -p ~/Documents/rag_docs/research
mkdir -p ~/Documents/rag_docs/manuals
mkdir -p ~/Documents/rag_docs/notes
```

### Tip 3: Use Descriptive Queries
Instead of: "What is this about?"
Use: "What are the main features of the authentication system described in the documentation?"

### Tip 4: Adjust top_k for Better Results
- Use `top_k: 3` for focused, specific answers
- Use `top_k: 10` for comprehensive, detailed answers

### Tip 5: Monitor Your Collection
Regularly check stats to know what's indexed:
```
Use the get_collection_stats tool
```

## 📊 Usage Patterns

### Pattern 1: Research Assistant
```
1. Ingest research papers
2. Ask: "Summarize the key findings"
3. Ask: "What methodologies were used?"
4. Ask: "What are the limitations mentioned?"
```

### Pattern 2: Documentation Helper
```
1. Ingest product documentation
2. Ask: "How do I configure authentication?"
3. Ask: "What are the API endpoints?"
4. Search: "error handling"
```

### Pattern 3: Knowledge Base
```
1. Ingest company documents
2. Ask: "What is our policy on remote work?"
3. Ask: "What are the benefits offered?"
4. Search: "vacation policy"
```

## ✅ Success Checklist

- [ ] Milvus running (`docker ps | grep milvus`)
- [ ] Ollama running (`curl http://localhost:11434/api/tags`)
- [ ] Config file created with absolute paths
- [ ] Claude Desktop restarted
- [ ] Tools visible in Claude Desktop
- [ ] `get_status` tool works
- [ ] Documents ingested successfully
- [ ] Queries return relevant answers

## 🎉 You're Ready!

If you've completed all steps and the checklist, you're ready to use your RAG system through Claude Desktop!

Try asking Claude:
```
Use the query_rag tool to ask: "What can you tell me about the documents I've ingested?"
```

---

**Need more help?** Check:
- `CLAUDE_DESKTOP_SETUP.md` - Detailed setup guide
- `MCP_SETUP_GUIDE.md` - General MCP information
- `docs/MCP_SERVER.md` - Technical documentation

**Made with Bob** 🤖