"use client";

import type { AuditEvent } from "@/lib/audit/audit-types";

type AuditEventDetailProps = {
  event: AuditEvent | null;
};

export default function AuditEventDetail({ event }: AuditEventDetailProps) {
  if (!event) {
    return (
      <aside className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
        Waehle ein Event aus, um Details zu sehen.
      </aside>
    );
  }

  return (
    <aside className="space-y-3 rounded-md border bg-card p-4">
      <h2 className="text-base font-semibold">Event Detail</h2>
      <dl className="space-y-1 text-sm">
        <div>
          <dt className="font-medium">ID</dt>
          <dd className="text-muted-foreground">{event.id}</dd>
        </div>
        <div>
          <dt className="font-medium">Action</dt>
          <dd className="text-muted-foreground">{event.action}</dd>
        </div>
        <div>
          <dt className="font-medium">Target</dt>
          <dd className="text-muted-foreground">
            {event.target_model} / {event.target_id}
          </dd>
        </div>
      </dl>
      <div>
        <p className="mb-1 text-sm font-medium">Metadata</p>
        <pre className="max-h-80 overflow-auto rounded-md bg-muted p-3 text-xs">
          {JSON.stringify(event.metadata, null, 2)}
        </pre>
      </div>
    </aside>
  );
}
