"use client";

import RequireAccess from "@/components/auth/RequireAccess";
import AuditArchiveForm from "@/components/audit-ops/AuditArchiveForm";
import AuditHealthSnapshotCard from "@/components/audit-ops/AuditHealthSnapshotCard";
import AuditIntegrityForm from "@/components/audit-ops/AuditIntegrityForm";
import AuditSetupRolesAction from "@/components/audit-ops/AuditSetupRolesAction";
import AuditSiemPreviewPanel from "@/components/audit-ops/AuditSiemPreviewPanel";
import { useAuth } from "@/hooks/use-auth";

export default function AuditOpsPage() {
  const auth = useAuth();

  return (
    <RequireAccess permissions={["audit.ops.manage"]}>
      <section className="space-y-5">
        <header className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Audit Operator</h1>
          <p className="text-sm text-muted-foreground">
            Administrative Aktionen fuer Integritaet, SIEM-Vorschau und Archivierung.
          </p>
        </header>
        <div className="grid gap-4 xl:grid-cols-2">
          <AuditHealthSnapshotCard tenantSlug={auth.tenantSlug} />
          <AuditIntegrityForm tenantSlug={auth.tenantSlug} />
          <AuditSiemPreviewPanel tenantSlug={auth.tenantSlug} />
          <AuditArchiveForm tenantSlug={auth.tenantSlug} />
          <AuditSetupRolesAction tenantSlug={auth.tenantSlug} />
        </div>
      </section>
    </RequireAccess>
  );
}
