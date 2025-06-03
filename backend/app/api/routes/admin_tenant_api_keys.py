from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import TenantApiKey, AdminTenantApiKeyPublic
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/admin/tenant-api-keys", tags=["admin tenant api keys"])
service = ApiKeyService(settings.API_KEY_ENCRYPTION_KEY)

@router.get("/", response_model=List[AdminTenantApiKeyPublic])
def list_tenant_api_keys(
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
) -> List[AdminTenantApiKeyPublic]:
    """List all tenant API keys across all tenants (super-admin only)."""
    statement = select(TenantApiKey)
    keys = session.exec(statement).all()
    result: List[AdminTenantApiKeyPublic] = []
    for key in keys:
        raw = service.decrypt_key(key.encrypted_key)
        result.append(
            AdminTenantApiKeyPublic(
                id=key.id,
                tenant_id=key.tenant_id,
                provider=key.provider,
                is_active=key.is_active,
                created_at=key.created_at,
                last_used=key.last_used,
                api_key=raw,
            )
        )
    return result