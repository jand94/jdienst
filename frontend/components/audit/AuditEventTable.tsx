"use client";

import type { AuditEvent } from "@/lib/audit/audit-types";
import { Button } from "@/components/ui/button";

type AuditEventTableProps = {
  events: AuditEvent[];
  loading: boolean;
  error: string | null;
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onSelectEvent: (eventId: string) => void;
};

export default function AuditEventTable({
  events,
  loading,
  error,
  page,
  total,
  pageSize,
  onPageChange,
  onSelectEvent,
}: AuditEventTableProps) {
  const maxPage = Math.max(1, Math.ceil(total / pageSize));

  if (loading) {
    return <p className="rounded-md border p-4 text-sm text-muted-foreground">Lade Audit-Events...</p>;
  }

  if (error) {
    return <p className="rounded-md border border-destructive/50 p-4 text-sm text-destructive">{error}</p>;
  }

  if (events.length === 0) {
    return <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">Keine Audit-Events gefunden.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-3 py-2">Zeit</th>
              <th className="px-3 py-2">Action</th>
              <th className="px-3 py-2">Model</th>
              <th className="px-3 py-2">Target</th>
              <th className="px-3 py-2">Actor</th>
              <th className="px-3 py-2">Details</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id} className="border-t">
                <td className="px-3 py-2">{new Date(event.created_at).toLocaleString("de-DE")}</td>
                <td className="px-3 py-2">{event.action}</td>
                <td className="px-3 py-2">{event.target_model}</td>
                <td className="px-3 py-2">{event.target_id}</td>
                <td className="px-3 py-2">{event.actor ?? "-"}</td>
                <td className="px-3 py-2">
                  <Button variant="outline" size="sm" onClick={() => onSelectEvent(event.id)}>
                    Anzeigen
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Seite {page} von {maxPage} ({total} Eintraege)
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
            Zurueck
          </Button>
          <Button variant="outline" size="sm" onClick={() => onPageChange(page + 1)} disabled={page >= maxPage}>
            Weiter
          </Button>
        </div>
      </div>
    </div>
  );
}
