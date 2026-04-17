"use client";

import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import { httpClient } from "@/lib/api/http-client";
import { deriveRoles, hasAnyRole } from "@/lib/auth/role-mapping";
import { getMe, getMyTenants, login, logout, refresh } from "@/lib/auth/auth-api";
import { clearAccessToken } from "@/lib/auth/token-store";
import { getTenantSlug, setTenantSlug as persistTenantSlug } from "@/lib/auth/tenant-store";
import type { AppRole, LoginCredentials, SessionSnapshot, SessionUser } from "@/lib/auth/session-types";

type AuthContextValue = SessionSnapshot & {
  signIn: (credentials: LoginCredentials) => Promise<void>;
  signOut: () => Promise<void>;
  setTenant: (tenantSlug: string) => void;
  hasRole: (...roles: AppRole[]) => boolean;
  refreshSession: () => Promise<void>;
};

const defaultSnapshot: SessionSnapshot = {
  status: "loading",
  user: null,
  roles: [],
  tenantSlug: "",
  errorMessage: null,
};

export const AuthContext = createContext<AuthContextValue | null>(null);

type AuthProviderProps = {
  children: React.ReactNode;
};

async function fetchAuthenticatedUser(tenantSlug: string): Promise<SessionUser> {
  return getMe(tenantSlug);
}

async function resolveTenantSlug(preferredTenantSlug?: string): Promise<string> {
  const memberships = await getMyTenants();
  if (memberships.length === 0) {
    throw new Error("Dem Benutzer ist kein aktiver Tenant zugeordnet.");
  }
  const preferred = preferredTenantSlug?.trim();
  const selected = preferred
    ? memberships.find((membership) => membership.tenant_slug === preferred)
    : undefined;
  const tenantSlug = selected?.tenant_slug ?? memberships[0].tenant_slug;
  persistTenantSlug(tenantSlug);
  return tenantSlug;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [snapshot, setSnapshot] = useState<SessionSnapshot>({
    ...defaultSnapshot,
    tenantSlug: getTenantSlug(),
  });

  const applyAuthenticatedUser = useCallback((user: SessionUser, tenantSlug: string) => {
    const resolvedRoles = deriveRoles(user);
    setSnapshot({
      status: "authenticated",
      user,
      roles: resolvedRoles,
      tenantSlug,
      errorMessage: null,
    });
  }, []);

  const refreshSession = useCallback(async () => {
    await refresh();
    const tenantSlug = await resolveTenantSlug(getTenantSlug());
    const me = await fetchAuthenticatedUser(tenantSlug);
    applyAuthenticatedUser(me, tenantSlug);
  }, [applyAuthenticatedUser]);

  useEffect(() => {
    httpClient.setRefreshHandler(async () => {
      await refresh();
    });
  }, []);

  useEffect(() => {
    let active = true;
    const bootstrap = async () => {
      try {
        await refreshSession();
      } catch {
        if (!active) {
          return;
        }
        clearAccessToken();
        setSnapshot((prev) => ({
          status: "unauthenticated",
          user: null,
          roles: [],
          tenantSlug: prev.tenantSlug,
          errorMessage: null,
        }));
      }
    };
    void bootstrap();

    return () => {
      active = false;
    };
  }, [refreshSession]);

  const signIn = useCallback(
    async (credentials: LoginCredentials) => {
      setSnapshot((prev) => ({ ...prev, status: "loading", errorMessage: null }));
      try {
        await login(credentials.username, credentials.password);
        const tenantSlug = await resolveTenantSlug(getTenantSlug());
        const me = await fetchAuthenticatedUser(tenantSlug);
        applyAuthenticatedUser(me, tenantSlug);
      } catch (error) {
        clearAccessToken();
        const message = error instanceof Error ? error.message : "Anmeldung fehlgeschlagen.";
        setSnapshot({
          status: "error",
          user: null,
          roles: [],
          tenantSlug: getTenantSlug(),
          errorMessage: message,
        });
        throw error;
      }
    },
    [applyAuthenticatedUser],
  );

  const signOut = useCallback(async () => {
    try {
      await logout();
    } finally {
      clearAccessToken();
      setSnapshot((prev) => ({
        status: "unauthenticated",
        user: null,
        roles: [],
        tenantSlug: prev.tenantSlug,
        errorMessage: null,
      }));
    }
  }, []);

  const setTenant = useCallback((tenantSlug: string) => {
    persistTenantSlug(tenantSlug);
    setSnapshot((prev) => ({ ...prev, tenantSlug: tenantSlug.trim() }));
  }, []);

  const contextValue = useMemo<AuthContextValue>(
    () => ({
      ...snapshot,
      signIn,
      signOut,
      setTenant,
      refreshSession,
      hasRole: (...roles: AppRole[]) => hasAnyRole(snapshot.roles, roles),
    }),
    [refreshSession, setTenant, signIn, signOut, snapshot],
  );

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}
