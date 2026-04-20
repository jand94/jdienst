"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { getNotificationOpsHealthSnapshot } from "@/lib/notifications/notification-ops-api";
import type { NotificationOpsHealthSnapshot } from "@/lib/notifications/notification-ops-types";

type NotificationHealthSnapshotCardProps = {
  tenantSlug: string;
};

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function NotificationHealthSnapshotCard({ tenantSlug }: NotificationHealthSnapshotCardProps) {
  const [data, setData] = useState<NotificationOpsHealthSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSnapshot = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getNotificationOpsHealthSnapshot(tenantSlug, 24);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification Snapshot konnte nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Notification Health</h2>
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
            <dt className="font-medium">Status</dt>
            <dd>{data.passed ? "OK" : "Warnung"}</dd>
          </div>
          <div>
            <dt className="font-medium">Pending Deliveries</dt>
            <dd>{data.delivery.pending_total}</dd>
          </div>
          <div>
            <dt className="font-medium">Terminal Failures</dt>
            <dd>{data.delivery.terminal_failed_total}</dd>
          </div>
          <div>
            <dt className="font-medium">Oldest Pending</dt>
            <dd>{data.delivery.oldest_pending_age_seconds}s</dd>
          </div>
          <div>
            <dt className="font-medium">Success Rate</dt>
            <dd>{formatPercent(data.delivery.recent_success_rate)}</dd>
          </div>
          <div>
            <dt className="font-medium">Digest Pending</dt>
            <dd>{data.digest.pending_total}</dd>
          </div>
        </dl>
      )}
    </article>
  );
}
