# .env File Configuration Guide

## The Problem

If you're seeing this error when uploading files:
```
"The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
```

Even though you've set `OPENAI_API_KEY` in your `.env` file, **the issue is likely with how the value is formatted**.

## Root Cause

**DO NOT wrap environment variable values in quotes** (unless they contain spaces or special characters).

### ❌ INCORRECT Format:
```bash
OPENAI_API_KEY="sk-proj-xxx..."
APP_NAME="RAG Backend"
EMBEDDING_PROVIDER="openai"
```

When values are quoted, `pydantic-settings` reads the quotes as **part of the actual value**, so:
- The OpenAI client receives: `"sk-proj-xxx..."` (with quotes) ❌
- Instead of: `sk-proj-xxx...` (without quotes) ✅

### ✅ CORRECT Format:
```bash
OPENAI_API_KEY=sk-proj-xxx...
APP_NAME=RAG Backend
EMBEDDING_PROVIDER=openai
```

## When to Use Quotes

Only use quotes when the value contains spaces or special shell characters:

```bash
# Value with spaces - quotes needed
APP_DESCRIPTION=RAG Backend API for document processing

# Simple value - no quotes needed
APP_NAME=RAG_Backend

# API key - no quotes needed
OPENAI_API_KEY=sk-proj-abc123xyz

# Number - no quotes needed
PORT=8000

# Boolean - no quotes needed
DEBUG=false
```

## How to Fix

1. Open your `.env` file
2. Remove all quotes from values
3. Save the file
4. Restart your application

## Example Fixed .env File

```bash
# ============================================
# RAG Backend Environment Configuration
# ============================================

# REQUIRED: OpenAI API Key for embeddings
OPENAI_API_KEY=sk-proj-your-actual-key-here

# ============================================
# Application Settings (Optional)
# ============================================

APP_NAME=RAG Backend
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# API settings
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# ============================================
# Embedding Settings
# ============================================

EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# ============================================
# Vector Store Settings
# ============================================

VECTOR_STORE=chroma_local
CHROMA_COLLECTION_NAME=documents
```

## Verifying the Fix

After updating your `.env` file, start the application:

```bash
python main.py
```

You should see in the startup logs:
```
OPENAI KEY = sk-proj-xxx... (without quotes)
```

If you still see quotes around the key, check your `.env` file again.

## Additional Troubleshooting

### Issue 1: .env file not being loaded

**Symptoms**: Settings use default values instead of .env values

**Solution**: Ensure your `.env` file is in the project root directory (same location as `main.py`)

### Issue 2: File encoding issues

**Symptoms**: Weird characters in values

**Solution**: Save `.env` file with UTF-8 encoding (no BOM)

### Issue 3: Whitespace issues

**Symptoms**: Values have extra spaces

**Solution**: Remove any spaces around the `=` sign:
```bash
# ❌ Incorrect
OPENAI_API_KEY = sk-proj-xxx

# ✅ Correct
OPENAI_API_KEY=sk-proj-xxx
```

## Best Practices

1. **Never commit `.env` to git** - it contains secrets
2. **Use `.env.example` as a template** - without real secrets
3. **Keep values unquoted** - unless absolutely necessary
4. **Comment your variables** - explain what each does
5. **Validate on startup** - the app will error if required vars are missing

## Reference

This application uses `pydantic-settings` to load environment variables. See the [official documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for more details.
