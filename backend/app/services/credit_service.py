from sqlmodel import Session, select, func
from fastapi import HTTPException
import uuid
from datetime import datetime

from app.models import CreditTransaction

class CreditService:
    def get_tenant_balance(self, session: Session, tenant_id: uuid.UUID) -> float:
        statement = select(func.sum(CreditTransaction.amount)).where(
            CreditTransaction.tenant_id == tenant_id
        )
        balance = session.exec(statement).one()
        return balance or 0
        
    def add_credits(
        self, 
        session: Session, 
        tenant_id: uuid.UUID, 
        amount: float, 
        description: str, 
        admin_id: uuid.UUID
    ) -> CreditTransaction:
        transaction = CreditTransaction(
            tenant_id=tenant_id,
            user_id=admin_id,
            amount=amount,  # Positive for adding
            description=description,
            transaction_type="add"
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
        
    def deduct_credits(
        self, 
        session: Session, 
        tenant_id: uuid.UUID, 
        amount: float, 
        description: str, 
        user_id: uuid.UUID
    ) -> CreditTransaction:
        # Check if tenant has enough credits
        balance = self.get_tenant_balance(session, tenant_id)
        if balance < amount:
            raise HTTPException(status_code=402, detail="Insufficient credits")
            
        transaction = CreditTransaction(
            tenant_id=tenant_id,
            user_id=user_id,
            amount=-amount,  # Negative for deduction
            description=description,
            transaction_type="deduct"
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
        
    def refund_transaction(
        self, 
        session: Session, 
        transaction_id: uuid.UUID
    ) -> CreditTransaction:
        transaction = session.get(CreditTransaction, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        refund = CreditTransaction(
            tenant_id=transaction.tenant_id,
            user_id=transaction.user_id,
            amount=-transaction.amount,  # Reverse the original amount
            description=f"Refund for transaction {transaction.id}",
            transaction_type="refund"
        )
        session.add(refund)
        session.commit()
        session.refresh(refund)
        return refund