from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from typing import List

from app.api.deps import (
    SessionDep, SuperAdminUser, TenantAdminUser, TenantFromPath,
    CurrentUserWithTenant, require_same_tenant
)
from app.models import (
    User, UserCreate, UserUpdate, UserPublic, Message,
    TenantInvitation, TenantInvitationCreate, TenantInvitationPublic
)
from app.services.invitation_service import InvitationService
from app import crud

router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["tenant users"])
invitation_service = InvitationService()

# app/api/routes/tenant_users.py
@router.get("/", response_model=List[UserPublic])
def list_tenant_users(
    tenant: TenantFromPath,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """List all users in a tenant"""
    require_same_tenant(current_data, tenant.id)
    
    statement = select(User).where(
        User.tenant_id == tenant.id
    ).offset(skip).limit(limit)
    
    users = session.exec(statement).all()
    return users

@router.post("/invitations", response_model=TenantInvitationPublic)
def create_invitation(
    tenant: TenantFromPath,
    invitation_data: TenantInvitationCreate,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> TenantInvitation:
    """Create invitation for new user (TenantAdmin only)"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    invitation = invitation_service.create_invitation(
        session,
        tenant.id,
        invitation_data.email,
        invitation_data.role,
        admin.id
    )
    
    return invitation

@router.get("/invitations", response_model=List[TenantInvitationPublic])
def list_invitations(
    tenant: TenantFromPath,
    session: SessionDep,
    admin_data: TenantAdminUser,
    include_used: bool = False
) -> List[TenantInvitation]:
    """List all invitations for a tenant"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    query = select(TenantInvitation).where(
        TenantInvitation.tenant_id == tenant.id
    )
    
    if not include_used:
        query = query.where(TenantInvitation.is_used == False)
        
    invitations = session.exec(query).all()
    return invitations

@router.delete("/invitations/{invitation_id}", response_model=Message)
def delete_invitation(
    tenant: TenantFromPath,
    invitation_id: uuid.UUID,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> Message:
    """Delete an invitation"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    invitation = session.get(TenantInvitation, invitation_id)
    if not invitation or invitation.tenant_id != tenant.id:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
        )
        
    session.delete(invitation)
    session.commit()
    
    return Message(message="Invitation deleted successfully")
    
@router.patch("/{user_id}", response_model=UserPublic)
def update_tenant_user(
    tenant: TenantFromPath,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    session: SessionDep,
    admin_data: TenantAdminUser,
) -> UserPublic:
    """Update a user's status within a tenant (tenant admin only)"""
    admin, _ = admin_data
    # Ensure tenant admin belongs to this tenant
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    # Fetch user and ensure belongs to tenant
    user = session.get(User, user_id)
    if not user or user.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="User not found in this tenant")
    # Only allow updating fields on UserUpdate (e.g., is_active)
    updated_user = crud.update_user(session=session, db_user=user, user_in=user_in)
    return updated_user