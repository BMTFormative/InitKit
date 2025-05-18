from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import (
    SessionDep, SuperAdminUser, TenantAdminUser, TenantFromPath
)
from app.models import (
    TenantApiKey, TenantApiKeyCreate, TenantApiKeyPublic, Message
)
from app.services.api_key_service import ApiKeyService
from app.core.config import settings

router = APIRouter(prefix="/tenants/{tenant_id}/api-keys", tags=["tenant api keys"])
api_key_service = ApiKeyService(settings.API_KEY_ENCRYPTION_KEY)

@router.post("/", response_model=TenantApiKeyPublic)
def create_api_key(
    tenant: TenantFromPath,
    key_data: TenantApiKeyCreate,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> TenantApiKeyPublic:
    """Create/rotate API key for a tenant (TenantAdmin or SuperAdmin only)"""
    admin, _ = admin_data
    
    api_key = api_key_service.create_tenant_api_key(
        session,
        tenant.id,
        key_data.provider,
        key_data.api_key
    )
    
    # Don't return the actual key, just metadata
    return TenantApiKeyPublic(
        id=api_key.id,
        provider=api_key.provider,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used=api_key.last_used
    )

@router.get("/", response_model=List[TenantApiKeyPublic])
def list_api_keys(
    tenant: TenantFromPath,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> List[TenantApiKeyPublic]:
    """List API keys for a tenant (TenantAdmin or SuperAdmin only)"""
    admin, _ = admin_data
    
    statement = select(TenantApiKey).where(
        TenantApiKey.tenant_id == tenant.id
    )
    
    keys = session.exec(statement).all()
    
    # Don't return actual keys, just metadata
    return [
        TenantApiKeyPublic(
            id=key.id,
            provider=key.provider,
            is_active=key.is_active,
            created_at=key.created_at,
            last_used=key.last_used
        )
        for key in keys
    ]

@router.delete("/{key_id}", response_model=Message)
def delete_api_key(
    tenant: TenantFromPath,
    key_id: uuid.UUID,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> Message:
    """Delete an API key (TenantAdmin or SuperAdmin only)"""
    admin, _ = admin_data
    
    key = session.get(TenantApiKey, key_id)
    if not key or key.tenant_id != tenant.id:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
        
    session.delete(key)
    session.commit()
    
    return Message(message="API key deleted successfully")