import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { refreshMock, getMeMock, getMyTenantsMock, httpSetRefreshHandlerMock } = vi.hoisted(() => ({
  refreshMock: vi.fn(),
  getMeMock: vi.fn(),
  getMyTenantsMock: vi.fn(),
  httpSetRefreshHandlerMock: vi.fn(),
}));

vi.mock("@/lib/auth/auth-api", () => ({
  refresh: refreshMock,
  getMe: getMeMock,
  getMyTenants: getMyTenantsMock,
  login: vi.fn(),
  logout: vi.fn(),
}));

vi.mock("@/lib/api/http-client", () => ({
  httpClient: {
    setRefreshHandler: httpSetRefreshHandlerMock,
  },
}));

vi.mock("@/lib/auth/tenant-store", () => ({
  getTenantSlug: vi.fn(() => "tenant-a"),
  setTenantSlug: vi.fn(),
}));

vi.mock("@/lib/auth/token-store", () => ({
  clearAccessToken: vi.fn(),
}));

import { AuthProvider, AuthContext } from "@/components/auth/AuthProvider";

function Consumer() {
  return (
    <AuthContext.Consumer>
      {(value) => (
        <div>
          <p>{value?.status ?? "none"}</p>
          <p>{value?.can("audit.events.read") ? "can-audit-read" : "cannot-audit-read"}</p>
          <p>{value?.hasFeature("dynamic_authz_navigation") ? "feature-dynamic-on" : "feature-dynamic-off"}</p>
        </div>
      )}
    </AuthContext.Consumer>
  );
}

describe("AuthProvider", () => {
  it("boots into authenticated status when refresh and me succeed", async () => {
    refreshMock.mockResolvedValue(undefined);
    getMyTenantsMock.mockResolvedValue([
      {
        tenant_id: "tenant-id",
        tenant_slug: "tenant-a",
        tenant_name: "Tenant A",
        role: "member",
        is_active: true,
      },
    ]);
    getMeMock.mockResolvedValue({
      id: 1,
      username: "max",
      email: "max@example.org",
      first_name: "Max",
      last_name: "Mustermann",
      is_active: true,
      is_staff: true,
      date_joined: "2024-01-01T00:00:00Z",
      permissions: ["audit.events.read", "settings.view"],
      feature_flags: ["dynamic_authz_navigation"],
      current_tenant_role: "admin",
    });

    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("authenticated")).toBeInTheDocument();
    });
    expect(screen.getByText("can-audit-read")).toBeInTheDocument();
    expect(screen.getByText("feature-dynamic-on")).toBeInTheDocument();
    expect(getMyTenantsMock).toHaveBeenCalledTimes(1);
    expect(getMeMock).toHaveBeenCalledWith("tenant-a");
    expect(httpSetRefreshHandlerMock).toHaveBeenCalledTimes(1);
  });
});
