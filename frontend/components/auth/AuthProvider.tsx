"use client";

import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import { httpClient } from "@/lib/api/http-client";
import { hasAnyPermission, hasFeatureFlag, hasPermission } from "@/lib/auth/access-control";
import { deriveRoles, hasAnyRole } from "@/lib/auth/role-mapping";
import { getMe, getMyTenants, login, logout, refresh, setNavigationFavorites } from "@/lib/auth/auth-api";
import { clearAccessToken } from "@/lib/auth/token-store";
import { getTenantSlug, setTenantSlug as persistTenantSlug } from "@/lib/auth/tenant-store";
import type { AppRole, FeatureFlag, LoginCredentials, SessionSnapshot, SessionUser } from "@/lib/auth/session-types";

type AuthContextValue = SessionSnapshot & {
  signIn: (credentials: LoginCredentials) => Promise<void>;
  signOut: () => Promise<void>;
  setTenant: (tenantSlug: string) => void;
  hasRole: (...roles: AppRole[]) => boolean;
  can: (permission: string) => boolean;
  canAny: (...permissions: string[]) => boolean;
  hasFeature: (featureFlag: FeatureFlag | string) => boolean;
  navigationFavorites: string[];
  toggleNavigationFavorite: (href: string) => Promise<void>;
  reorderNavigationFavorites: (sourceHref: string, targetHref: string) => Promise<void>;
  refreshSession: () => Promise<void>;
};

const defaultSnapshot: SessionSnapshot = {
  status: "loading",
  user: null,
  roles: [],
  permissions: [],
  featureFlags: [],
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
    const resolvedPermissions = Array.from(new Set(user.permissions ?? []));
    const resolvedFeatureFlags = Array.from(new Set(user.feature_flags ?? []));
    setSnapshot({
      status: "authenticated",
      user,
      roles: resolvedRoles,
      permissions: resolvedPermissions,
      featureFlags: resolvedFeatureFlags,
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
          permissions: [],
          featureFlags: [],
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
          permissions: [],
          featureFlags: [],
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
        permissions: [],
        featureFlags: [],
        tenantSlug: prev.tenantSlug,
        errorMessage: null,
      }));
    }
  }, []);

  const setTenant = useCallback((tenantSlug: string) => {
    persistTenantSlug(tenantSlug);
    setSnapshot((prev) => ({ ...prev, tenantSlug: tenantSlug.trim() }));
  }, []);

  const saveNavigationFavorites = useCallback(async (favorites: string[]) => {
    const savedFavorites = await setNavigationFavorites(favorites);
    setSnapshot((prev) => {
      if (prev.status !== "authenticated" || !prev.user) {
        return prev;
      }
      return {
        ...prev,
        user: {
          ...prev.user,
          navigation_favorites: savedFavorites,
        },
      };
    });
  }, []);

  const contextValue = useMemo<AuthContextValue>(
    () => ({
      ...snapshot,
      signIn,
      signOut,
      setTenant,
      refreshSession,
      hasRole: (...roles: AppRole[]) => hasAnyRole(snapshot.roles, roles),
      can: (permission: string) => hasPermission(snapshot.permissions, permission),
      canAny: (...permissions: string[]) => hasAnyPermission(snapshot.permissions, permissions),
      hasFeature: (featureFlag: FeatureFlag | string) => hasFeatureFlag(snapshot.featureFlags, featureFlag),
      navigationFavorites: snapshot.user?.navigation_favorites ?? [],
      toggleNavigationFavorite: async (href: string) => {
        if (snapshot.status !== "authenticated" || !snapshot.user) {
          return;
        }
        const normalizedHref = href.trim();
        if (!normalizedHref.startsWith("/")) {
          throw new Error("Favoritenpfad muss mit '/' beginnen.");
        }
        const current = snapshot.user.navigation_favorites ?? [];
        const exists = current.includes(normalizedHref);
        const nextFavorites = exists ? current.filter((item) => item !== normalizedHref) : [...current, normalizedHref];
        await saveNavigationFavorites(nextFavorites);
      },
      reorderNavigationFavorites: async (sourceHref: string, targetHref: string) => {
        if (snapshot.status !== "authenticated" || !snapshot.user) {
          return;
        }
        const current = snapshot.user.navigation_favorites ?? [];
        const sourceIndex = current.indexOf(sourceHref);
        const targetIndex = current.indexOf(targetHref);
        if (sourceIndex < 0 || targetIndex < 0 || sourceIndex === targetIndex) {
          return;
        }
        const nextFavorites = [...current];
        const [movedItem] = nextFavorites.splice(sourceIndex, 1);
        nextFavorites.splice(targetIndex, 0, movedItem);
        await saveNavigationFavorites(nextFavorites);
      },
    }),
    [refreshSession, saveNavigationFavorites, setTenant, signIn, signOut, snapshot],
  );

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}
