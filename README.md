# RAG Backend API

A production-ready RAG (Retrieval-Augmented Generation) backend system built with FastAPI, PydanticAI, LangChain, and LangGraph.

## Features

- **Document Ingestion**: Upload and process PDF, TXT, and DOCX files
- **RAG Query/Chat**: Query documents with grounded answer generation
- **Intelligent Processing**: PydanticAI agents orchestrate workflows
- **Vector Embeddings**: OpenAI text-embedding-3-small (with local fallback)
- **Persistent Storage**: ChromaDB (local or cloud-hosted)
- **Async-First**: Fully async for high performance
- **Production Ready**: Comprehensive error handling, logging, and validation

## Architecture

### Components

1. **FastAPI Layer** (`app/api/`): HTTP endpoints and middleware
2. **Agent Layer** (`app/agents/`): PydanticAI agents (ingestion + query)
3. **RAG Pipeline** (`app/rag/`): LangGraph workflows with loaders, splitters, embeddings, and storage
4. **Service Layer** (`app/services/`): Business logic orchestration
5. **Core** (`app/core/`): Configuration, errors, logging, constants

### Data Flow

```
Client Upload
    ↓
FastAPI Endpoint
    ↓
UploadService (validation, save files)
    ↓
PydanticAI Ingestion Agent
    ↓
LangGraph Pipeline:
    - Load Document (PDF/TXT/DOCX)
    - Split into Chunks
    - Generate Embeddings (OpenAI)
    - Store in ChromaDB
    ↓
Cleanup Temp Files
    ↓
Return Results to Client
```

## Installation

### Prerequisites

- Python 3.10 - 3.13 (Python 3.14+ not supported due to ChromaDB compatibility)
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rag_agent
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### Upload Endpoint

**POST** `/api/v1/upload`

Upload and process documents for the RAG system.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form field `files` with one or more files

**Response:**
```json
{
  "success": true,
  "files_processed": 1,
  "chunks_created": 42,
  "message": "Successfully processed 1/1 files",
  "details": [
    {
      "filename": "document.pdf",
      "file_size_bytes": 152048,
      "chunks_created": 42,
      "processing_time_ms": 3542.8,
      "status": "success",
      "error": null
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "files=@document.pdf" \
  -H "Content-Type: multipart/form-data"
```

### Chat Endpoint

**POST** `/api/v1/chat`

Query documents with RAG (Retrieval-Augmented Generation). Generates grounded answers based only on retrieved document chunks.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "query": "What is machine learning?",
  "top_k": 5,
  "session_id": "optional-session-id",
  "filter_metadata": {"source_type": "pdf"}
}
```

**Parameters:**
- `query` (string, required): User question (1-2000 characters)
- `top_k` (integer, optional): Number of chunks to retrieve (1-20, default: 5)
- `session_id` (string, optional): Session ID for conversation tracking
- `filter_metadata` (object, optional): Metadata filters for retrieval

**Response:**
```json
{
  "success": true,
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": ["ml_intro.pdf", "ai_handbook.txt"],
  "retrieved_chunks": [
    {
      "chunk_id": "abc123",
      "document_id": "def456",
      "content": "Machine learning is a subset of artificial intelligence...",
      "chunk_index": 0,
      "filename": "ml_intro.pdf",
      "source_type": "pdf",
      "similarity_score": null
    }
  ],
  "query_time_ms": 250.5,
  "session_id": "optional-session-id",
  "error": null
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'
```

**Key Features:**
- Grounded answers based ONLY on retrieved context
- Source attribution (cites document names)
- Handles missing information gracefully
- Low temperature (0.0) for factual responses
- Returns retrieved chunks for transparency

### Health Check

**GET** `/api/v1/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-05T12:00:00Z"
}
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key

**Optional (with defaults):**
- `MAX_FILE_SIZE_MB`: Maximum file size (default: 10)
- `MAX_FILES_PER_REQUEST`: Maximum files per upload (default: 10)
- `CHUNK_SIZE`: Text chunk size in characters (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap in characters (default: 200)
- `EMBEDDING_PROVIDER`: "openai" or "local" (default: "openai")
- `VECTOR_STORE`: "chroma_local", "chroma_cloud", or "memory" (default: "chroma_local")
- `QUERY_LLM_MODEL`: LLM for answer generation (default: "gpt-4o-mini")
- `QUERY_TOP_K`: Default number of chunks to retrieve (default: 5)
- `QUERY_TEMPERATURE`: LLM temperature for grounded responses (default: 0.0)
- `QUERY_MAX_CONTEXT_LENGTH`: Maximum context length in characters (default: 4000)

### Vector Storage Options

The system supports three vector storage backends:

#### 1. Local ChromaDB (Default)
Stores vectors locally in the `data/vector_store/` directory. Best for development and testing.

**Configuration:**
```bash
VECTOR_STORE="chroma_local"
CHROMA_COLLECTION_NAME="documents"
```

**Pros:**
- No external dependencies
- Fast local access
- Free and unlimited
- Full control over data

**Cons:**
- Single machine only
- Manual backups required
- Scaling limitations

#### 2. Chroma Cloud
Managed vector database service hosted by Chroma. Best for production deployments.

**Configuration:**
```bash
VECTOR_STORE="chroma_cloud"
CHROMA_CLOUD_API_KEY="your-api-key-here"
CHROMA_CLOUD_HOST="api.trychroma.com"
CHROMA_CLOUD_PORT=443
CHROMA_COLLECTION_NAME="documents"

# Optional: Multi-tenancy support
CHROMA_CLOUD_TENANT="your-tenant"
CHROMA_CLOUD_DATABASE="your-database"
```

**Setup:**
1. Create account at [https://trychroma.com](https://trychroma.com)
2. Generate API key from dashboard
3. Add API key to `.env` file
4. Set `VECTOR_STORE="chroma_cloud"`

**Pros:**
- Managed infrastructure
- Automatic backups
- Scalable and distributed
- High availability

**Cons:**
- Requires account and API key
- Usage-based pricing
- Network latency

#### 3. In-Memory Storage
Stores vectors in memory. For testing only - data is not persisted.

**Configuration:**
```bash
VECTOR_STORE="memory"
```

**Use Case:**
- Unit tests
- Integration tests
- Quick prototyping

### Migrating from Local to Cloud

If you're currently using local ChromaDB and want to migrate to Chroma Cloud:

1. Update `.env`:
```bash
# Change from:
VECTOR_STORE="chroma"  # or "chroma_local"

# To:
VECTOR_STORE="chroma_cloud"
CHROMA_CLOUD_API_KEY="your-api-key"
```

2. Re-upload your documents to populate the cloud database
3. Your local data in `data/vector_store/` will remain unchanged

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_upload.py -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/
```

## Project Structure

```
rag_agent/
├── app/
│   ├── api/              # FastAPI routes and middleware
│   ├── agents/           # PydanticAI agents
│   ├── core/             # Configuration and errors
│   ├── models/           # Pydantic models
│   ├── rag/              # RAG components
│   │   ├── loaders/      # Document loaders
│   │   ├── splitters/    # Text splitters
│   │   ├── embeddings/   # Embedding layer
│   │   ├── storage/      # Vector stores
│   │   ├── pipelines/    # Processing pipelines
│   │   └── graphs/       # LangGraph workflows
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── tests/                # Test suite
├── data/                 # Data storage (gitignored)
├── main.py               # Application entry point
└── requirements.txt      # Dependencies
```

## Supported File Types

- **PDF** (.pdf): Parsed with PyMuPDF
- **Text** (.txt): Plain text with encoding detection
- **Word** (.docx): Parsed with python-docx

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
