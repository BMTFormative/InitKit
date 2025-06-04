# backend/app/services/job_posting_service.py
import asyncio
from typing import Dict, Any
from sqlmodel import Session
import uuid

from app.models import JobPosting
from app.services.credit_service import CreditService
from app.services.claude_service import ClaudeService, QuotaExceededError
from app.services.api_key_service import ApiKeyService

class JobPostingService:
    def __init__(self):
        self.api_key_service = ApiKeyService()
        self.credit_service = CreditService()
    
    async def generate_job_posting(
        self, 
        session: Session,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate job posting using Claude AI with credit deduction"""
        
        # Check credits (5 credits per generation)
        user_balance = self.credit_service.get_user_balance(session, user_id)
        if user_balance < 5:
            raise ValueError("Insufficient credits for job posting generation")
        
        # Get Claude API key for tenant
        claude_key = self.api_key_service.get_active_key_for_tenant(session, tenant_id, "claude")
        if not claude_key:
            raise ValueError("No Claude API key configured for this tenant")
        
        try:
            # Initialize Claude service
            claude_service = ClaudeService(claude_key)
            
            # Generate job posting
            result = await claude_service.generate_job_posting(job_data)
            
            # Deduct credits for successful generation
            self.credit_service.deduct_user_credits(
                session, 
                tenant_id, 
                5.0, 
                f"Job posting generation: {job_data.get('job_title', 'Untitled')}", 
                user_id
            )
            
            return {
                "content": result["content"],
                "model_used": result["model_used"],
                "knowledge_sources": result.get("knowledge_sources", []),
                "credits_used": 5.0,
                "success": True
            }
            
        except QuotaExceededError:
            raise ValueError("Claude API rate limit exceeded. Please try again later.")
        except Exception as e:
            raise ValueError(f"Failed to generate job posting: {str(e)}")
    
    async def analyze_job_posting(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str
    ) -> Dict[str, Any]:
        """Analyze job posting quality using Claude AI"""
        
        # Check credits (2 credits per analysis)
        user_balance = self.credit_service.get_user_balance(session, user_id)
        if user_balance < 2:
            raise ValueError("Insufficient credits for job posting analysis")
        
        # Get Claude API key for tenant
        claude_key = self.api_key_service.get_active_key_for_tenant(session, tenant_id, "claude")
        if not claude_key:
            raise ValueError("No Claude API key configured for this tenant")
        
        try:
            # Initialize Claude service
            claude_service = ClaudeService(claude_key)
            
            # Analyze job posting
            result = await claude_service.analyze_job_posting(content)
            
            if result["success"]:
                # Deduct credits for successful analysis
                self.credit_service.deduct_user_credits(
                    session,
                    tenant_id, 
                    2.0, 
                    "Job posting quality analysis", 
                    user_id
                )
            
            return {
                "score": result["score"],
                "suggestions": result["suggestions"],
                "credits_used": 2.0 if result["success"] else 0.0,
                "success": result["success"]
            }
            
        except QuotaExceededError:
            raise ValueError("Claude API rate limit exceeded. Please try again later.")
        except Exception as e:
            raise ValueError(f"Failed to analyze job posting: {str(e)}")
    
    def save_job_posting(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        job_data: Dict[str, Any],
        generated_content: str,
        generation_metadata: Dict[str, Any]
    ) -> JobPosting:
        """Save generated job posting to database"""
        
        job_posting = JobPosting(
            tenant_id=tenant_id,
            created_by=user_id,
            job_title=job_data.get("job_title"),
            location=job_data.get("location"),
            experience_level=job_data.get("experience_level"),
            employment_type=job_data.get("employment_type"),
            job_overview=job_data.get("job_overview"),
            responsibilities=job_data.get("responsibilities", []),
            team_intro=job_data.get("team_intro"),
            required_skills=job_data.get("required_skills"),
            education_requirements=job_data.get("education_requirements"),
            certifications=job_data.get("certifications"),
            include_salary=job_data.get("include_salary", False),
            salary_range=job_data.get("salary_range"),
            benefits=job_data.get("benefits", []),
            perks=job_data.get("perks"),
            platform=job_data.get("platform", "LinkedIn"),
            length=job_data.get("length", "standard"),
            application_deadline_days=job_data.get("application_deadline"),
            keywords=job_data.get("keywords"),
            generated_content=generated_content,
            credits_used=generation_metadata.get("credits_used", 0.0),
            generation_model=generation_metadata.get("model_used"),
            generation_metadata=generation_metadata,
            status="draft"
        )
        
        session.add(job_posting)
        session.commit()
        session.refresh(job_posting)
        
        return job_posting