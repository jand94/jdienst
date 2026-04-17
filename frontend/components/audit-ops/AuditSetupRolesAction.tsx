"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { setupAuditRoles } from "@/lib/audit/audit-ops-api";
import type { AuditSetupRolesResponse } from "@/lib/audit/audit-types";

type AuditSetupRolesActionProps = {
  tenantSlug: string;
};

export default function AuditSetupRolesAction({ tenantSlug }: AuditSetupRolesActionProps) {
  const [result, setResult] = useState<AuditSetupRolesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const execute = async () => {
    const confirmed = window.confirm("Sollen Audit-Rollen jetzt synchronisiert werden?");
    if (!confirmed) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await setupAuditRoles(tenantSlug);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rollen konnten nicht synchronisiert werden.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <h2 className="text-base font-semibold">Setup Roles</h2>
      <Button variant="outline" onClick={() => void execute()} disabled={loading}>
        {loading ? "Synchronisiere..." : "Rollen synchronisieren"}
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {result && (
        <div className="rounded-md bg-muted p-3 text-sm">
          <p>Neu erstellt: {result.created_roles}</p>
          <p>Rollen: {result.roles.join(", ") || "-"}</p>
        </div>
      )}
    </article>
  );
}
