from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import (
    SessionDep,
    CurrentUserWithTenant,
    TenantFromPath,
)
from app.models import (
    TenantApiKey,
    TenantApiKeyCreate,
    TenantApiKeyPublic,
    TenantApiKeyUpdate,
    Message,
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
    current_data: CurrentUserWithTenant,
) -> TenantApiKeyPublic:
    """Create/rotate API key for a tenant.
    Tenant admins can manage non-OpenAI keys; only super-admin can manage OpenAI keys."""
    user, token_tenant_id, role = current_data
    # Require tenant admin or super-admin
    if role not in ["tenant_admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Tenant admin privileges required")
    # Ensure same tenant unless super-admin
    if tenant.id and role != "superadmin" and str(tenant.id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this tenant's resources")
    # Only super-admin may manage OpenAI API keys
    if key_data.provider.lower() == "openai" and role != "superadmin":
        raise HTTPException(status_code=403, detail="Super admin privileges required to manage OpenAI API key")
    # Create or rotate the key
    api_key = api_key_service.create_tenant_api_key(
        session,
        tenant.id,
        key_data.provider,
        key_data.api_key,
    )
    # Return metadata only
    return TenantApiKeyPublic(
        id=api_key.id,
        provider=api_key.provider,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used=api_key.last_used,
    )

@router.get("/", response_model=List[TenantApiKeyPublic])
def list_api_keys(
    tenant: TenantFromPath,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> List[TenantApiKeyPublic]:
    """List API keys for a tenant.
    Tenant admins can view non-OpenAI keys; only super-admin can view OpenAI keys."""
    user, token_tenant_id, role = current_data
    # Require tenant admin or super-admin
    if role not in ["tenant_admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Tenant admin privileges required")
    # Ensure same tenant unless super-admin
    if tenant.id and role != "superadmin" and str(tenant.id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this tenant's resources")
    # Retrieve keys
    statement = select(TenantApiKey).where(TenantApiKey.tenant_id == tenant.id)
    keys = session.exec(statement).all()
    result: List[TenantApiKeyPublic] = []
    for key in keys:
        # Only super-admin may view OpenAI keys
        if key.provider.lower() == "openai" and role != "superadmin":
            continue
        result.append(
            TenantApiKeyPublic(
                id=key.id,
                provider=key.provider,
                is_active=key.is_active,
                created_at=key.created_at,
                last_used=key.last_used,
            )
        )
    return result

@router.delete("/{key_id}", response_model=Message)
def delete_api_key(
    tenant: TenantFromPath,
    key_id: uuid.UUID,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> Message:
    """Delete an API key for a tenant.
    Tenant admins can delete non-OpenAI keys; only super-admin can delete OpenAI keys."""
    user, token_tenant_id, role = current_data
    # Require tenant admin or super-admin
    if role not in ["tenant_admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Tenant admin privileges required")
    # Ensure same tenant unless super-admin
    if tenant.id and role != "superadmin" and str(tenant.id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this tenant's resources")
    # Fetch key
    key = session.get(TenantApiKey, key_id)
    if not key or key.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="API key not found")
    # Only super-admin may delete OpenAI keys
    if key.provider.lower() == "openai" and role != "superadmin":
        raise HTTPException(status_code=403, detail="Super admin privileges required to delete OpenAI API key")
    session.delete(key)
    session.commit()
    return Message(message="API key deleted successfully")
    
@router.patch("/{key_id}", response_model=TenantApiKeyPublic)
def update_api_key_status(
    tenant: TenantFromPath,
    key_id: uuid.UUID,
    key_data: TenantApiKeyUpdate,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
) -> TenantApiKeyPublic:
    """Update the active status of an API key for a tenant.
    Tenant admins can modify non-OpenAI keys; only super-admin can modify OpenAI keys."""
    user, token_tenant_id, role = current_data
    # Require tenant admin or super-admin
    if role not in ["tenant_admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Tenant admin privileges required")
    # Ensure same tenant unless super-admin
    if tenant.id and role != "superadmin" and str(tenant.id) != str(token_tenant_id):
        raise HTTPException(status_code=403, detail="Access denied to this tenant's resources")
    # Fetch key
    key = session.get(TenantApiKey, key_id)
    if not key or key.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="API key not found")
    # Only super-admin may modify OpenAI key status
    if key.provider.lower() == "openai" and role != "superadmin":
        raise HTTPException(status_code=403, detail="Super admin privileges required to modify OpenAI API key")
    # Activate or deactivate key
    if key_data.is_active:
        # Deactivate any other active keys for this provider
        statement = select(TenantApiKey).where(
            TenantApiKey.tenant_id == tenant.id,
            TenantApiKey.provider == key.provider,
            TenantApiKey.is_active == True,
            TenantApiKey.id != key_id,
        )
        other_keys = session.exec(statement).all()
        for other in other_keys:
            other.is_active = False
            session.add(other)
    key.is_active = key_data.is_active
    session.add(key)
    session.commit()
    session.refresh(key)
    return TenantApiKeyPublic(
        id=key.id,
        provider=key.provider,
        is_active=key.is_active,
        created_at=key.created_at,
        last_used=key.last_used,
    )