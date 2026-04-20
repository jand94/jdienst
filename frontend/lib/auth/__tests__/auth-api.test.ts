import { beforeEach, describe, expect, it, vi } from "vitest";

const { postMock, getMock, putMock, setAccessTokenMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
  getMock: vi.fn(),
  putMock: vi.fn(),
  setAccessTokenMock: vi.fn(),
}));

vi.mock("@/lib/api/http-client", () => ({
  httpClient: {
    post: postMock,
    get: getMock,
    put: putMock,
  },
}));

vi.mock("@/lib/auth/token-store", () => ({
  setAccessToken: setAccessTokenMock,
}));

import { getMe, getMyTenants, getNavigationFavorites, login, logout, refresh, setNavigationFavorites } from "@/lib/auth/auth-api";

describe("auth-api", () => {
  beforeEach(() => {
    postMock.mockReset();
    getMock.mockReset();
    putMock.mockReset();
    setAccessTokenMock.mockReset();
  });

  it("maps login token response and stores access token", async () => {
    postMock.mockResolvedValue({ access: "access-token", token_type: "Bearer" });

    const result = await login("max", "secret");

    expect(postMock).toHaveBeenCalledWith(
      "/api/auth/v1/login/",
      { username: "max", password: "secret" },
      { includeCredentials: true, retryOnAuthFailure: false },
    );
    expect(setAccessTokenMock).toHaveBeenCalledWith("access-token", "Bearer");
    expect(result).toEqual({ access: "access-token", tokenType: "Bearer" });
  });

  it("refreshes tokens and updates token store", async () => {
    postMock.mockResolvedValue({ access: "new-access", token_type: "Bearer" });

    const result = await refresh();

    expect(postMock).toHaveBeenCalledWith(
      "/api/auth/v1/refresh/",
      undefined,
      { includeCredentials: true, retryOnAuthFailure: false },
    );
    expect(setAccessTokenMock).toHaveBeenCalledWith("new-access", "Bearer");
    expect(result.access).toBe("new-access");
  });

  it("loads me endpoint with tenant header", async () => {
    getMock.mockResolvedValue({ id: 1, username: "max" });

    await getMe("tenant-a");

    expect(getMock).toHaveBeenCalledWith("/api/accounts/v1/users/me/", {
      auth: true,
      tenantSlug: "tenant-a",
      retryOnAuthFailure: false,
    });
  });

  it("calls logout with auth and credentials", async () => {
    postMock.mockResolvedValue({ detail: "ok" });

    await logout();

    expect(postMock).toHaveBeenCalledWith(
      "/api/auth/v1/logout/",
      undefined,
      { auth: true, includeCredentials: true, retryOnAuthFailure: false },
    );
  });

  it("loads my tenants without explicit tenant header", async () => {
    getMock.mockResolvedValue([{ tenant_slug: "tenant-a" }]);

    await getMyTenants();

    expect(getMock).toHaveBeenCalledWith("/api/accounts/v1/users/me/tenants/", {
      auth: true,
      retryOnAuthFailure: false,
    });
  });

  it("loads navigation favorites for authenticated user", async () => {
    getMock.mockResolvedValue({ favorites: ["/settings"] });

    const result = await getNavigationFavorites();

    expect(result).toEqual(["/settings"]);
    expect(getMock).toHaveBeenCalledWith("/api/accounts/v1/users/me/navigation-favorites/", {
      auth: true,
      retryOnAuthFailure: false,
    });
  });

  it("updates navigation favorites for authenticated user", async () => {
    putMock.mockResolvedValue({ favorites: ["/audit", "/settings"] });

    const result = await setNavigationFavorites(["/audit", "/settings"]);

    expect(result).toEqual(["/audit", "/settings"]);
    expect(putMock).toHaveBeenCalledWith(
      "/api/accounts/v1/users/me/navigation-favorites/",
      { favorites: ["/audit", "/settings"] },
      { auth: true, retryOnAuthFailure: false },
    );
  });
});
