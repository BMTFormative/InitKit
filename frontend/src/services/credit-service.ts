// frontend/src/services/credit-service.ts
import { CreditTransaction, CreditAddInput } from '@/types/tenant';

export const CreditService = {
  listTransactions: async (tenantId: string): Promise<CreditTransaction[]> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/credits`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
    
  addCredits: async ({ tenantId, data }: { tenantId: string; data: CreditAddInput }): Promise<CreditTransaction> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/credits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
};