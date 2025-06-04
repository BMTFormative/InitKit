from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, Extra
from typing import Any, Dict, Optional

# Internal Job Posting modules
from app.modules.job_posting.chat_manager import ChatManager
from app.modules.job_posting.claude_api import ClaudeAPI
from app.modules.job_posting.knowledge_base import KnowledgeBaseManager
from app.modules.job_posting.intelligent_enhancement import IntelligentJobEnhancer

router = APIRouter()

# Request model for generating job postings (allows extra form fields)
class GenerateJobPostingRequest(BaseModel, extra=Extra.allow):
    job_title: str = Field(..., example="Software Engineer")
    job_description: Optional[str] = Field(None, example="Build APIs…")
    job_overview: Optional[str] = Field(None, example="Summary of role…")
    platform: Optional[str] = Field(None, example="linkedin")


# Instantiate managers for job posting
chat_manager = ChatManager()
kb_manager = KnowledgeBaseManager()
intelligent_enhancer = IntelligentJobEnhancer(kb_manager)
claude_api = ClaudeAPI()

@router.get("/health")
async def health_check():
    """Simple health check for the integrated Job Posting module."""
    return {"status": "job_posting module is up"}

@router.post("/generate")
async def generate_job_posting(
    payload: GenerateJobPostingRequest = Body(...)
):
    """Generate a job posting using the integrated module."""
    data: Dict[str, Any] = payload.dict()
    job_title = data.get("job_title")
    if not job_title:
        raise HTTPException(status_code=400, detail="job_title is required")

    # Enhance the job posting context
    enhancement = intelligent_enhancer.analyze_and_enhance(data)
    context = enhancement.get("enhanced_context", "")

    # Stream response chunks from Claude
    async def event_stream():
        async for chunk in claude_api.send_message_stream(context):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")

class AnalyzeBiasRequest(BaseModel, extra=Extra.ignore):
    query: str = Field(..., example="Software Engineer")
    n_results: int = Field(5, ge=1, example=5)

@router.post("/analyze-bias")
async def analyze_bias(
    payload: AnalyzeBiasRequest = Body(...)
):
    """Analyze potential bias in search results."""
    query = payload.query
    n_results = payload.n_results
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    # Perform bias analysis via the vector store
    analysis = kb_manager.vector_store.analyze_search_bias(query, n_results)
    recommendations = []
    if isinstance(analysis, dict) and analysis.get("bias_detected"):
        recommendations.append("Consider using balanced retrieval to improve diversity.")

    return JSONResponse(content={
        "query": query,
        "bias_analysis": analysis,
        "recommendations": recommendations
    })