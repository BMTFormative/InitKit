# Job Posting Module Integration

This document outlines how to integrate the **job_posting** module into our application, enabling AI-powered job posting generation and bias analysis.

## Overview

The **job_posting** module provides two primary endpoints via FastAPI:
  - **POST** `/api/v1/job_postings/generate`
    • Streams generated job postings from Claude (RAG pattern).
  - **POST** `/api/v1/job_postings/analyze-bias`
    • Analyzes vector search results for potential bias and returns recommendations.

Core implementation lives under:
```
backend/app/modules/job_posting/
```

## Prerequisites

1. **Install dependencies** (from `backend/`):
   ```bash
   # Using Poetry
   poetry add anthropic chromadb sentence-transformers python-dotenv numpy torch transformers pydantic-settings
   
   # Or using pip
   pip install anthropic chromadb sentence-transformers python-dotenv numpy torch transformers pydantic-settings
   ```

2. **Environment variables** (add to `backend/.env` or one level above `backend/app/`):
   ```env
   ANTHROPIC_API_KEY=<your_claude_api_key>
   CLAUDE_MODEL=claude-opus-4-20250514
   VECTOR_STORE_PATH=../job_posting/data/vector_store
   KNOWLEDGE_BASE_PATH=../job_posting/data/knowledge_base
   VECTOR_SEARCH_TOP_K=5
   VECTOR_SEARCH_SIMILARITY_THRESHOLD=0.3
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

3. Confirm that `backend/pyproject.toml` lists these libraries under `[project].dependencies`.

## Configuration

The shared settings in `backend/app/core/config.py` now expose:
```python
settings.ANTHROPIC_API_KEY
settings.DEFAULT_MODEL
settings.SYSTEM_INSTRUCTIONS
settings.VECTOR_STORE_PATH
settings.KNOWLEDGE_BASE_PATH
settings.VECTOR_SEARCH_TOP_K
settings.VECTOR_SEARCH_SIMILARITY_THRESHOLD
settings.EMBEDDING_MODEL
```
These drive the behavior of `claude_api.py`, `knowledge_base.py`, and vector store modules.

## Backend Integration

1. **Include the router** in `backend/app/api/main.py`:
   ```python
   from app.api.routes import job_postings

   api_router.include_router(
       job_postings.router,
       prefix="/job_postings",
       tags=["job_postings"]
   )
   ```

2. **Start the server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Verify via Swagger/OpenAPI**:
   Browse to `http://localhost:8000/docs` to see:
   - **Generate** schema (Pydantic model `GenerateJobPostingRequest`)
   - **Analyze Bias** schema (`AnalyzeBiasRequest`)

## Frontend Integration

Call the endpoints with any HTTP client. Examples using `fetch`:

- **Generate** (stream):
  ```js
  fetch('/api/v1/job_postings/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_title: 'Software Engineer',
      job_description: 'Build REST APIs with FastAPI',
      platform: 'linkedin'
    })
  }).then(response => {
    const reader = response.body.getReader();
    // read stream chunks...
  });
  ```

- **Analyze Bias**:
  ```js
  fetch('/api/v1/job_postings/analyze-bias', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'Software Engineer', n_results: 5 })
  })
    .then(res => res.json())
    .then(console.log);
  ```

## Testing

- Use the auto-generated Swagger UI or write unit tests for:
  - `ChatManager`, `KnowledgeBaseManager`, and vector store methods
  - `ClaudeAPI.send_message_stream` (mocking Anthropic client)
  - `IntelligentJobEnhancer.analyze_and_enhance`

## Extending

- **New endpoints**: add to `backend/app/api/routes/job_postings.py`
- **Schema updates**: extend Pydantic models for request/response
- **System instructions**: tweak `settings.SYSTEM_INSTRUCTIONS`
- **Alternate vector store**: swap `vector_store.py` or `vector_store_simple.py`

This integration guide should help future developers configure and use the job_posting module seamlessly.