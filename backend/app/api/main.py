from fastapi import APIRouter

from app.api.routes import (
    items, login, private, users, utils, subscriptions,
    tenants, tenant_users, tenant_api_keys, tenant_credits, ai_proxy, tenant_email_config
)
from app.api.routes import admin_api_keys, admin_tenant_api_keys
from app.api.routes import job_postings
from app.core.config import settings
from app.api.routes import payment
api_router = APIRouter()
api_router.include_router(payment.router)
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router)
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(tenant_email_config.router)
api_router.include_router(tenant_users.router)
api_router.include_router(tenant_api_keys.router)
api_router.include_router(tenant_credits.router)
api_router.include_router(ai_proxy.router, prefix="/ai-proxy", tags=["ai proxy"])
api_router.include_router(admin_api_keys.router)
# Tenant API keys across all tenants (super-admin only)
api_router.include_router(admin_tenant_api_keys.router)
# Job Posting module endpoints
api_router.include_router(job_postings.router, prefix="/job_postings", tags=["job_postings"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router, tags=["private"], prefix="/private")
