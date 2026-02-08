# RAG Chat Assistant - Streamlit Frontend

A professional dark-mode Streamlit frontend for the RAG (Retrieval-Augmented Generation) backend system. This UI provides an intuitive interface for uploading documents and chatting with your knowledge base.

## Features

- **Two-Page Interface**
  - **Chat**: Interactive chat interface with RAG-powered responses
  - **Upload Documents**: File upload with progress tracking

- **Professional Dark Mode**
  - Custom dark theme with blue accents
  - Styled message bubbles (user: right/blue, AI: left/gray)
  - Source badges for transparency

- **Real-time Backend Integration**
  - Health check monitoring
  - Connection status indicators
  - Error handling with actionable feedback

- **Session Management**
  - Persistent chat history during session
  - Upload result tracking
  - Backend status caching

## Requirements

- Python 3.13 or lower
- Running RAG backend on `http://localhost:8000`
- Dependencies listed in `requirements.txt`

## Installation

### 1. Navigate to the Ui directory

```bash
cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent/Ui
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend (Terminal 1)

The frontend requires the FastAPI backend to be running:

```bash
# Navigate to the project root
cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent

# Start the backend
python main.py
```

The backend should start on `http://localhost:8000`. You'll see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Verify the backend is running:**
```bash
# In the Ui directory, run the test script
cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent/Ui
python test_backend.py
```

This will test both the root endpoint (`/`) and health endpoint (`/api/v1/health`).

### Start the Frontend (Terminal 2)

In a separate terminal:

```bash
# Navigate to the Ui directory
cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent/Ui

# Start Streamlit
streamlit run app.py
```

The frontend will automatically open in your browser at `http://localhost:8501`.

## Usage

### Uploading Documents

1. Navigate to **"Upload Documents"** in the sidebar
2. Click **"Browse files"** and select your documents
   - Supported formats: PDF, DOCX, TXT
   - Max file size: 10MB per file
3. Review selected files (name and size displayed)
4. Click **"Upload and Process"**
5. Wait for processing (progress indicator shown)
6. View results:
   - Files processed count
   - Chunks created count
   - Per-file success/error details

### Chatting with Documents

1. Navigate to **"Chat"** in the sidebar
2. (Optional) Adjust **top_k** slider to control retrieval
   - Higher values = more context, slower response
   - Default: 5 chunks
3. Type your question in the input box
4. Click **"Send"** or press Enter
5. View AI response with:
   - Answer text
   - Source document badges
   - Query processing time

### Managing Chat History

- **Clear History**: Click "Clear Chat History" button in sidebar
- **View History**: All messages persist during your browser session
- **New Session**: Close browser tab to start fresh

## Configuration

### API Endpoints

The backend exposes the following endpoints:

- **Root**: `http://localhost:8000/` - Basic info and docs link
- **Health**: `http://localhost:8000/api/v1/health` - Health check
- **Upload**: `http://localhost:8000/api/v1/upload` - Document upload
- **Chat**: `http://localhost:8000/api/v1/chat` - RAG queries
- **API Docs**: `http://localhost:8000/docs` - Interactive API documentation

Edit `config/settings.py` to change API URLs:

```python
API_BASE_URL = "http://localhost:8000/api/v1"  # Backend API base
API_HEALTH_URL = "http://localhost:8000/api/v1/health"  # Health check
```

### Theme Customization

Edit `.streamlit/config.toml` to customize colors:

```toml
[theme]
primaryColor = "#4A90E2"  # Blue accent
backgroundColor = "#0E1117"  # Dark background
secondaryBackgroundColor = "#1E2130"  # Lighter background
textColor = "#FAFAFA"  # Text color
```

### File Upload Limits

Edit `config/settings.py`:

```python
MAX_FILE_SIZE_MB = 10  # Maximum file size
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt"]  # Accepted formats
```

## Troubleshooting

### Backend Connection Issues

