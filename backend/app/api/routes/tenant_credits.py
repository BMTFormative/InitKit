from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import (
    SessionDep, SuperAdminUser, TenantAdminUser, TenantFromPath,
    CurrentUserWithTenant, require_same_tenant
)
from app.models import (
    CreditTransaction, CreditTransactionCreate, CreditTransactionPublic, Message
)
from app.services.credit_service import CreditService

router = APIRouter(prefix="/tenants/{tenant_id}/credits", tags=["tenant credits"])
credit_service = CreditService()

@router.post("/", response_model=CreditTransactionPublic)
def add_credits(
    tenant: TenantFromPath,
    transaction_data: CreditTransactionCreate,
    session: SessionDep,
    admin: SuperAdminUser
) -> CreditTransaction:
    """Add credits to a tenant (SuperAdmin only)"""
    
    if transaction_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive for adding credits"
        )
        
    transaction = credit_service.add_credits(
        session,
        tenant.id,
        transaction_data.amount,
        transaction_data.description,
        admin.id
    )
    
    return transaction

@router.get("/", response_model=List[CreditTransactionPublic])
def list_transactions(
    tenant: TenantFromPath,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
    skip: int = 0,
    limit: int = 100
) -> List[CreditTransaction]:
    """List credit transactions for a tenant"""
    require_same_tenant(current_data, tenant.id)
    
    statement = select(CreditTransaction).where(
        CreditTransaction.tenant_id == tenant.id
    ).order_by(CreditTransaction.created_at.desc()).offset(skip).limit(limit)
    
    transactions = session.exec(statement).all()
    return transactions