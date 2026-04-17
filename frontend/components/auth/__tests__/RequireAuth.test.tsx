import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const replaceMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
  usePathname: () => "/audit",
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: vi.fn(),
}));

import RequireAuth from "@/components/auth/RequireAuth";
import { useAuth } from "@/hooks/use-auth";

describe("RequireAuth", () => {
  it("redirects unauthenticated users to login", async () => {
    vi.mocked(useAuth).mockReturnValue({
      status: "unauthenticated",
      user: null,
      roles: [],
      tenantSlug: "tenant-a",
      errorMessage: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      setTenant: vi.fn(),
      hasRole: vi.fn(),
      refreshSession: vi.fn(),
    });

    render(
      <RequireAuth>
        <p>secret</p>
      </RequireAuth>,
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login?next=%2Faudit");
    });
  });

  it("renders content for authenticated users", () => {
    vi.mocked(useAuth).mockReturnValue({
      status: "authenticated",
      user: null,
      roles: [],
      tenantSlug: "tenant-a",
      errorMessage: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      setTenant: vi.fn(),
      hasRole: vi.fn(),
      refreshSession: vi.fn(),
    });

    render(
      <RequireAuth>
        <p>sichtbar</p>
      </RequireAuth>,
    );

    expect(screen.getByText("sichtbar")).toBeInTheDocument();
  });
});
