"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { getAuditHealthSnapshot } from "@/lib/audit/audit-ops-api";
import type { AuditHealthSnapshotResponse } from "@/lib/audit/audit-types";

type AuditHealthSnapshotCardProps = {
  tenantSlug: string;
};

export default function AuditHealthSnapshotCard({ tenantSlug }: AuditHealthSnapshotCardProps) {
  const [data, setData] = useState<AuditHealthSnapshotResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSnapshot = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAuditHealthSnapshot(tenantSlug, 24);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Snapshot konnte nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Health Snapshot</h2>
        <Button size="sm" variant="outline" onClick={() => void loadSnapshot()} disabled={loading}>
          {loading ? "Lade..." : "Aktualisieren"}
        </Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!data ? (
        <p className="text-sm text-muted-foreground">Noch kein Snapshot geladen.</p>
      ) : (
        <dl className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <dt className="font-medium">Events total</dt>
            <dd>{data.events_total}</dd>
          </div>
          <div>
            <dt className="font-medium">Nicht exportiert</dt>
            <dd>{data.events_not_exported}</dd>
          </div>
          <div>
            <dt className="font-medium">Ohne Actor</dt>
            <dd>{data.events_without_actor}</dd>
          </div>
          <div>
            <dt className="font-medium">Window</dt>
            <dd>{data.window_hours}h</dd>
          </div>
        </dl>
      )}
    </article>
  );
}
