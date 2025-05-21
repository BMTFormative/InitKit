from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.services.invitation_service import InvitationService
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message, NewPassword, Token, UserPublic, UserCreate, User
from app.services.api_key_service import ApiKeyService
from sqlmodel import select
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])
api_key_service = ApiKeyService(settings.API_KEY_ENCRYPTION_KEY)


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create token payload with role and tenant_id
    # Use is_superuser to grant global super-admin role
    token_data = {
        "sub": str(user.id),
        "role": "superadmin" if user.is_superuser else user.role
    }
    
    # Only add tenant_id if it exists
    if user.tenant_id:
        token_data["tenant_id"] = str(user.tenant_id)
    
    # Create the JWT
    token_str = security.create_access_token(
        token_data, expires_delta=access_token_expires
    )
    # On first login, give the tenant an active Admin API key if they have none
    if user.tenant_id:
        # Only assign one unique global key per tenant
        existing = api_key_service.get_active_key_for_tenant(
            session, user.tenant_id, "openai"
        )
        if not existing:
            # Consume the next available Admin API key for this provider
            raw_key = api_key_service.consume_admin_api_key(
                session, "openai"
            )
            if raw_key:
                api_key_service.create_tenant_api_key(
                    session, user.tenant_id, "openai", raw_key
                )
    return Token(access_token=token_str)


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
@router.post("/login/accept-invitation", response_model=UserPublic)
def accept_invitation(
    session: SessionDep,
    token: str = Body(...),
    user_data: UserCreate = Body(...),
) -> User:
    """
    Accept an invitation and create a new user
    """
    invitation_service = InvitationService()
    user = invitation_service.accept_invitation(
        session=session,
        token=token,
        user_data=user_data
    )
    return user