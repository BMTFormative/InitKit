// Service for managing global API keys (super-admin only)
import { ApiKey, ApiKeyCreateInput } from '@/types/tenant';

const BASE_URL = `${import.meta.env.VITE_API_URL}/api/v1/admin/api-keys`;

export const GlobalApiKeyService = {
  listApiKeys: async (): Promise<ApiKey[]> =>
    fetch(BASE_URL, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    }).then(async res => {
      if (!res.ok) throw new Error('Failed to fetch global API keys');
      return res.json();
    }),

  createApiKey: async (data: ApiKeyCreateInput): Promise<ApiKey> =>
    fetch(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to create API key');
      }
      return res.json();
    }),

  deleteApiKey: async (keyId: string): Promise<{ message: string }> =>
    fetch(`${BASE_URL}/${keyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    }).then(async res => {
      if (!res.ok) throw new Error('Failed to delete API key');
      return res.json();
    }),

  updateApiKeyStatus: async (keyId: string, isActive: boolean): Promise<ApiKey> =>
    fetch(`${BASE_URL}/${keyId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({ is_active: isActive }),
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to update API key status');
      }
      return res.json();
    }),
};