# backend/app/api/routes/job_postings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
import uuid
from typing import Any, Dict, List

from app.api.deps import SessionDep, CurrentUserWithTenant
from app.services.job_posting_service import JobPostingService
from app.models import JobPosting, Message

router = APIRouter(prefix="/tenants/{tenant_id}/job-postings", tags=["job postings"])

@router.post("/generate", response_model=Dict[str, Any])
async def generate_job_posting(
    tenant_id: uuid.UUID,
    job_data: Dict[str, Any],
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Generate AI-powered job posting with credit deduction"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        job_service = JobPostingService()
        result = await job_service.generate_job_posting(
            session=session,
            tenant_id=tenant_id,
            user_id=user.id,
            job_data=job_data
        )
        
        return {
            "generated_content": result["content"],
            "model_used": result["model_used"],
            "knowledge_sources": result.get("knowledge_sources", []),
            "credits_used": result["credits_used"],
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Job posting generation failed")

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_job_posting(
    tenant_id: uuid.UUID,
    content_data: Dict[str, str],  # {"content": "job posting text"}
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Analyze job posting quality and provide suggestions"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    content = content_data.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    try:
        job_service = JobPostingService()
        result = await job_service.analyze_job_posting(
            session=session,
            tenant_id=tenant_id,
            user_id=user.id,
            content=content
        )
        
        return {
            "score": result["score"],
            "suggestions": result["suggestions"],
            "credits_used": result["credits_used"],
            "success": result["success"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Job posting analysis failed")

@router.post("/apply-suggestions", response_model=Dict[str, Any])
async def apply_suggestions(
    tenant_id: uuid.UUID,
    suggestion_data: Dict[str, Any],
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Apply suggestions to improve a job posting"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    original_content = suggestion_data.get("original_content")
    suggestions = suggestion_data.get("suggestions", [])
    
    if not original_content or not suggestions:
        raise HTTPException(status_code=400, detail="Original content and suggestions are required")
    
    try:
        # Create job data for improvement
        job_data = {
            "job_title": "Job Posting Improvement",
            "job_overview": f"Original content: {original_content}",
            "platform": "general",
            "improvement_suggestions": suggestions,
            "additional_instructions": suggestion_data.get("comment", "")
        }
        
        job_service = JobPostingService()
        result = await job_service.generate_job_posting(
            session=session,
            tenant_id=tenant_id,
            user_id=user.id,
            job_data=job_data
        )
        
        return {
            "improved_content": result["content"],
            "credits_used": result["credits_used"],
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Suggestion application failed")

@router.post("/", response_model=Dict[str, Any])
async def create_job_posting(
    tenant_id: uuid.UUID,
    job_data: Dict[str, Any],
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Create and save a job posting (with optional AI generation)"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        job_service = JobPostingService()
        
        # If AI generation is requested
        if job_data.get("use_ai_generation", False):
            # Generate with AI
            generation_result = await job_service.generate_job_posting(
                session=session,
                tenant_id=tenant_id,
                user_id=user.id,
                job_data=job_data
            )
            
            # Save the generated job posting
            job_posting = job_service.save_job_posting(
                session=session,
                tenant_id=tenant_id,
                user_id=user.id,
                job_data=job_data,
                generated_content=generation_result["content"],
                generation_metadata={
                    "model_used": generation_result["model_used"],
                    "knowledge_sources": generation_result.get("knowledge_sources", []),
                    "credits_used": generation_result["credits_used"]
                }
            )
            
            return {
                "job_posting": job_posting,
                "generated_content": generation_result["content"],
                "ai_generated": True
            }
        else:
            # Save manually created job posting
            job_posting = job_service.save_job_posting(
                session=session,
                tenant_id=tenant_id,
                user_id=user.id,
                job_data=job_data,
                generated_content=job_data.get("generated_content", ""),
                generation_metadata={}
            )
            
            return {
                "job_posting": job_posting,
                "ai_generated": False
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Job posting creation failed")

@router.get("/", response_model=List[Dict[str, Any]])
def list_job_postings(
    tenant_id: uuid.UUID,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """List tenant job postings"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Query with tenant isolation
    statement = (
        select(JobPosting)
        .where(JobPosting.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .order_by(JobPosting.created_at.desc())
    )
    
    job_postings = session.exec(statement).all()
    return [
        {
            "id": jp.id,
            "job_title": jp.job_title,
            "platform": jp.platform,
            "status": jp.status,
            "credits_used": jp.credits_used,
            "generation_model": jp.generation_model,
            "created_at": jp.created_at,
            "ai_generated": bool(jp.generation_model)
        }
        for jp in job_postings
    ]

@router.get("/{job_posting_id}", response_model=Dict[str, Any])
def get_job_posting(
    tenant_id: uuid.UUID,
    job_posting_id: uuid.UUID,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Get a specific job posting"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    job_posting = session.get(JobPosting, job_posting_id)
    if not job_posting or job_posting.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    return job_posting

@router.put("/{job_posting_id}", response_model=Dict[str, Any])
def update_job_posting(
    tenant_id: uuid.UUID,
    job_posting_id: uuid.UUID,
    update_data: Dict[str, Any],
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Update a job posting"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    job_posting = session.get(JobPosting, job_posting_id)
    if not job_posting or job_posting.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Update allowed fields
    for field, value in update_data.items():
        if hasattr(job_posting, field) and field not in ['id', 'tenant_id', 'created_by', 'created_at']:
            setattr(job_posting, field, value)
    
    session.add(job_posting)
    session.commit()
    session.refresh(job_posting)
    
    return job_posting

@router.delete("/{job_posting_id}", response_model=Message)
def delete_job_posting(
    tenant_id: uuid.UUID,
    job_posting_id: uuid.UUID,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Delete a job posting"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    job_posting = session.get(JobPosting, job_posting_id)
    if not job_posting or job_posting.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    session.delete(job_posting)
    session.commit()
    
    return Message(message="Job posting deleted successfully")