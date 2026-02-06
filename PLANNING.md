# RAG Backend - Architecture & Planning

## Overview

This document describes the architecture, design decisions, and extension guidelines for the RAG Backend system.

## System Architecture

### High-Level Design

The RAG Backend is built with a modular, layered architecture:

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│  (Routing, Middleware, Dependency Injection)    │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│              Service Layer                      │
│  (Business Logic, Orchestration)                │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│           PydanticAI Agent Layer                │
│  (Intelligent Orchestration, Error Handling)    │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│          LangGraph Workflow Engine              │
│  (State Management, Node Execution)             │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│            RAG Components                       │
│  (Loaders, Splitters, Embeddings, Storage)      │
└─────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Layer (`app/api/`)

**Purpose**: HTTP interface and request handling

**Components**:
- `routes.py`: API router registration
- `upload.py`: Document upload endpoint
- `dependencies.py`: Dependency injection
- `middleware.py`: Error handling and logging

**Design Decisions**:
- Async-first for high concurrency
- Dependency injection for testability
- Custom middleware for consistent error responses
- OpenAPI documentation auto-generated

### 2. Service Layer (`app/services/`)

**Purpose**: Business logic orchestration

**Components**:
- `upload_service.py`: Upload workflow orchestration
- `file_service.py`: File operations (save, cleanup, hash)
- `validation_service.py`: File validation logic

**Design Decisions**:
- Single Responsibility Principle
- Services compose lower-level components
- No business logic in endpoints
- Always cleanup temp files in finally block

### 3. PydanticAI Agent (`app/agents/ingestion/`)

**Purpose**: Intelligent orchestration of document processing

**Components**:
- `agent.py`: Main agent with PydanticAI
- `tools.py`: Agent tools for validation and processing
- `prompts.py`: System prompts and instructions

**Design Decisions**:
- Agent wraps LangGraph pipeline
- Provides natural language error messages
- Tool-based architecture for extensibility
- Easy to add new processing capabilities

### 4. LangGraph Workflow (`app/rag/graphs/`, `app/rag/pipelines/`)

**Purpose**: State-managed document processing workflow

**Components**:
- `state.py`: TypedDict state definition
- `nodes.py`: Workflow node functions
- `ingestion_graph.py`: Graph builder
- `pipelines/ingestion.py`: Pipeline wrapper

**Design Decisions**:
- Explicit state management
- Each node is a pure function with dependencies injected
- Linear workflow: load → split → embed → store
- Easy to add conditional branching or parallel processing

### 5. RAG Components (`app/rag/`)

#### Document Loaders (`app/rag/loaders/`)

**Purpose**: Load and parse various document formats

**Pattern**: Factory pattern with abstract base class

**Implementations**:
- `pdf.py`: PyMuPDF-based PDF loader
- `txt.py`: Text file loader with encoding detection
- `docx.py`: python-docx-based DOCX loader

**Extension**: Implement `BaseDocumentLoader` and register in `DocumentLoaderFactory`

#### Text Splitters (`app/rag/splitters/`)

**Purpose**: Split documents into chunks for embedding

**Pattern**: Strategy pattern with configuration

**Implementations**:
- `recursive.py`: Recursive character splitter (wraps LangChain)

**Configuration**: `SplitterConfig` (chunk_size, chunk_overlap, separators)

**Extension**: Implement `BaseTextSplitter` for custom splitting logic

#### Embeddings (`app/rag/embeddings/`)

**Purpose**: Generate vector embeddings for text

**Pattern**: Abstract interface with multiple providers

**Implementations**:
- `openai.py`: OpenAI text-embedding-3-small (DEFAULT)
- `local.py`: Sentence-transformers (fallback)

**Extension**: Implement `BaseEmbedder` and add to `EmbedderFactory`

#### Vector Storage (`app/rag/storage/`)

**Purpose**: Store and retrieve embedded chunks

**Pattern**: Repository pattern with abstract interface

