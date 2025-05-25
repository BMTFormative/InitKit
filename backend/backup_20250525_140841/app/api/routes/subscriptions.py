import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select, SQLModel, Field

from app import crud
from app.api.deps import (
    CurrentUser,
    CurrentUserWithTenant,
    TenantAdminUser,
    TenantFromPath,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    SubscriptionPlan,
    SubscriptionPlanCreate,
    SubscriptionPlanPublic,
    SubscriptionPlanUpdate,
    SubscriptionPlansPublic,
    User,
    UserSubscription,
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    UserSubscriptionPublic,
)
from app.services.credit_service import CreditService

router = APIRouter()
credit_service = CreditService()
 
# Schema for bulk subscribing users in a tenant
class TenantBulkSubscriptionCreate(SQLModel):
    plan_id: uuid.UUID = Field(..., description="Subscription plan to apply to all users in tenant")

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
    # Allocate initial credit to user based on plan's credit limit
    plan = session.get(SubscriptionPlan, subscription_in.plan_id)
    try:
        credit_limit = getattr(plan, 'credit_limit', 0) or 0
    except Exception:
        credit_limit = 0
    if credit_limit > 0 and current_user.tenant_id:
        credit_service.add_credits(
            session,
            current_user.tenant_id,
            credit_limit,
            f"Initial credit for plan '{plan.name}'",
            current_user.id
        )
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

# Subscribe a specific user (tenant-admin or super-admin)
@router.post("/subscribe/{user_id}", response_model=UserSubscriptionPublic)
def subscribe_user_for_admin(
    *,
    session: SessionDep,
    current_data: CurrentUserWithTenant,
    user_id: uuid.UUID,
    subscription_in: UserSubscriptionCreate,
) -> Any:
    """
    Subscribe a specific user to a plan (tenant-admin or super-admin).
    """
    current_user, tenant_id, role = current_data
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # Permission checks
    if role == "superadmin":
        pass
    elif role == "tenant_admin":
        if not tenant_id or str(target.tenant_id) != str(tenant_id):
            raise HTTPException(status_code=403, detail="Not enough privileges")
    else:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    # Validate plan
    plan = session.get(SubscriptionPlan, subscription_in.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive plan")
    # Cancel existing subscription
    existing = crud.get_user_subscription(session=session, user_id=user_id)
    if existing:
        existing.status = "cancelled"
        session.add(existing)
    # Create subscription
    subscription = crud.create_user_subscription(
        session=session,
        user_id=user_id,
        plan_id=subscription_in.plan_id,
    )
    session.refresh(subscription)
    # Allocate credits to target user
    credit_limit = getattr(plan, 'credit_limit', 0) or 0
    if credit_limit > 0 and target.tenant_id:
        credit_service.add_credits(
            session,
            target.tenant_id,
            credit_limit,
            f"Initial credit for plan '{plan.name}'",
            user_id,
        )
    return subscription

# Bulk subscribe all users in a tenant
@router.post("/tenants/{tenant_id}/bulk-subscribe", response_model=List[UserSubscriptionPublic])
def bulk_subscribe_tenant_users(
    *,
    session: SessionDep,
    tenant: TenantFromPath,
    admin_data: TenantAdminUser,
    data: TenantBulkSubscriptionCreate,
) -> Any:
    """
    Subscribe all users in a tenant to a plan (tenant-admin or super-admin).
    """
    admin_user, tenant_id = admin_data
    # Validate plan
    plan = session.get(SubscriptionPlan, data.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive plan")
    # Get all users in tenant
    users = session.exec(select(User).where(User.tenant_id == tenant_id)).all()
    subscriptions: list[UserSubscription] = []
    for u in users:
        # Cancel existing
        existing = crud.get_user_subscription(session=session, user_id=u.id)
        if existing:
            existing.status = "cancelled"
            session.add(existing)
        # Create new subscription
        sub = crud.create_user_subscription(
            session=session,
            user_id=u.id,
            plan_id=data.plan_id,
        )
        session.refresh(sub)
        # Allocate credits
        credit_limit = getattr(plan, 'credit_limit', 0) or 0
        if credit_limit > 0:
            credit_service.add_credits(
                session,
                tenant_id,
                credit_limit,
                f"Initial credit for plan '{plan.name}' (bulk)",
                u.id,
            )
        subscriptions.append(sub)
    return subscriptions