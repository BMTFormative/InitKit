import stripe
from sqlmodel import Session, select
from fastapi import HTTPException
import uuid

from app.models import PaymentMethod, PaymentTransaction, User, UserSubscription
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY  # Add to your config

class PaymentService:
    def create_payment_method(
        self, 
        session: Session, 
        user_id: uuid.UUID, 
        stripe_payment_method_id: str
    ) -> PaymentMethod:
        """Save payment method for user"""
        try:
            # Get payment method details from Stripe
            pm = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
            
            payment_method = PaymentMethod(
                user_id=user_id,
                stripe_payment_method_id=stripe_payment_method_id,
                card_last_four=pm.card.last4,
                card_brand=pm.card.brand,
                exp_month=pm.card.exp_month,
                exp_year=pm.card.exp_year,
                is_default=True  # First card is default
            )
            
            session.add(payment_method)
            session.commit()
            session.refresh(payment_method)
            return payment_method
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")

    def process_subscription_payment(
        self,
        session: Session,
        user_id: uuid.UUID,
        subscription_id: uuid.UUID,
        amount: float,
        payment_method_id: str
    ) -> PaymentTransaction:
        """Process payment for subscription"""
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                payment_method=payment_method_id,
                confirm=True,
                return_url=f"{settings.FRONTEND_HOST}/subscriptions"
            )
            
            # Save transaction
            transaction = PaymentTransaction(
                user_id=user_id,
                subscription_id=subscription_id,
                stripe_payment_intent_id=intent.id,
                amount=amount,
                status=intent.status
            )
            
            session.add(transaction)
            session.commit()
            return transaction
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")