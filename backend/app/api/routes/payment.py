from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.api.deps import SessionDep, CurrentUser
from app.models import PaymentMethod, PaymentMethodCreate, PaymentMethodPublic, Message
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["payment"])
payment_service = PaymentService()

@router.post("/payment-methods", response_model=PaymentMethodPublic)
def create_payment_method(
    session: SessionDep,
    current_user: CurrentUser,
    payment_method_data: PaymentMethodCreate
) -> PaymentMethod:
    """Add payment method for user"""
    return payment_service.create_payment_method(
        session,
        current_user.id,
        payment_method_data.stripe_payment_method_id
    )

@router.get("/payment-methods", response_model=List[PaymentMethodPublic])
def list_payment_methods(
    session: SessionDep,
    current_user: CurrentUser
) -> List[PaymentMethod]:
    """List user's payment methods"""
    statement = select(PaymentMethod).where(
        PaymentMethod.user_id == current_user.id
    )
    return session.exec(statement).all()