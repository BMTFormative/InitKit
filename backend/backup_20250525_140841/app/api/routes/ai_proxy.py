from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
import uuid
from typing import Dict, Any

from app.api.deps import (
    SessionDep, CurrentUserWithTenant, require_same_tenant
)
from app.services.api_key_service import ApiKeyService
from app.services.credit_service import CreditService
from app.services.ai_api_service import AiApiProxyService
from app.core.config import settings

router = APIRouter(prefix="/ai-proxy", tags=["ai proxy"])

api_key_service = ApiKeyService(settings.API_KEY_ENCRYPTION_KEY)
credit_service = CreditService()
ai_proxy_service = AiApiProxyService(api_key_service, credit_service)

@router.post("/openai/{endpoint:path}")
async def proxy_openai_request(
    endpoint: str,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
    payload: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """Proxy request to OpenAI API with credit deduction"""
    user, tenant_id, role = current_data
    
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail="No tenant associated with this user"
        )
        
    # Make sure the proxy endpoint is allowed
    allowed_endpoints = ["chat/completions", "completions", "embeddings"]
    if not any(endpoint.startswith(e) for e in allowed_endpoints):
        raise HTTPException(
            status_code=403,
            detail=f"Endpoint not allowed: {endpoint}"
        )
        
    result = await ai_proxy_service.proxy_openai_request(
        session,
        tenant_id,
        user.id,
        endpoint,
        payload
    )
    
    return result