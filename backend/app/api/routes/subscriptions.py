import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Message,
    SubscriptionPlan,
    SubscriptionPlanCreate,
    SubscriptionPlanPublic,
    SubscriptionPlanUpdate,
    SubscriptionPlansPublic,
    UserSubscription,
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    UserSubscriptionPublic,
)

router = APIRouter()

# Public endpoints for subscription plans
@router.get("/plans", response_model=SubscriptionPlansPublic)
def list_subscription_plans(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> Any:
    """
    List all available subscription plans.
    """
    plans = crud.get_subscription_plans(
        session=session, skip=skip, limit=limit, active_only=active_only
    )
    
    count_statement = select(func.count()).select_from(SubscriptionPlan)
    if active_only:
        count_statement = count_statement.where(SubscriptionPlan.is_active == True)
    count = session.exec(count_statement).one()
    
    return SubscriptionPlansPublic(data=plans, count=count)


# Admin endpoints for plan management
@router.post(
    "/plans",
    response_model=SubscriptionPlanPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_subscription_plan(
    *,
    session: SessionDep,
    plan_in: SubscriptionPlanCreate,
) -> Any:
    """
    Create a new subscription plan. Admin only.
    """
    plan = crud.create_subscription_plan(session=session, plan_create=plan_in)
    return plan


@router.patch(
    "/plans/{plan_id}",
    response_model=SubscriptionPlanPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_subscription_plan(
    *,
    session: SessionDep,
    plan_id: uuid.UUID,
    plan_in: SubscriptionPlanUpdate,
) -> Any:
    """
    Update a subscription plan. Admin only.
    """
    plan = session.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan = crud.update_subscription_plan(session=session, db_plan=plan, plan_update=plan_in)
    return plan


@router.delete(
    "/plans/{plan_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_subscription_plan(
    *,
    session: SessionDep,
    plan_id: uuid.UUID,
) -> Message:
    """
    Delete a subscription plan. Admin only.
    """
    plan = session.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    session.delete(plan)
    session.commit()
    return Message(message="Plan deleted successfully")


# User subscription endpoints
@router.post("/subscribe", response_model=UserSubscriptionPublic)
def subscribe_to_plan(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    subscription_in: UserSubscriptionCreate,
) -> Any:
    """
    Subscribe to a plan or change current plan.
    """
    # Check if plan exists and is active
    plan = session.get(SubscriptionPlan, subscription_in.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive plan")
    
    # Check if user already has an active subscription
    existing_subscription = crud.get_user_subscription(
        session=session, user_id=current_user.id
    )
    
    if existing_subscription:
        # Cancel existing subscription
        existing_subscription.status = "cancelled"
        session.add(existing_subscription)
    
    # Create new subscription
    subscription = crud.create_user_subscription(
        session=session,
        user_id=current_user.id,
        plan_id=subscription_in.plan_id
    )
    
    session.refresh(subscription)
    return subscription


@router.get("/my-subscription", response_model=UserSubscriptionPublic | None)
def get_my_subscription(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get current user's active subscription.
    """
    subscription = crud.get_user_subscription(
        session=session, user_id=current_user.id
    )
    return subscription


@router.patch("/subscription/{subscription_id}", response_model=UserSubscriptionPublic)
def update_subscription(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    subscription_id: uuid.UUID,
    subscription_in: UserSubscriptionUpdate,
) -> Any:
    """
    Update subscription (cancel or change status).
    """
    subscription = session.get(UserSubscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    subscription = crud.update_user_subscription(
        session=session,
        db_subscription=subscription,
        subscription_update=subscription_in
    )
    return subscription