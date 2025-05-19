// frontend/src/types/tenant.ts
import { UserPublic as ClientUserPublic } from '@/client';

export interface UserWithTenant extends ClientUserPublic {
  tenant_id?: string;
  role?: string;
}

export interface Tenant {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  credit_balance?: number;
}

export interface TenantCreateInput {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface TenantUpdateInput {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface TenantUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
}

export interface TenantInvitation {
  id: string;
  email: string;
  role: string;
  expires_at: string;
  created_at: string;
  is_used: boolean;
  tenant_id: string;
}

export interface ApiKey {
  id: string;
  provider: string;
  is_active: boolean;
  created_at: string;
  last_used: string | null;
}

export interface ApiKeyCreateInput {
  provider: string;
  api_key: string;
}

export interface CreditTransaction {
  id: string;
  amount: number;
  description: string;
  transaction_type: string;
  created_at: string;
  user_id: string | null;
}

export interface CreditAddInput {
  amount: number;
  description: string;
}

export interface InvitationCreateInput {
  email: string;
  role: string;
}

export interface UserCreateInput {
  email: string;
  password: string;
  full_name?: string;
}

export interface AcceptInvitationInput {
  token: string;
  user_data: UserCreateInput;
}

export interface EmailConfig {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  smtp_use_tls: boolean;
  from_email: string;
  from_name?: string;
}