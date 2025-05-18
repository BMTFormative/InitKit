from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import (
    SessionDep, SuperAdminUser, TenantAdminUser, TenantFromPath,
    CurrentUserWithTenant, require_same_tenant
)
from app.models import (
    Tenant, TenantCreate, TenantUpdate, TenantPublic, TenantWithBalancePublic,
    User, Message
)
from app.services.credit_service import CreditService

router = APIRouter(tags=["tenants"])
credit_service = CreditService()

@router.post("/", response_model=TenantPublic)
def create_tenant(
    tenant_in: TenantCreate,
    session: SessionDep,
    admin: SuperAdminUser
) -> Tenant:
    """Create new tenant (SuperAdmin only)"""
    tenant = Tenant.model_validate(tenant_in)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant

@router.get("/", response_model=List[TenantPublic])
def list_tenants(
    session: SessionDep,
    admin: SuperAdminUser,
    skip: int = 0,
    limit: int = 100
) -> List[Tenant]:
    """List all tenants (SuperAdmin only)"""
    statement = select(Tenant).offset(skip).limit(limit)
    tenants = session.exec(statement).all()
    return tenants

@router.get("/{tenant_id}", response_model=TenantWithBalancePublic)
def get_tenant(
    tenant: TenantFromPath,
    session: SessionDep,
    current_data: CurrentUserWithTenant
) -> TenantWithBalancePublic:
    """Get tenant details with credit balance"""
    user = require_same_tenant(current_data, tenant.id)
    balance = credit_service.get_tenant_balance(session, tenant.id)
    
    # Manual construction of response with balance
    return TenantWithBalancePublic(
        id=tenant.id,
        name=tenant.name,
        description=tenant.description,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        credit_balance=balance
    )

@router.patch("/{tenant_id}", response_model=TenantPublic)
def update_tenant(
    tenant: TenantFromPath,
    tenant_update: TenantUpdate,
    session: SessionDep,
    admin: SuperAdminUser
) -> Tenant:
    """Update tenant (SuperAdmin only)"""
    tenant_data = tenant_update.model_dump(exclude_unset=True)
    tenant.sqlmodel_update(tenant_data)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant

@router.delete("/{tenant_id}", response_model=Message)
def delete_tenant(
    tenant: TenantFromPath,
    session: SessionDep,
    admin: SuperAdminUser
) -> Message:
    """Delete tenant (SuperAdmin only)"""
    session.delete(tenant)
    session.commit()
    return Message(message="Tenant deleted successfully")