**Implementations**:
- `chroma.py`: ChromaDB local persistent storage (DEFAULT)
- `chroma_cloud.py`: Chroma Cloud hosted storage
- `memory.py`: In-memory storage for testing

**Extension**: Implement `BaseVectorStore` and add to `VectorStoreFactory`

**Chroma Cloud Setup**:
1. Create account at https://trychroma.com
2. Generate API key from dashboard
3. Set environment variables:
   - `VECTOR_STORE="chroma_cloud"`
   - `CHROMA_CLOUD_API_KEY="your-key"`
4. Optionally configure tenant/database for multi-tenancy

### 6. Core (`app/core/`)

**Purpose**: Application-wide configuration and utilities

**Components**:
- `config.py`: Pydantic settings with validation
- `errors.py`: Exception hierarchy
- `logging.py`: Structured JSON logging
- `constants.py`: Enums and default values

**Design Decisions**:
- Settings loaded from environment variables
- Custom exception hierarchy for specific error types
- Structured logging for observability
- Type-safe constants

### 7. Models (`app/models/`)

**Purpose**: Data structures and API contracts

**Components**:
- `schemas.py`: API request/response models
- `document.py`: Document and chunk models
- `metadata.py`: Metadata structures

**Design Decisions**:
- Pydantic models for validation
- Clear separation between domain and API models
- Type hints throughout

## Design Principles

### 1. Modularity

- Each component has a single responsibility
- No file exceeds 500 lines of code
- Clear boundaries between layers
- Easy to test in isolation

### 2. Extensibility

- Abstract base classes for all component types
- Factory pattern for component creation
- Easy to add new file types, embedders, or storage backends
- Configuration-driven behavior

### 3. Type Safety

- Type hints throughout
- Pydantic models for validation
- Enums for constants
- MyPy for static type checking

### 4. Async-First

- All I/O operations are async
- FastAPI async handlers
- Async document loaders and embedders
- Supports high concurrency

### 5. Error Handling

- Custom exception hierarchy
- Specific error types (FileValidationError, EmbeddingError, etc.)
- Middleware converts exceptions to JSON responses
- Structured error logging

### 6. Testing

- Unit tests for individual components
- Integration tests for services
- API tests for endpoints
- Pytest with async support

## Data Flow

### Document Ingestion Flow

1. **Client uploads files** (multipart/form-data)
   - Multiple files supported
   - Files can be PDF, TXT, or DOCX

2. **FastAPI endpoint** receives request
   - `POST /api/v1/upload`
   - Files extracted from form data

3. **UploadService orchestrates processing**
   - Validates files (type, size, count)
   - Saves files to temp directory
   - Calls IngestionAgent

4. **IngestionAgent processes each file**
   - Uses PydanticAI for orchestration
   - Calls validation and processing tools
   - Returns structured results

5. **LangGraph pipeline executes**
   - Load: DocumentLoader parses file
   - Split: TextSplitter creates chunks
   - Embed: Embedder generates vectors (OpenAI API)
   - Store: VectorStore persists chunks (ChromaDB local or cloud)

6. **Cleanup and response**
   - Temp files deleted immediately
   - Results aggregated
   - JSON response returned to client

### State Transformation

```python
IngestionState:
  file_path: "data/uploads/doc.pdf"
  ↓ load_document_node
  document: Document(content="...", metadata=...)
  ↓ split_document_node
  chunks: [DocumentChunk(...), ...]
  ↓ embed_chunks_node
  embedded_chunks: [DocumentChunk(embedding=[...]), ...]
  ↓ store_chunks_node
  status: "completed"
```

## Extension Guidelines

### Adding a New File Type

1. Create loader in `app/rag/loaders/`:
```python
from .base import BaseDocumentLoader

class HTMLLoader(BaseDocumentLoader):
    async def load(self) -> Document:
        # Implementation
        pass
```

2. Add to FileType enum in `app/core/constants.py`:
```python
class FileType(str, Enum):
    HTML = "html"
```

