// frontend/src/services/tenant-service.ts
import { 
  Tenant, 
  TenantCreateInput, 
  TenantUpdateInput 
} from '@/types/tenant';

export const TenantService = {
  listTenants: async (): Promise<Tenant[]> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
    
  createTenant: async (data: TenantCreateInput): Promise<Tenant> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
    
  updateTenant: async ({ tenantId, data }: { tenantId: string; data: TenantUpdateInput }): Promise<Tenant> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
    
  deleteTenant: async (tenantId: string): Promise<{ message: string }> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
};