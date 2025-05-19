# backend/app/services/invitation_service.py
from fastapi import HTTPException
from sqlmodel import Session, select
import uuid
from datetime import datetime, timedelta
import emails
import logging
import jwt

from app.models import TenantInvitation, User, UserCreate, Tenant, EmailConfig
from app.core.security import create_access_token, get_password_hash
from app.core.config import settings
from app.utils import render_email_template

logger = logging.getLogger(__name__)

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
        """
        Create an invitation for a user to join a tenant.
        Will send an email if the tenant has email configuration.
        """
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
        
        # Create a unique invitation ID
        invitation_id = str(uuid.uuid4())
        
        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        if existing_invitation:
            # Update existing invitation
            existing_invitation.expires_at = expires_at
            existing_invitation.created_by = created_by
            existing_invitation.role = role
            
            # Create optimized token with minimal payload
            token_data = {
                "sub": str(existing_invitation.id),  # Use existing ID
                "tid": str(tenant_id),               # Tenant ID (shortened key name)
                "eml": email,                        # User email (shortened key name)
                "rol": role,                         # User role (shortened key name)
                "inv": True,                         # Flag to identify as invitation token
                "exp": expires_at.timestamp(),       # Expiration timestamp
                "iat": datetime.utcnow().timestamp() # Issued at timestamp
            }
            
            token = create_access_token(token_data, expires_delta=None)  # Use explicit expiration in payload
            
            existing_invitation.token = token
            session.add(existing_invitation)
            session.commit()
            session.refresh(existing_invitation)
            
            # We'll try to send the updated invitation email below
            invitation = existing_invitation
        else:
            # Create optimized token with minimal payload
            token_data = {
                "sub": invitation_id,                # Unique ID for this invitation
                "tid": str(tenant_id),               # Tenant ID (shortened key name)
                "eml": email,                        # User email (shortened key name)
                "rol": role,                         # User role (shortened key name)
                "inv": True,                         # Flag to identify as invitation token
                "exp": expires_at.timestamp(),       # Expiration timestamp
                "iat": datetime.utcnow().timestamp() # Issued at timestamp
            }
            
            token = create_access_token(token_data, expires_delta=None)  # Use explicit expiration in payload
            
            invitation = TenantInvitation(
                id=uuid.UUID(invitation_id),  # Use same ID as in token
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
        
        # Get tenant and creator information
        tenant = session.get(Tenant, tenant_id)
        creator = session.get(User, created_by)
        
        if not tenant:
            logger.error(f"Tenant {tenant_id} not found when creating invitation")
            return invitation
            
        if not creator:
            logger.error(f"Creator {created_by} not found when creating invitation")
            return invitation
        
        # Check if tenant has email configuration
        statement = select(EmailConfig).where(
            EmailConfig.tenant_id == tenant_id
        )
        email_config = session.exec(statement).first()
        
        # Generate invitation URL
        frontend_url = settings.FRONTEND_HOST
        invite_url = f"{frontend_url}/accept-invitation?token={token}"
            
        # Prepare email context
        email_context = {
            "project_name": tenant.name,
            "username": email,
            "invite_url": invite_url,
            "creator_name": creator.full_name or creator.email,
            "expires_hours": expires_hours
        }
        
        # Render email template
        html_content = render_email_template(
            template_name="invitation.html",
            context=email_context,
        )
        
        subject = f"Invitation to join {tenant.name}"
        
        # Send invitation email
        if email_config:
            # Use tenant's email configuration
            try:
                message = emails.Message(
                    subject=subject,
                    html=html_content,
                    mail_from=(email_config.from_name or tenant.name, email_config.from_email),
                )
                
                smtp_options = {
                    "host": email_config.smtp_host,
                    "port": email_config.smtp_port,
                    "tls": email_config.smtp_use_tls,
                    "user": email_config.smtp_user,
                    "password": email_config.smtp_password,
                    "debug": 1  # Enable SMTP level debugging
                }
                
                response = message.send(to=email, smtp=smtp_options)
                logger.info(f"Invitation email sent using tenant configuration: {response}")
                logger.info(f"SMTP Response status: {getattr(response, 'status_code', None)}")
            except Exception as e:
                logger.error(f"Failed to send invitation email using tenant configuration: {str(e)}", exc_info=True)
                # Continue even if email fails - the invitation is still created
        elif settings.emails_enabled:
            # Fall back to system email configuration
            try:
                message = emails.Message(
                    subject=subject,
                    html=html_content,
                    mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
                )
                
                smtp_options = {
                    "host": settings.SMTP_HOST, 
                    "port": settings.SMTP_PORT,
                    "debug": 1  # Enable SMTP level debugging
                }
                
                if settings.SMTP_TLS:
                    smtp_options["tls"] = True
                elif settings.SMTP_SSL:
                    smtp_options["ssl"] = True
                
                if settings.SMTP_USER:
                    smtp_options["user"] = settings.SMTP_USER
                    
                if settings.SMTP_PASSWORD:
                    smtp_options["password"] = settings.SMTP_PASSWORD
                
                response = message.send(to=email, smtp=smtp_options)
                logger.info(f"Invitation email sent using system configuration: {response}")
                logger.info(f"SMTP Response status: {getattr(response, 'status_code', None)}")
            except Exception as e:
                logger.error(f"Failed to send invitation email using system configuration: {str(e)}", exc_info=True)
        else:
            logger.warning("No email configuration available. Invitation created but email not sent.")
        
        return invitation
        
    def accept_invitation(
        self,
        session: Session,
        token: str,
        user_data: UserCreate
    ) -> User:
        """
        Accept an invitation and create a new user in the tenant.
        """
        # Validate token with improved error handling
        try:
            # Decode the token with explicit algorithms
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"],
                options={"verify_signature": True, "verify_exp": True}
            )
            
            # Validate it's an invitation token
            if not payload.get("inv"):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid invitation token type"
                )
                
            # Extract data using shortened key names
            invitation_id = payload.get("sub")
            email = payload.get("eml")
            tenant_id = payload.get("tid")
            role = payload.get("rol", "user")
            
            if not all([invitation_id, email, tenant_id]):
                raise HTTPException(
                    status_code=400,
                    detail="Incomplete invitation token"
                )
            
            # Find invitation by ID for better security
            invitation = session.get(TenantInvitation, uuid.UUID(invitation_id))
            if not invitation:
                raise HTTPException(
                    status_code=404,
                    detail="Invitation not found"
                )
                
            # Additional validations
            if invitation.is_used:
                raise HTTPException(
                    status_code=400, 
                    detail="Invitation has already been used"
                )
                
            if invitation.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=400,
                    detail="Invitation has expired"
                )
                
            # Verify email matches between token and invitation record
            if invitation.email.lower() != email.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Token email mismatch"
                )
                
            # Ensure user email matches invitation email
            if user_data.email.lower() != email.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Email in user data doesn't match invitation email"
                )
                
            # Check if user already exists
            statement = select(User).where(User.email == email)
            existing_user = session.exec(statement).first()
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="User with this email already exists"
                )
                
            # Create user
            user = User(
                email=email,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                tenant_id=uuid.UUID(tenant_id),
                role=role,
                is_active=True,
                is_superuser=False
            )
            session.add(user)
            
            # Mark invitation as used
            invitation.is_used = True
            session.add(invitation)
            
            session.commit()
            session.refresh(user)
            
            # Send welcome email
            self._send_welcome_email(session, uuid.UUID(tenant_id), user)
            
            return user
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired invitation token attempted")
            raise HTTPException(
                status_code=400,
                detail="Invitation token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token in accept_invitation: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid invitation token format"
            )
        except Exception as e:
            logger.error(f"Error in accept_invitation: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error accepting invitation"
            )
    
    def _send_welcome_email(
        self,
        session: Session,
        tenant_id: uuid.UUID,
        user: User
    ) -> None:
        """
        Send a welcome email to the new user.
        """
        try:
            # Get tenant information
            tenant = session.get(Tenant, tenant_id)
            if not tenant:
                logger.error(f"Tenant {tenant_id} not found when sending welcome email")
                return
                
            # Check if tenant has email configuration
            statement = select(EmailConfig).where(
                EmailConfig.tenant_id == tenant_id
            )
            email_config = session.exec(statement).first()
            
            # Generate login URL
            frontend_url = settings.FRONTEND_HOST
            login_url = f"{frontend_url}/login"
                
            # Prepare email context
            email_context = {
                "project_name": tenant.name,
                "username": user.full_name or user.email,
                "login_url": login_url,
            }
            
            # Render email template
            html_content = render_email_template(
                template_name="welcome.html",
                context=email_context,
            )
            
            subject = f"Welcome to {tenant.name}"
            
            # Send welcome email
            if email_config:
                # Use tenant's email configuration
                message = emails.Message(
                    subject=subject,
                    html=html_content,
                    mail_from=(email_config.from_name or tenant.name, email_config.from_email),
                )
                
                smtp_options = {
                    "host": email_config.smtp_host,
                    "port": email_config.smtp_port,
                    "tls": email_config.smtp_use_tls,
                    "user": email_config.smtp_user,
                    "password": email_config.smtp_password,
                    "debug": 1  # Enable SMTP level debugging
                }
                
                response = message.send(to=user.email, smtp=smtp_options)
                logger.info(f"Welcome email sent using tenant configuration: {response}")
                logger.info(f"SMTP Response status: {getattr(response, 'status_code', None)}")
            elif settings.emails_enabled:
                # Fall back to system email configuration
                message = emails.Message(
                    subject=subject,
                    html=html_content,
                    mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
                )
                
                smtp_options = {
                    "host": settings.SMTP_HOST, 
                    "port": settings.SMTP_PORT,
                    "debug": 1  # Enable SMTP level debugging
                }
                
                if settings.SMTP_TLS:
                    smtp_options["tls"] = True
                elif settings.SMTP_SSL:
                    smtp_options["ssl"] = True
                
                if settings.SMTP_USER:
                    smtp_options["user"] = settings.SMTP_USER
                    
                if settings.SMTP_PASSWORD:
                    smtp_options["password"] = settings.SMTP_PASSWORD
                
                response = message.send(to=user.email, smtp=smtp_options)
                logger.info(f"Welcome email sent using system configuration: {response}")
                logger.info(f"SMTP Response status: {getattr(response, 'status_code', None)}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}", exc_info=True)
            # Ignore errors in welcome email - user is still created