3. Register in `DocumentLoaderFactory`:
```python
_loaders = {
    FileType.HTML: HTMLLoader,
}
```

### Adding a New Embedding Provider

1. Implement `BaseEmbedder` in `app/rag/embeddings/`:
```python
class HuggingFaceEmbedder(BaseEmbedder):
    async def embed_chunks(self, chunks): ...
    async def embed_query(self, query): ...
    @property
    def embedding_dimensions(self): ...
```

2. Add to `EmbedderFactory`
3. Add configuration to Settings
4. Update environment variables

### Adding a New Vector Store

1. Implement `BaseVectorStore` in `app/rag/storage/`:
```python
class PineconeVectorStore(BaseVectorStore):
    async def add_chunks(self, chunks): ...
    async def similarity_search(self, query_embedding, k): ...
    async def delete_by_document_id(self, document_id): ...
    async def count(self): ...
```

2. Add to `VectorStoreFactory`
3. Add configuration to Settings

### Adding a New Endpoint

1. Create router in `app/api/`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/query")
async def query_documents(...):
    pass
```

2. Include in `app/api/routes.py`:
```python
from .query import router as query_router
api_router.include_router(query_router, tags=["query"])
```

## Configuration Management

### Settings Priority

1. Environment variables (`.env` file)
2. Default values in `Settings` class

### Required Settings

- `OPENAI_API_KEY`: OpenAI API key (required for default embeddings)

### Optional Settings

All other settings have sensible defaults. Override as needed.

## Security Considerations

### File Upload Security

- File size limits enforced
- File type validation (extension + MIME type)
- Temporary file storage with cleanup
- No arbitrary file path access

### API Security (Future)

- Add authentication middleware
- Rate limiting
- CORS configuration
- Input sanitization

## Performance Considerations

### Async Operations

- All I/O is async
- Concurrent file processing possible
- Non-blocking embeddings and storage

### Caching

- Settings cached with `lru_cache`
- Service instances cached
- Consider adding Redis for distributed caching

### Optimization Opportunities

- Batch embeddings for efficiency
- Parallel document processing
- Streaming large file uploads
- Background task processing

## Monitoring and Observability

### Logging

- Structured JSON logs
- Request ID tracking
- Processing time metrics
- Error details captured

### Metrics (Future)

- Document processing rate
- Embedding API latency
- Vector store query performance
- Error rates by type

## Testing Strategy

### Unit Tests

- Test individual components in isolation
- Mock external dependencies
- Focus on business logic

### Integration Tests

- Test service layer with real components
- Use in-memory storage to avoid external dependencies
- Test error handling paths

### API Tests

- Use FastAPI TestClient
- Test all endpoints
- Verify status codes and response formats

## Dependencies

### Core Dependencies

- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **PydanticAI**: Agent framework
- **LangChain/LangGraph**: RAG workflow
- **OpenAI**: Embeddings
- **ChromaDB**: Vector storage

### Document Processing

- **PyMuPDF**: PDF parsing
- **python-docx**: DOCX parsing
- **aiofiles**: Async file I/O

### Development

- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking
- **flake8**: Linting

## Future Enhancements

### Phase 2: Query/Retrieval

- Query endpoint with semantic search
- PydanticAI query agent
- Reranking for improved relevance
- LLM-based answer generation

### Phase 3: Advanced Features

- Document deduplication (by hash)
- Metadata filtering in queries
- Batch processing
- Webhook notifications
- Multi-tenancy support
- Authentication and authorization

### Phase 4: Scaling

- Distributed task queue (Celery)
- Redis caching
- Load balancing
- Database for metadata
- Horizontal scaling

## Conclusion

This RAG Backend is designed for production use with:
- ✅ Modular, extensible architecture
- ✅ Type-safe, validated code
- ✅ Comprehensive error handling
- ✅ Async-first performance
- ✅ Clear separation of concerns
- ✅ Extensive documentation

For questions or contributions, please refer to the project's GitHub repository.
