// frontend/src/services/email-config-service.ts
import { EmailConfig } from '@/types/tenant';

export const EmailConfigService = {
  getEmailConfig: async (tenantId: string): Promise<EmailConfig | null> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/email-config`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    .then(res => res.status === 404 ? null : res.json())
    .catch(() => null),
    
  saveEmailConfig: async ({ tenantId, data }: { tenantId: string; data: EmailConfig }): Promise<EmailConfig> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/email-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    }).then(res => res.json()),
    
  testEmailConfig: async (tenantId: string): Promise<{ message: string }> => 
    fetch(`${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/email-config/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).then(res => res.json()),
};