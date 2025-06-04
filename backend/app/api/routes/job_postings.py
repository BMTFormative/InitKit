from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
import uuid
from typing import Any

from app.api.deps import SessionDep, CurrentUserWithTenant, TenantAdminUser
from app.services.credit_service import CreditService
from app.services.api_key_service import ApiKeyService
from app.models import JobPosting, JobPostingTemplate, Message
from app.services.job_posting_service import JobPostingService

router = APIRouter(prefix="/tenants/{tenant_id}/job-postings", tags=["job postings"])

@router.post("/", response_model=dict)
async def create_job_posting(
    tenant_id: uuid.UUID,
    job_data: dict,  # Your job posting request data
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Any:
    """Generate AI-powered job posting with credit deduction"""
    user, token_tenant_id, role = current_data
    
    # Ensure tenant access
    if role != "superadmin" and str(tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check credits (5 credits per generation)
    credit_service = CreditService()
    user_balance = credit_service.get_user_balance(session, user.id)
    if user_balance < 5:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Get Claude API key for tenant
    api_key_service = ApiKeyService()
    claude_key = api_key_service.get_active_key_for_tenant(session, tenant_id, "claude")
    if not claude_key:
        raise HTTPException(status_code=400, detail="No Claude API key configured")
    
    # Generate job posting
    job_service = JobPostingService(claude_key)
    result = await job_service.generate_job_posting(job_data)
    
    # Save to database
    job_posting = JobPosting(
        tenant_id=tenant_id,
        created_by=user.id,
        job_title=job_data.get("job_title"),
        **job_data,  # Map other fields
        generated_content=result["content"],
        quality_score=result.get("quality_score"),
        credits_used=5.0,
        generation_model="claude-3-5-sonnet"
    )
    session.add(job_posting)
    
    # Deduct credits
    credit_service.deduct_user_credits(
        session, tenant_id, 5.0, 
        f"Job posting generation: {job_data.get('job_title')}", 
        user.id
    )
    
    session.commit()
    session.refresh(job_posting)
    
    return {"job_posting": job_posting, "generated_content": result["content"]}

@router.get("/", response_model=list[dict])
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
    return job_postings