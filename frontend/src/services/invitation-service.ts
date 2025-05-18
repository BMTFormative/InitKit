// frontend/src/services/invitation-service.ts
import { AcceptInvitationInput, TenantUser } from '@/types/tenant';

export const InvitationService = {
  acceptInvitation: async (data: AcceptInvitationInput): Promise<TenantUser> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/login/accept-invitation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
};