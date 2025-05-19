import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel,Column, JSON
from datetime import datetime

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    tenant_id: uuid.UUID | None = None
    role: str = Field(default="user")

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

# New Tenant Model - add after existing models
class TenantBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    
class Tenant(TenantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    users: list["User"] = Relationship(back_populates="tenant")
    api_keys: list["TenantApiKey"] = Relationship(back_populates="tenant", cascade_delete=True)
    credit_ledger: list["CreditTransaction"] = Relationship(back_populates="tenant", cascade_delete=True)
    email_config: "EmailConfig" = Relationship(back_populates="tenant", sa_relationship_kwargs={"uselist": False})
# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    tenant_id: uuid.UUID | None = Field(foreign_key="tenant.id", nullable=True)  # Null for SuperAdmin
    tenant: Tenant | None = Relationship(back_populates="users")
    role: str = Field(max_length=20, default="user")  # "superadmin", "tenant_admin", "user"
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    subscription: list["UserSubscription"] = Relationship(back_populates="user", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    role: str


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
    tenant_id: uuid.UUID | None = None
    role: str = "user"


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# Shared properties for SubscriptionPlan
class SubscriptionPlanBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(ge=0)
    duration_days: int = Field(gt=0)
    features: list[str] = Field(default=[], sa_column=Column(JSON))
    is_active: bool = Field(default=True)


# Properties to receive on plan creation
class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


# Properties to receive on plan update
class SubscriptionPlanUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, ge=0)
    duration_days: int | None = Field(default=None, gt=0)
    features: list[str] | None = Field(default=None, sa_column=Column(JSON))
    is_active: bool | None = None


# Database model for subscription plans
class SubscriptionPlan(SubscriptionPlanBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# Properties to return via API
class SubscriptionPlanPublic(SubscriptionPlanBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SubscriptionPlansPublic(SQLModel):
    data: list[SubscriptionPlanPublic]
    count: int


# Shared properties for UserSubscription
class UserSubscriptionBase(SQLModel):
    plan_id: uuid.UUID = Field(foreign_key="subscriptionplan.id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    status: str = Field(default="active", max_length=50)


# Properties to receive on subscription creation
class UserSubscriptionCreate(SQLModel):
    plan_id: uuid.UUID


# Properties to receive on subscription update
class UserSubscriptionUpdate(SQLModel):
    status: str | None = Field(default=None, max_length=50)


# Database model for user subscriptions
class UserSubscription(UserSubscriptionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User | None = Relationship(back_populates="subscription")
    plan: SubscriptionPlan | None = Relationship()


# Properties to return via API
class UserSubscriptionPublic(UserSubscriptionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    plan: SubscriptionPlanPublic



# API Key Management
class TenantApiKey(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", ondelete="CASCADE")
    tenant: Tenant = Relationship(back_populates="api_keys")
    provider: str = Field(max_length=50)  # e.g., "openai"
    encrypted_key: str = Field()  # Encrypted API key
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime | None = Field(default=None)

# Credit System
class CreditTransaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", ondelete="CASCADE")
    tenant: Tenant = Relationship(back_populates="credit_ledger")
    user_id: uuid.UUID | None = Field(foreign_key="user.id", nullable=True)
    user: "User" = Relationship()
    amount: float  # Positive for adding credits, negative for deductions
    description: str = Field(max_length=255)
    transaction_type: str = Field(max_length=20)  # "add", "deduct", "refund"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Invitation System
class TenantInvitation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", ondelete="CASCADE")
    tenant: Tenant = Relationship()
    email: EmailStr
    role: str = Field(default="user")
    token: str  # JWT token for invitation
    expires_at: datetime
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: bool = Field(default=False)

# Response models for API
class TenantCreate(TenantBase):
    pass

class TenantUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None

class TenantPublic(TenantBase):
    id: uuid.UUID
    created_at: datetime

class TenantWithBalancePublic(TenantPublic):
    credit_balance: float

class TenantApiKeyCreate(SQLModel):
    provider: str = Field(max_length=50)
    api_key: str

class TenantApiKeyPublic(SQLModel):
    id: uuid.UUID
    provider: str
    is_active: bool
    created_at: datetime
    last_used: datetime | None

class CreditTransactionCreate(SQLModel):
    amount: float
    description: str = Field(max_length=255)

class CreditTransactionPublic(SQLModel):
    id: uuid.UUID
    amount: float
    description: str
    transaction_type: str
    created_at: datetime
    user_id: uuid.UUID | None

class TenantInvitationCreate(SQLModel):
    email: EmailStr
    role: str = Field(default="user")

class TenantInvitationPublic(SQLModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    expires_at: datetime
    created_at: datetime
    is_used: bool
    tenant_id: uuid.UUID

# Email Configuration for Tenants
class EmailConfigBase(SQLModel):
    smtp_host: str
    smtp_port: int = Field(default=587)
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool = Field(default=True)
    from_email: EmailStr
    from_name: str | None = Field(default=None, max_length=255)

class EmailConfig(EmailConfigBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tenant: "Tenant" = Relationship(back_populates="email_config")