**Problem**: "Backend is not connected" error

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check for port conflicts (ensure port 8000 is available)
3. Review backend logs for errors
4. Restart backend: `python main.py`

### Upload Failures

**Problem**: Files fail to upload

**Possible causes and solutions**:
- **File too large**: Reduce file size or split document
- **Unsupported format**: Convert to PDF, DOCX, or TXT
- **Backend error**: Check backend logs for details
- **Timeout**: Try uploading fewer files at once

### Chat Not Working

**Problem**: Queries fail or return errors

**Possible causes and solutions**:
- **No documents uploaded**: Upload documents first
- **Backend disconnected**: Restart backend
- **Invalid query**: Try rephrasing your question
- **Timeout**: Reduce top_k value or simplify query

### Theme Not Applied

**Problem**: Dark theme not showing

**Solution**:
1. Verify `.streamlit/config.toml` exists
2. Restart Streamlit server
3. Clear browser cache
4. Check browser console for errors

## Project Structure

```
Ui/
├── .streamlit/
│   └── config.toml          # Dark theme configuration
├── config/
│   ├── __init__.py
│   └── settings.py          # API URLs and constants
├── utils/
│   ├── __init__.py
│   ├── api_client.py        # Backend API communication
│   ├── session_manager.py   # Session state management
│   └── ui_components.py     # Reusable UI components
├── pages/
│   ├── 1_Chat.py            # Chat interface page
│   └── 2_Upload_Documents.py  # Upload interface page
├── app.py                   # Main entry point
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## API Integration

### Chat Endpoint

**URL**: `POST http://localhost:8000/api/v1/chat`

**Request**:
```json
{
  "query": "What is the main topic?",
  "top_k": 5
}
```

**Response**:
```json
{
  "success": true,
  "answer": "The main topic is...",
  "sources": ["document1.pdf", "document2.txt"],
  "chunks": [...],
  "query_time_ms": 250.5,
  "error": null
}
```

### Upload Endpoint

**URL**: `POST http://localhost:8000/api/v1/upload`

**Request**: `multipart/form-data` with field name `"files"`

**Response**:
```json
{
  "success": true,
  "files_processed": 2,
  "chunks_created": 45,
  "message": "Successfully processed 2 files",
  "details": [
    {
      "filename": "doc1.pdf",
      "status": "success",
      "chunks_created": 25
    },
    {
      "filename": "doc2.txt",
      "status": "success",
      "chunks_created": 20
    }
  ],
  "error": null
}
```

## Development

### Code Structure Guidelines

Following the project's `CLAUDE.md` guidelines:

- All files <500 lines of code
- Type hints throughout
- Docstrings for all functions (Google style)
- Modular, reusable components
- Clear separation of concerns

### Testing Locally

1. Start backend with test environment
2. Upload sample documents (PDF, DOCX, TXT)
3. Test chat with various queries
4. Verify error handling (disconnect backend, invalid files, etc.)
5. Check UI responsiveness and styling

### Adding New Features

1. **New Page**: Create `pages/N_PageName.py`
2. **New Component**: Add to `utils/ui_components.py`
3. **New API Call**: Add to `utils/api_client.py`
4. **Configuration**: Update `config/settings.py`

## Performance Considerations

- **Backend Timeouts**:
  - Health check: 2 seconds
  - Chat query: 30 seconds
  - File upload: 60 seconds

- **Session State**:
  - Chat history stored in browser session
  - Cleared on tab close or manual clear
  - No persistent storage

- **File Processing**:
  - Files processed sequentially by backend
  - Large files may take longer
  - Progress indicated by spinner

## Security Notes

- No authentication implemented (add if deploying publicly)
- Files uploaded to backend temp directory (cleaned after processing)
- No client-side file storage
- CORS disabled by default (configure if needed)

## Support

For issues or questions:
1. Check this README
2. Review backend logs
3. Verify backend is running
4. Check browser console for errors
5. Refer to main project documentation

## License

Part of the RAG Backend project. See main project LICENSE.
