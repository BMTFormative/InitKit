from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    AdminApiKey,
    AdminApiKeyCreate,
    AdminApiKeyPublic,
    AdminApiKeyUpdate,
    Message,
)
from app.services.api_key_service import ApiKeyService
from app.core.config import settings

router = APIRouter(prefix="/admin/api-keys", tags=["admin api keys"])
service = ApiKeyService(settings.API_KEY_ENCRYPTION_KEY)

@router.post("/", response_model=AdminApiKeyPublic)
def create_admin_api_key(
    key_data: AdminApiKeyCreate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser)
) -> AdminApiKeyPublic:
    """Create or rotate a global API key (super-admin only)."""
    key = service.create_admin_api_key(
        session,
        key_data.provider,
        key_data.api_key,
    )
    # Return key value in response for display
    raw = service.decrypt_key(key.encrypted_key)
    return AdminApiKeyPublic(
        id=key.id,
        provider=key.provider,
        is_active=key.is_active,
        created_at=key.created_at,
        last_used=key.last_used,
        api_key=raw,
    )

@router.get("/", response_model=List[AdminApiKeyPublic])
def list_admin_api_keys(
    session: SessionDep,
    current_user=Depends(get_current_active_superuser)
) -> List[AdminApiKeyPublic]:
    """List all global API keys (super-admin only)."""
    statement = select(AdminApiKey)
    keys = session.exec(statement).all()
    result: List[AdminApiKeyPublic] = []
    for key in keys:
        # Decrypt stored key for display
        raw = service.decrypt_key(key.encrypted_key)
        result.append(
            AdminApiKeyPublic(
                id=key.id,
                provider=key.provider,
                is_active=key.is_active,
                created_at=key.created_at,
                last_used=key.last_used,
                api_key=raw,
            )
        )
    return result

@router.delete("/{key_id}", response_model=Message)
def delete_admin_api_key(
    key_id: uuid.UUID,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser)
) -> Message:
    """Delete a global API key (super-admin only)."""
    key = session.get(AdminApiKey, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    session.delete(key)
    session.commit()
    return Message(message="API key deleted successfully")

@router.patch("/{key_id}", response_model=AdminApiKeyPublic)
def update_admin_api_key_status(
    key_id: uuid.UUID,
    key_data: AdminApiKeyUpdate,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser)
) -> AdminApiKeyPublic:
    """Activate or deactivate a global API key (super-admin only)."""
    key = session.get(AdminApiKey, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    # If activating, deactivate others
    if key_data.is_active:
        stmt = select(AdminApiKey).where(
            AdminApiKey.provider == key.provider,
            AdminApiKey.is_active == True,
            AdminApiKey.id != key_id,
        )
        others = session.exec(stmt).all()
        for other in others:
            other.is_active = False
            session.add(other)
    key.is_active = key_data.is_active
    session.add(key)
    session.commit()
    session.refresh(key)
    # Include raw key for display
    raw = service.decrypt_key(key.encrypted_key)
    return AdminApiKeyPublic(
        id=key.id,
        provider=key.provider,
        is_active=key.is_active,
        created_at=key.created_at,
        last_used=key.last_used,
        api_key=raw,
    )