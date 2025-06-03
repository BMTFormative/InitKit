import uuid
from typing import Any

from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate,SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate, UserSubscription, UserSubscriptionCreate, UserSubscriptionUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_subscription_plan(*, session: Session, plan_create: SubscriptionPlanCreate) -> SubscriptionPlan:
    db_plan = SubscriptionPlan.model_validate(plan_create)
    session.add(db_plan)
    session.commit()
    session.refresh(db_plan)
    return db_plan


def update_subscription_plan(*, session: Session, db_plan: SubscriptionPlan, plan_update: SubscriptionPlanUpdate) -> SubscriptionPlan:
    plan_data = plan_update.model_dump(exclude_unset=True)
    db_plan.sqlmodel_update(plan_data)
    db_plan.updated_at = datetime.utcnow()
    session.add(db_plan)
    session.commit()
    session.refresh(db_plan)
    return db_plan


def get_subscription_plans(*, session: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> list[SubscriptionPlan]:
    statement = select(SubscriptionPlan)
    if active_only:
        statement = statement.where(SubscriptionPlan.is_active == True)
    statement = statement.offset(skip).limit(limit)
    plans = session.exec(statement).all()
    return plans


def create_user_subscription(*, session: Session, user_id: uuid.UUID, plan_id: uuid.UUID) -> UserSubscription:
    # Get the plan to calculate end date
    plan = session.get(SubscriptionPlan, plan_id)
    if not plan:
        raise ValueError("Subscription plan not found")
    
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan.duration_days)
    
    db_subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        status="active"
    )
    session.add(db_subscription)
    session.commit()
    session.refresh(db_subscription)
    return db_subscription


def get_user_subscription(*, session: Session, user_id: uuid.UUID) -> UserSubscription | None:
    statement = select(UserSubscription).where(
        UserSubscription.user_id == user_id,
        UserSubscription.status == "active"
    )
    subscription = session.exec(statement).first()
    return subscription


def update_user_subscription(*, session: Session, db_subscription: UserSubscription, subscription_update: UserSubscriptionUpdate) -> UserSubscription:
    subscription_data = subscription_update.model_dump(exclude_unset=True)
    db_subscription.sqlmodel_update(subscription_data)
    session.add(db_subscription)
    session.commit()
    session.refresh(db_subscription)
    return db_subscription