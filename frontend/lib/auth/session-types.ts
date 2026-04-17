export type AppRole = "staff" | "audit_reader" | "audit_operator";

export type SessionUser = {
  id: number | string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  roles?: string[];
};

export type UserTenantMembership = {
  tenant_id: string;
  tenant_slug: string;
  tenant_name: string;
  role: string;
  is_active: boolean;
};

export type AuthTokens = {
  access: string;
  tokenType: string;
};

export type SessionStatus = "loading" | "authenticated" | "unauthenticated" | "error";

export type SessionSnapshot = {
  status: SessionStatus;
  user: SessionUser | null;
  roles: AppRole[];
  tenantSlug: string;
  errorMessage: string | null;
};

export type LoginCredentials = {
  username: string;
  password: string;
};
