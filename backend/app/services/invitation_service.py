from fastapi import HTTPException
from sqlmodel import Session, select
import uuid
from datetime import datetime, timedelta

from app.models import TenantInvitation, User, UserCreate
from app.core.security import create_access_token, get_password_hash
import jwt
from app.core.config import settings

class InvitationService:
    def create_invitation(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        email: str,
        role: str,
        created_by: uuid.UUID,
        expires_hours: int = 48
    ) -> TenantInvitation:
        # Check if user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
            
        # Check if invitation already exists
        statement = select(TenantInvitation).where(
            TenantInvitation.email == email,
            TenantInvitation.tenant_id == tenant_id,
            TenantInvitation.is_used == False
        )
        existing_invitation = session.exec(statement).first()
        if existing_invitation:
            # Update existing invitation
            existing_invitation.expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            existing_invitation.created_by = created_by
            existing_invitation.role = role
            session.add(existing_invitation)
            session.commit()
            session.refresh(existing_invitation)
            return existing_invitation
            
        # Create new invitation
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        token_data = {
            "sub": str(uuid.uuid4()),  # Temporary ID
            "tenant_id": str(tenant_id),
            "email": email,
            "role": role,
            "invitation": True
        }
        token = create_access_token(
            token_data, 
            timedelta(hours=expires_hours)
        )
        
        invitation = TenantInvitation(
            tenant_id=tenant_id,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            created_by=created_by
        )
        session.add(invitation)
        session.commit()
        session.refresh(invitation)
        return invitation
        
    def accept_invitation(
        self,
        session: Session,
        token: str,
        user_data: UserCreate
    ) -> User:
        # Validate token
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            if not payload.get("invitation"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid invitation token"
                )
                
            email = payload.get("email")
            tenant_id = payload.get("tenant_id")
            role = payload.get("role", "user")
            
            # Find invitation
            statement = select(TenantInvitation).where(
                TenantInvitation.email == email,
                TenantInvitation.tenant_id == uuid.UUID(tenant_id),
                TenantInvitation.is_used == False
            )
            invitation = session.exec(statement).first()
            if not invitation:
                raise HTTPException(
                    status_code=404,
                    detail="Invitation not found or already used"
                )
                
            if invitation.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=400,
                    detail="Invitation has expired"
                )
                
            # Create user
            user = User(
                email=email,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                tenant_id=uuid.UUID(tenant_id),
                role=role
            )
            session.add(user)
            
            # Mark invitation as used
            invitation.is_used = True
            session.add(invitation)
            
            session.commit()
            session.refresh(user)
            return user
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=400,
                detail="Invalid invitation token"
            )