"""
Service layer for managing Job Posting dynamic configuration.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Session

from app.models import JobPostingConfig
from app.core.config import settings

def get_job_posting_config(session: Session) -> Optional[JobPostingConfig]:
    """
    Retrieve the singleton JobPostingConfig from the database.
    """
    return session.get(JobPostingConfig, 1)

def create_job_posting_config(session: Session) -> JobPostingConfig:
    """
    Create the default JobPostingConfig using environment settings.
    """
    config = JobPostingConfig(
        id=1,
        default_model=settings.DEFAULT_MODEL,
        vector_store_path=settings.VECTOR_STORE_PATH,
        knowledge_base_path=settings.KNOWLEDGE_BASE_PATH,
        vector_search_top_k=settings.VECTOR_SEARCH_TOP_K,
        vector_search_similarity_threshold=settings.VECTOR_SEARCH_SIMILARITY_THRESHOLD,
        embedding_model=settings.EMBEDDING_MODEL,
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

def update_job_posting_config(
    session: Session,
    config_update: JobPostingConfig
) -> JobPostingConfig:
    """
    Update the existing JobPostingConfig with new values.
    """
    config = get_job_posting_config(session)
    if not config:
        config = create_job_posting_config(session)
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    config.updated_at = datetime.utcnow()
    session.add(config)
    session.commit()
    session.refresh(config)
    return config