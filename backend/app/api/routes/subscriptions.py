# backend/app/api/routes/subscriptions.py (new file)

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Subscription,
    SubscriptionCreate,
    SubscriptionPublic,
    SubscriptionUpdate,
    SubscriptionsPublic,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/", response_model=SubscriptionsPublic)
def read_subscriptions(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve subscriptions.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Subscription)
        count = session.exec(count_statement).one()
        statement = select(Subscription).offset(skip).limit(limit)
        subscriptions = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Subscription)
            .where(Subscription.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Subscription)
            .where(Subscription.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        subscriptions = session.exec(statement).all()

    return SubscriptionsPublic(data=subscriptions, count=count)


@router.get("/{id}", response_model=SubscriptionPublic)
def read_subscription(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get subscription by ID.
    """
    subscription = session.get(Subscription, id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not current_user.is_superuser and (subscription.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return subscription


@router.post("/", response_model=SubscriptionPublic)
def create_subscription(
    *, session: SessionDep, current_user: CurrentUser, subscription_in: SubscriptionCreate
) -> Any:
    """
    Create new subscription.
    """
    subscription = Subscription.model_validate(subscription_in, update={"owner_id": current_user.id})
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


@router.put("/{id}", response_model=SubscriptionPublic)
def update_subscription(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    subscription_in: SubscriptionUpdate,
) -> Any:
    """
    Update a subscription.
    """
    subscription = session.get(Subscription, id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not current_user.is_superuser and (subscription.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = subscription_in.model_dump(exclude_unset=True)
    subscription.sqlmodel_update(update_dict)
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


@router.delete("/{id}")
def delete_subscription(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a subscription.
    """
    subscription = session.get(Subscription, id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not current_user.is_superuser and (subscription.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(subscription)
    session.commit()
    return Message(message="Subscription deleted successfully")