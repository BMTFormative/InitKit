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


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    subscription: list["UserSubscription"] = Relationship(back_populates="user", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


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