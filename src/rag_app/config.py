"""
Configuration file for RAG application
Uses TOML configuration via config_loader
"""
from .config_loader import get_config

# Load configuration
_cfg = get_config()

# Milvus Configuration
MILVUS_HOST = _cfg.milvus['host']
MILVUS_PORT = str(_cfg.milvus['port'])
COLLECTION_NAME = _cfg.milvus['collection_name']

# Embedding Configuration
EMBEDDING_MODEL = _cfg.embedding['model']
EMBEDDING_DIMENSION = _cfg.embedding['dimension']

# Ollama Configuration
OLLAMA_BASE_URL = _cfg.ollama['base_url']
OLLAMA_MODEL = _cfg.ollama['model']

# Document Processing Configuration
CHUNK_SIZE = _cfg.document_processing['chunk_size']
CHUNK_OVERLAP = _cfg.document_processing['chunk_overlap']
SUPPORTED_EXTENSIONS = _cfg.document_processing['supported_extensions']

# Retrieval Configuration
TOP_K = _cfg.retrieval['top_k']
SIMILARITY_THRESHOLD = _cfg.retrieval['similarity_threshold']

# Application Settings
DATA_DIR = _cfg.paths['data_dir']

# Made with Bob
