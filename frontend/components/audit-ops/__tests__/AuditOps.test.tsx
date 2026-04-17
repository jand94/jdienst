import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

const { setupAuditRolesMock } = vi.hoisted(() => ({
  setupAuditRolesMock: vi.fn(),
}));

vi.mock("@/lib/audit/audit-ops-api", () => ({
  setupAuditRoles: setupAuditRolesMock,
}));

import AuditSetupRolesAction from "@/components/audit-ops/AuditSetupRolesAction";

describe("Audit Ops", () => {
  it("runs setup roles action", async () => {
    vi.stubGlobal("confirm", vi.fn(() => true));
    setupAuditRolesMock.mockResolvedValue({
      created_roles: 2,
      roles: ["audit_reader", "audit_operator"],
    });

    render(<AuditSetupRolesAction tenantSlug="tenant-a" />);

    await userEvent.click(screen.getByRole("button", { name: "Rollen synchronisieren" }));

    expect(setupAuditRolesMock).toHaveBeenCalledWith("tenant-a");
    expect(await screen.findByText("Neu erstellt: 2")).toBeInTheDocument();
  });
});
