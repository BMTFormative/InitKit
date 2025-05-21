// Service for managing tenant API keys across all tenants (super-admin only)
import { AdminTenantApiKey } from '@/types/tenant';

const BASE_URL = `${import.meta.env.VITE_API_URL}/api/v1/admin/tenant-api-keys`;

export const AdminTenantApiKeyService = {
  listApiKeys: async (): Promise<AdminTenantApiKey[]> =>
    fetch(BASE_URL, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || 'Failed to fetch tenant API keys');
      }
      return res.json();
    }),
};