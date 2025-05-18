// frontend/src/services/tenant-user-service.ts
import { 
  TenantUser, 
  TenantInvitation,
  InvitationCreateInput 
} from '@/types/tenant';

export const TenantUserService = {
  listTenantUsers: async (tenantId: string): Promise<TenantUser[]> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/users`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
    
  listInvitations: async (tenantId: string): Promise<TenantInvitation[]> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/users/invitations`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
    
  createInvitation: async ({ tenantId, data }: { tenantId: string; data: InvitationCreateInput }): Promise<TenantInvitation> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/users/invitations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
    
  deleteInvitation: async ({ tenantId, invitationId }: { tenantId: string; invitationId: string }): Promise<{ message: string }> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/users/invitations/${invitationId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
};