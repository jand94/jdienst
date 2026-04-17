import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AuditEventTable from "@/components/audit/AuditEventTable";

describe("AuditEventTable", () => {
  it("shows loading state", () => {
    render(
      <AuditEventTable
        events={[]}
        loading
        error={null}
        page={1}
        total={0}
        pageSize={50}
        onPageChange={vi.fn()}
        onSelectEvent={vi.fn()}
      />,
    );
    expect(screen.getByText("Lade Audit-Events...")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    render(
      <AuditEventTable
        events={[]}
        loading={false}
        error={null}
        page={1}
        total={0}
        pageSize={50}
        onPageChange={vi.fn()}
        onSelectEvent={vi.fn()}
      />,
    );
    expect(screen.getByText("Keine Audit-Events gefunden.")).toBeInTheDocument();
  });

  it("renders success rows", () => {
    render(
      <AuditEventTable
        events={[
          {
            id: "1",
            actor: 10,
            action: "auth.login.succeeded",
            target_model: "user",
            target_id: "10",
            metadata: {},
            ip_address: null,
            user_agent: "ua",
            previous_hash: "a",
            integrity_hash: "b",
            archived_at: null,
            exported_at: null,
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ]}
        loading={false}
        error={null}
        page={1}
        total={1}
        pageSize={50}
        onPageChange={vi.fn()}
        onSelectEvent={vi.fn()}
      />,
    );
    expect(screen.getByText("auth.login.succeeded")).toBeInTheDocument();
    expect(screen.getByText("Anzeigen")).toBeInTheDocument();
  });
});
