from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid

from app.api.deps import (
    SessionDep, TenantAdminUser, TenantFromPath,
    CurrentUserWithTenant, require_same_tenant
)
from app.models import (
    EmailConfig, EmailConfigBase, Message
)
from app.utils import send_test_email

router = APIRouter(prefix="/tenants/{tenant_id}/email-config", tags=["tenant email config"])

@router.get("/", response_model=EmailConfigBase)
def get_email_config(
    tenant: TenantFromPath,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> EmailConfigBase:
    """Get email configuration for a tenant (TenantAdmin only)"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    statement = select(EmailConfig).where(
        EmailConfig.tenant_id == tenant.id
    )
    config = session.exec(statement).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Email configuration not found"
        )
        
    return config

@router.post("/", response_model=EmailConfigBase)
def create_email_config(
    tenant: TenantFromPath,
    config_data: EmailConfigBase,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> EmailConfig:
    """Create/update email configuration for a tenant (TenantAdmin only)"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    # Check if config already exists
    statement = select(EmailConfig).where(
        EmailConfig.tenant_id == tenant.id
    )
    existing_config = session.exec(statement).first()
    
    if existing_config:
        # Update existing config
        for key, value in config_data.dict().items():
            setattr(existing_config, key, value)
        existing_config.updated_at = datetime.utcnow()
        session.add(existing_config)
        session.commit()
        session.refresh(existing_config)
        return existing_config
    
    # Create new config
    config = EmailConfig(tenant_id=tenant.id, **config_data.dict())
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

@router.post("/test", response_model=Message)
def test_email_config(
    tenant: TenantFromPath,
    session: SessionDep,
    admin_data: TenantAdminUser
) -> Message:
    """Send test email using tenant's email configuration"""
    admin, _ = admin_data
    
    # Only allow tenant admins of this tenant or superadmins
    require_same_tenant((admin, admin.tenant_id, admin.role), tenant.id)
    
    statement = select(EmailConfig).where(
        EmailConfig.tenant_id == tenant.id
    )
    config = session.exec(statement).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Email configuration not found"
        )
    
    # Send test email
    try:
        send_test_email(
            email_to=admin.email,
            smtp_host=config.smtp_host,
            smtp_port=config.smtp_port,
            smtp_user=config.smtp_user,
            smtp_password=config.smtp_password,
            smtp_tls=config.smtp_use_tls,
            from_email=config.from_email,
            from_name=config.from_name or tenant.name
        )
        return Message(message="Test email sent successfully")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test email: {str(e)}"
        )