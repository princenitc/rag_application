# Claude Desktop MCP Setup - Step by Step Guide

## 🎯 Important: Use Absolute Paths!

Since Claude Desktop runs as a **separate application**, it needs **absolute paths** to locate your MCP server. Relative paths will NOT work.

## 📍 Your Project Location

Your RAG application is located at:
```
/Users/prince/IKC/learning/rag_application
```

## 🔧 Step-by-Step Setup for Claude Desktop

### Step 1: Locate Claude Desktop Configuration Directory

**macOS:**
```bash
cd ~/Library/Application\ Support/Claude/
```

**Windows:**
```
%APPDATA%\Claude\
```

**Linux:**
```bash
cd ~/.config/Claude/
```

### Step 2: Create/Edit Configuration File

Create or edit the file `claude_desktop_config.json` in the Claude config directory.

**For macOS (Your System):**

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

**For Windows:**

```json
{
  "mcpServers": {
    "rag-application": {
      "command": "python",
      "args": [
        "-m",
        "src.rag_app.mcp_server"
      ],
      "cwd": "C:\\path\\to\\rag_application",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\rag_application"
      }
    }
  }
}
```

**For Linux:**

```json
{
  "mcpServers": {
    "rag-application": {
      "command": "python",
      "args": [
        "-m",
        "src.rag_app.mcp_server"
      ],
      "cwd": "/home/username/path/to/rag_application",
      "env": {
        "PYTHONPATH": "/home/username/path/to/rag_application"
      }
    }
  }
}
```

### Step 3: Understanding the Configuration

Let's break down what each field means:

```json
{
  "mcpServers": {
    "rag-application": {              // Name of your MCP server (can be anything)
      "command": "python",             // Command to run (use full path if needed)
      "args": [                        // Arguments passed to the command
        "-m",                          // Run as module
        "src.rag_app.mcp_server"       // Module path (relative to cwd)
      ],
      "cwd": "/absolute/path/here",    // ⚠️ MUST be absolute path to your project
      "env": {                         // Environment variables
        "PYTHONPATH": "/absolute/path/here"  // ⚠️ MUST be absolute path
      }
    }
  }
}
```

### Step 4: Find Your Python Path (If Needed)

If `python` command doesn't work, use the full path to Python:

**Find Python path:**
```bash
which python
# or
which python3
```

Example output: `/usr/local/bin/python3`

**Update config with full Python path:**
```json
{
  "mcpServers": {
    "rag-application": {
      "command": "/usr/local/bin/python3",  // Full path to Python
      "args": ["-m", "src.rag_app.mcp_server"],
      "cwd": "/Users/prince/IKC/learning/rag_application",
      "env": {
        "PYTHONPATH": "/Users/prince/IKC/learning/rag_application"
      }
    }
  }
}
```

### Step 5: Verify Your Paths

Before restarting Claude, verify your paths are correct:

```bash
# Check if the directory exists
ls -la /Users/prince/IKC/learning/rag_application

# Check if the MCP server file exists
ls -la /Users/prince/IKC/learning/rag_application/src/rag_app/mcp_server.py

# Test if Python can find the module
cd /Users/prince/IKC/learning/rag_application
python -m src.rag_app.mcp_server --help
```

### Step 6: Ensure Services Are Running

Before starting Claude Desktop, make sure:

**1. Milvus is running:**
```bash
docker ps | grep milvus
```

If not running:
```bash
docker run -d --name milvus_standalone \
  -p 19530:19530 -p 9091:9091 \
  milvusdb/milvus:latest
```

**2. Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If not running:
```bash
ollama serve
```

### Step 7: Restart Claude Desktop

1. **Quit Claude Desktop completely** (not just close the window)
   - macOS: `Cmd + Q`
   - Windows: Right-click taskbar icon → Quit
   - Linux: Close all windows and check system tray

2. **Start Claude Desktop again**

3. **Wait for initialization** (may take 10-30 seconds)

### Step 8: Verify Connection

Once Claude Desktop is open:

1. Look for the **🔌 tools icon** or **hammer icon** in the interface
2. Click it to see available tools
3. You should see **6 tools** from "rag-application":
   - query_rag
   - ingest_documents
   - search_documents
   - get_status
   - get_collection_stats
   - reset_collection

### Step 9: Test the Connection

Try this in Claude Desktop:

```
Use the get_status tool to check if the RAG system is working
```

Expected response:
```
**RAG System Status**

- App: RAG Application v1.0.0
- Milvus: ✅ running
- Documents indexed: 0
- Ollama: ✅ running
- LLM Model: llama3
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
```

## 🐛 Troubleshooting

### Issue 1: Tools Not Showing Up

**Check Claude Desktop Logs:**

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Windows:**
```
%APPDATA%\Claude\logs\
```

**Common fixes:**
1. Verify absolute paths are correct
2. Check Python path is correct (`which python`)
3. Ensure no typos in JSON (use a JSON validator)
4. Make sure services (Milvus, Ollama) are running

### Issue 2: "Module not found" Error

**Solution:**
```bash
# Install dependencies in the correct Python environment
cd /Users/prince/IKC/learning/rag_application
pip install -r requirements.txt

# Verify installation
python -c "import mcp; print('MCP installed')"
```

### Issue 3: Permission Denied

**Solution:**
```bash
# Make sure Python has execute permissions
chmod +x $(which python)

# Or use full path to Python in config
which python3  # Copy this path to config
```

### Issue 4: Wrong Python Environment

If you're using a virtual environment:

**Option 1: Use venv Python directly**
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

**Option 2: Activate venv in command**
```json
{
  "mcpServers": {
    "rag-application": {
      "command": "bash",
      "args": [
        "-c",
        "source venv/bin/activate && python -m src.rag_app.mcp_server"
      ],
      "cwd": "/Users/prince/IKC/learning/rag_application",
      "env": {
        "PYTHONPATH": "/Users/prince/IKC/learning/rag_application"
      }
    }
  }
}
```

## ✅ Quick Verification Checklist

Before asking Claude to use the tools:

- [ ] Absolute paths used in config (not relative)
- [ ] `claude_desktop_config.json` saved in correct location
- [ ] JSON syntax is valid (no trailing commas, proper quotes)
- [ ] Milvus is running (`docker ps | grep milvus`)
- [ ] Ollama is running (`curl http://localhost:11434/api/tags`)
- [ ] Python dependencies installed (`pip list | grep mcp`)
- [ ] Claude Desktop completely restarted
- [ ] Tools visible in Claude Desktop interface

## 📝 Example Usage After Setup

Once connected, you can use natural language:

**Ingest documents:**
```
Use the ingest_documents tool to add documents from /Users/prince/Documents/my_docs
```

**Query documents:**
```
Use the query_rag tool to ask: "What are the key features mentioned in the documents?"
```

**Check status:**
```
Use the get_status tool
```

**Search documents:**
```
Use the search_documents tool to find information about "machine learning"
```

## 🎉 Success!

If you see the tools and can use them, congratulations! Your MCP server is properly integrated with Claude Desktop.

## 📚 Additional Resources

- **Main Setup Guide:** `MCP_SETUP_GUIDE.md`
- **MCP Documentation:** `docs/MCP_SERVER.md`
- **Project README:** `README.md`

---

**Made with Bob** 🤖