# Quick Start - MCP with Claude Desktop (5 Minutes)

## 🚀 Super Quick Setup

### 1. Start Services (2 minutes)

```bash
# Terminal 1: Start Milvus
docker run -d --name milvus_standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest

# Terminal 2: Start Ollama
ollama serve
```

### 2. Configure Claude Desktop (1 minute)

```bash
# Open config file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Paste this (use YOUR actual path):**
```json
{
  "mcpServers": {
    "rag-application": {
      "command": "python",
      "args": ["-m", "src.rag_app.mcp_server"],
      "cwd": "/Users/prince/IKC/learning/rag_application",
      "env": {
        "PYTHONPATH": "/Users/prince/IKC/learning/rag_application"
      }
    }
  }
}
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 3. Restart Claude Desktop (1 minute)

1. Press `Cmd + Q` to quit Claude
2. Wait 5 seconds
3. Open Claude Desktop again
4. Look for 🔌 or 🔨 icon

### 4. Test It! (1 minute)

In Claude Desktop, type:
```
Use the get_status tool
```

**If you see status info → SUCCESS! ✅**

## 📝 First Use Example

### Add Documents:
```
Use the ingest_documents tool to add documents from /Users/prince/Documents/my_docs
```

### Ask Questions:
```
Use the query_rag tool to ask: "What are the main topics in my documents?"
```

## 🐛 Not Working?

**Check services:**
```bash
docker ps | grep milvus          # Should show running container
curl http://localhost:11434/api/tags  # Should return JSON
```

**Check config:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**View logs:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

## 📚 Full Guides

- **Complete Usage Guide:** `HOW_TO_USE_MCP.md`
- **Detailed Setup:** `CLAUDE_DESKTOP_SETUP.md`
- **General Info:** `MCP_SETUP_GUIDE.md`

---

**That's it! You're ready to use RAG with Claude Desktop! 🎉**