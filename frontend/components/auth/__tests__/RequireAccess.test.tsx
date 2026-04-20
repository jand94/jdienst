import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/hooks/use-auth", () => ({
  useAuth: vi.fn(),
}));

import RequireAccess from "@/components/auth/RequireAccess";
import { useAuth } from "@/hooks/use-auth";

describe("RequireAccess", () => {
  it("renders fallback when permission is missing", () => {
    vi.mocked(useAuth).mockReturnValue({
      status: "authenticated",
      user: null,
      roles: [],
      permissions: ["dashboard.view"],
      featureFlags: ["dynamic_authz_navigation"],
      tenantSlug: "tenant-a",
      errorMessage: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      setTenant: vi.fn(),
      hasRole: vi.fn(),
      can: vi.fn((permission: string) => permission === "dashboard.view"),
      canAny: vi.fn(() => false),
      hasFeature: vi.fn(),
      navigationFavorites: [],
      toggleNavigationFavorite: vi.fn(),
      reorderNavigationFavorites: vi.fn(),
      refreshSession: vi.fn(),
    });

    render(
      <RequireAccess permissions={["audit.ops.manage"]}>
        <p>sichtbar</p>
      </RequireAccess>,
    );

    expect(screen.queryByText("sichtbar")).not.toBeInTheDocument();
    expect(screen.getByText("Keine Berechtigung fuer diesen Bereich.")).toBeInTheDocument();
  });

  it("renders children when at least one permission matches", () => {
    vi.mocked(useAuth).mockReturnValue({
      status: "authenticated",
      user: null,
      roles: [],
      permissions: ["audit.events.read"],
      featureFlags: ["dynamic_authz_navigation"],
      tenantSlug: "tenant-a",
      errorMessage: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      setTenant: vi.fn(),
      hasRole: vi.fn(),
      can: vi.fn((permission: string) => permission === "audit.events.read"),
      canAny: vi.fn((...permissions: string[]) => permissions.includes("audit.events.read")),
      hasFeature: vi.fn(),
      navigationFavorites: [],
      toggleNavigationFavorite: vi.fn(),
      reorderNavigationFavorites: vi.fn(),
      refreshSession: vi.fn(),
    });

    render(
      <RequireAccess permissions={["audit.events.read", "audit.ops.manage"]}>
        <p>sichtbar</p>
      </RequireAccess>,
    );

    expect(screen.getByText("sichtbar")).toBeInTheDocument();
  });
});
