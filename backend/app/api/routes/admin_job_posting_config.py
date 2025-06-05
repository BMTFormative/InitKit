from typing import Optional
from sqlmodel import SQLModel, Session
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import JobPostingConfig
from app.services.job_posting_config import (
    get_job_posting_config,
    create_job_posting_config,
    update_job_posting_config,
)

router = APIRouter(prefix="/admin", tags=["admin"])

class JobPostingConfigUpdate(SQLModel):
    """
    Fields to update in JobPostingConfig. All are optional.
    """
    default_model: Optional[str] = None
    vector_store_path: Optional[str] = None
    knowledge_base_path: Optional[str] = None
    vector_search_top_k: Optional[int] = None
    vector_search_similarity_threshold: Optional[float] = None
    embedding_model: Optional[str] = None

@router.get(
    "/job_posting_config", response_model=JobPostingConfig
)
def read_job_posting_config(
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> JobPostingConfig:
    """
    Retrieve the current job posting configuration, creating defaults if absent.
    """
    config = get_job_posting_config(session)
    if not config:
        config = create_job_posting_config(session)
    return config

@router.patch(
    "/job_posting_config", response_model=JobPostingConfig
)
def patch_job_posting_config(
    config_in: JobPostingConfigUpdate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> JobPostingConfig:
    """
    Update the job posting configuration. Only provided fields will be updated.
    """
    # Validate input exists
    if not config_in.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="No configuration fields provided for update.")
    try:
        updated = update_job_posting_config(session, config_in)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))