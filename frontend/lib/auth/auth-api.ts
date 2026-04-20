import { httpClient } from "@/lib/api/http-client";
import { setAccessToken } from "@/lib/auth/token-store";
import type { AuthTokens, SessionUser, UserTenantMembership } from "@/lib/auth/session-types";

type TokenResponse = {
  access: string;
  token_type: string;
};

type LogoutResponse = {
  detail: string;
};

type NavigationFavoritesResponse = {
  favorites: string[];
};

function mapTokens(response: TokenResponse): AuthTokens {
  return {
    access: response.access,
    tokenType: response.token_type || "Bearer",
  };
}

export async function login(username: string, password: string): Promise<AuthTokens> {
  const payload = await httpClient.post<TokenResponse>(
    "/api/auth/v1/login/",
    { username, password },
    { includeCredentials: true, retryOnAuthFailure: false },
  );
  const tokens = mapTokens(payload);
  setAccessToken(tokens.access, tokens.tokenType);
  return tokens;
}

export async function refresh(): Promise<AuthTokens> {
  const payload = await httpClient.post<TokenResponse>(
    "/api/auth/v1/refresh/",
    undefined,
    { includeCredentials: true, retryOnAuthFailure: false },
  );
  const tokens = mapTokens(payload);
  setAccessToken(tokens.access, tokens.tokenType);
  return tokens;
}

export async function logout(): Promise<LogoutResponse> {
  return httpClient.post<LogoutResponse>(
    "/api/auth/v1/logout/",
    undefined,
    { auth: true, includeCredentials: true, retryOnAuthFailure: false },
  );
}

export async function getMe(tenantSlug: string): Promise<SessionUser> {
  return httpClient.get<SessionUser>("/api/accounts/v1/users/me/", {
    auth: true,
    tenantSlug,
    retryOnAuthFailure: false,
  });
}

export async function getMyTenants(): Promise<UserTenantMembership[]> {
  return httpClient.get<UserTenantMembership[]>("/api/accounts/v1/users/me/tenants/", {
    auth: true,
    retryOnAuthFailure: false,
  });
}

export async function getNavigationFavorites(): Promise<string[]> {
  const payload = await httpClient.get<NavigationFavoritesResponse>("/api/accounts/v1/users/me/navigation-favorites/", {
    auth: true,
    retryOnAuthFailure: false,
  });
  return payload.favorites;
}

export async function setNavigationFavorites(favorites: string[]): Promise<string[]> {
  const payload = await httpClient.put<NavigationFavoritesResponse>(
    "/api/accounts/v1/users/me/navigation-favorites/",
    { favorites },
    { auth: true, retryOnAuthFailure: false },
  );
  return payload.favorites;
}
