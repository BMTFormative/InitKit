import uuid
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session,select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User, Tenant

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_user_with_tenant(
    session: SessionDep, 
    token: TokenDep
) -> tuple[User, uuid.UUID | None, str]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        user_id = token_data.sub
        tenant_id = token_data.tenant_id
        role = token_data.role
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Ensure tenant_id from token matches user's tenant_id in database
    if tenant_id and user.tenant_id and str(tenant_id) != str(user.tenant_id):
        raise HTTPException(
            status_code=403,
            detail="Token tenant_id doesn't match user's tenant_id"
        )
        
    return user, tenant_id, role

CurrentUserWithTenant = Annotated[tuple[User, uuid.UUID | None, str], Depends(get_current_user_with_tenant)]

# Role-based dependencies
def require_super_admin(current_data: CurrentUserWithTenant) -> User:
    user, _, role = current_data
    if role != "superadmin":
        raise HTTPException(
            status_code=403, 
            detail="Super admin privileges required"
        )
    return user

SuperAdminUser = Annotated[User, Depends(require_super_admin)]

def require_tenant_admin(current_data: CurrentUserWithTenant) -> tuple[User, uuid.UUID]:
    user, tenant_id, role = current_data
    if role not in ["tenant_admin", "superadmin"]:
        raise HTTPException(
            status_code=403, 
            detail="Tenant admin privileges required"
        )
    if not tenant_id and role != "superadmin":
        raise HTTPException(
            status_code=403, 
            detail="No tenant associated with this user"
        )
    return user, tenant_id

TenantAdminUser = Annotated[tuple[User, uuid.UUID], Depends(require_tenant_admin)]

def require_same_tenant(
    current_data: CurrentUserWithTenant, 
    tenant_id_param: uuid.UUID
) -> User:
    user, tenant_id, role = current_data
    if role == "superadmin":
        return user
    if str(tenant_id) != str(tenant_id_param):
        raise HTTPException(
            status_code=403, 
            detail="Access denied to this tenant's resources"
        )
    return user

def get_tenant_from_path(
    tenant_id: uuid.UUID, 
    session: SessionDep
) -> Tenant:
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )
    return tenant

TenantFromPath = Annotated[Tenant, Depends(get_tenant_from_path)]