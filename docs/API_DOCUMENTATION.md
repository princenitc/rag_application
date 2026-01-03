# RAG Application API Documentation

Complete API documentation for the RAG Application server.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. Add authentication middleware for production use.

## Endpoints

### Health & Status

#### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "message": "RAG Application API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET `/status`
Get system status including Milvus and Ollama.

**Response:**
```json
{
  "app_name": "RAG Application",
  "version": "1.0.0",
  "milvus_status": "running",
  "milvus_documents": 150,
  "ollama_status": "running",
  "ollama_model": "llama3",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### Query

#### POST `/query`
Query the RAG system with a question.

**Request Body:**
```json
{
  "question": "What is machine learning?",
  "top_k": 5,
  "stream": false
}
```

**Response:**
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is...",
  "sources": ["doc1.pdf", "doc2.txt"],
  "num_sources": 2
}
```

#### POST `/query/stream`
Query with streaming response (Server-Sent Events).

**Request Body:**
```json
{
  "question": "Explain neural networks",
  "top_k": 5
}
```

**Response:** Stream of events
```
data: {"content": "Neural"}
data: {"content": " networks"}
data: {"content": " are..."}
data: {"sources": ["doc1.pdf"], "done": true}
```

### Document Management

#### POST `/documents/upload`
Upload a document.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF, DOCX, TXT, or MD)

**Response:**
```json
{
  "filename": "document.pdf",
  "size": 1024000,
  "type": ".pdf"
}
```

#### GET `/documents`
List all uploaded documents.

**Response:**
```json
[
  {
    "filename": "document.pdf",
    "size": 1024000,
    "type": ".pdf"
  }
]
```

#### DELETE `/documents/{filename}`
Delete an uploaded document.

**Response:**
```json
{
  "message": "Document document.pdf deleted"
}
```

#### POST `/documents/ingest`
Ingest uploaded documents into the system.

**Request Body:**
```json
{
  "reset": false
}
```

**Response:**
```json
{
  "status": "success",
  "num_chunks": 150,
  "num_documents": 5,
  "message": "Successfully ingested 5 documents (150 chunks)"
}
```

### Collection Management

#### GET `/collection/stats`
Get collection statistics.

**Response:**
```json
{
  "name": "rag_documents",
  "num_entities": 150,
  "dimension": 384
}
```

#### POST `/collection/reset`
Reset the Milvus collection (deletes all data).

**Response:**
```json
{
  "message": "Collection reset successfully"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.
Visit `/redoc` for ReDoc documentation.

## Example Usage

### Python

```python
import requests

# Query
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is AI?", "top_k": 5}
)
print(response.json())

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/documents/upload",
        files={"file": f}
    )
print(response.json())

# Ingest documents
response = requests.post(
    "http://localhost:8000/documents/ingest",
    json={"reset": False}
)
print(response.json())
```

### cURL

```bash
# Query
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

# Get status
curl "http://localhost:8000/status"
```

### JavaScript/Fetch

```javascript
// Query
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: 'What is AI?',
    top_k: 5
  })
});
const data = await response.json();
console.log(data);

// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/documents/upload', {
  method: 'POST',
  body: formData
});
```

## Streaming Example

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/query/stream",
    json={"question": "Explain AI", "top_k": 5},
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'content' in data:
                print(data['content'], end='', flush=True)
            elif 'done' in data:
                print(f"\n\nSources: {data['sources']}")
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## CORS

CORS is not configured by default. Add CORS middleware if needed:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Considerations

1. **Authentication**: Add API key or OAuth authentication
2. **Rate Limiting**: Implement rate limiting per user/IP
3. **CORS**: Configure appropriate CORS settings
4. **HTTPS**: Use HTTPS in production
5. **Monitoring**: Add logging and monitoring
6. **Scaling**: Use multiple workers with Gunicorn
7. **Caching**: Implement caching for frequent queries