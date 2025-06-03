import httpx
from fastapi import HTTPException
from sqlmodel import Session
import uuid
import json
from typing import Dict, Any

from app.services.api_key_service import ApiKeyService
from app.services.credit_service import CreditService

class AiApiProxyService:
    def __init__(self, api_key_service: ApiKeyService, credit_service: CreditService):
        self.api_key_service = api_key_service
        self.credit_service = credit_service
        
    def _estimate_tokens(self, payload: Dict[str, Any]) -> int:
        """Estimate number of tokens in the request"""
        # Simplified estimation - in production, use tiktoken or similar
        if "messages" in payload:
            return sum(len(json.dumps(msg)) // 4 for msg in payload["messages"])
        elif "prompt" in payload:
            return len(payload["prompt"]) // 4
        return 100  # Default fallback
        
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost in credits based on model and tokens"""
        # Simplified cost calculation - adjust with your actual rates
        rates = {
            "gpt-3.5-turbo": 0.0015 / 1000,
            "gpt-4": 0.03 / 1000,
            "gpt-4-turbo": 0.01 / 1000,
        }
        rate = rates.get(model, 0.002 / 1000)  # Default fallback rate
        return tokens * rate * 100  # Convert to credits (e.g., 1 USD = 100 credits)
        
    async def proxy_openai_request(
        self, 
        session: Session, 
        tenant_id: uuid.UUID, 
        user_id: uuid.UUID, 
        endpoint: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Get tenant API key
        api_key = self.api_key_service.get_active_key_for_tenant(
            session, tenant_id, "openai"
        )
        if not api_key:
            raise HTTPException(
                status_code=403, 
                detail="No active OpenAI API key for this tenant"
            )
            
        # Calculate estimated cost
        model = payload.get("model", "gpt-3.5-turbo")
        tokens = self._estimate_tokens(payload)
        cost = self._calculate_cost(model, tokens)
        
        # Pre-deduct credits from the user's balance (we can refund if the request fails)
        transaction = self.credit_service.deduct_user_credits(
            session,
            tenant_id,
            cost,
            f"OpenAI API request: {model}",
            user_id
        )
        
        # Make API request
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.openai.com/v1/{endpoint}",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
            if response.status_code != 200:
                # If request fails, refund credits
                self.credit_service.refund_transaction(session, transaction.id)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
                
            result = response.json()
            
            # Calculate actual usage and adjust if needed
            if "usage" in result:
                actual_tokens = result["usage"].get("total_tokens", tokens)
                actual_cost = self._calculate_cost(model, actual_tokens)
                
                # If actual cost differs significantly from estimate, adjust
                if abs(actual_cost - cost) > 0.01:
                    adjustment = cost - actual_cost
                    self.credit_service.add_credits(
                        session,
                        tenant_id,
                        adjustment,
                        f"Cost adjustment for transaction {transaction.id}",
                        user_id
                    )
                    
            return result
            
        except Exception as e:
            # Refund on any exception
            self.credit_service.refund_transaction(session, transaction.id)
            raise HTTPException(
                status_code=500,
                detail=f"Error proxying request to OpenAI: {str(e)}"
            )