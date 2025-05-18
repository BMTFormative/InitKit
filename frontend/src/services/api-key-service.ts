// frontend/src/services/api-key-service.ts
import { ApiKey, ApiKeyCreateInput } from '@/types/tenant';

export const ApiKeyService = {
  listApiKeys: async (tenantId: string): Promise<ApiKey[]> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/api-keys`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
    
  createApiKey: async ({ tenantId, data }: { tenantId: string; data: ApiKeyCreateInput }): Promise<ApiKey> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/api-keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
    
  deleteApiKey: async ({ tenantId, keyId }: { tenantId: string; keyId: string }): Promise<{ message: string }> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/api-keys/${keyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
};