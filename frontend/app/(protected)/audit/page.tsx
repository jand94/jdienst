"use client";

import { useEffect, useMemo, useState } from "react";

import AuditEventDetail from "@/components/audit/AuditEventDetail";
import AuditEventFilters from "@/components/audit/AuditEventFilters";
import AuditEventTable from "@/components/audit/AuditEventTable";
import RequireRole from "@/components/auth/RequireRole";
import { getAuditEvent, listAuditEvents } from "@/lib/audit/audit-api";
import type { AuditEvent, AuditEventQuery } from "@/lib/audit/audit-types";
import { useAuth } from "@/hooks/use-auth";

const defaultQuery: AuditEventQuery = {
  page: 1,
  pageSize: 50,
  ordering: "-created_at",
};

export default function AuditPage() {
  const auth = useAuth();
  const [query, setQuery] = useState<AuditEventQuery>(defaultQuery);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const page = query.page ?? 1;
  const pageSize = query.pageSize ?? 50;

  const canLoad = useMemo(
    () => auth.status === "authenticated" && auth.hasRole("audit_reader", "audit_operator"),
    [auth],
  );

  useEffect(() => {
    if (!canLoad) {
      return;
    }
    let active = true;
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await listAuditEvents(auth.tenantSlug, query);
        if (!active) {
          return;
        }
        setEvents(response.results);
        setTotal(response.count);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Audit-Events konnten nicht geladen werden.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    void run();
    return () => {
      active = false;
    };
  }, [auth.tenantSlug, canLoad, query]);

  const selectEvent = async (eventId: string) => {
    try {
      const detail = await getAuditEvent(auth.tenantSlug, eventId);
      setSelectedEvent(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Event-Details konnten nicht geladen werden.");
    }
  };

  return (
    <RequireRole roles={["audit_reader", "audit_operator"]}>
      <section className="space-y-5">
        <header className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Audit Events</h1>
          <p className="text-sm text-muted-foreground">Filtere, sortiere und pruefe sicherheitsrelevante Ereignisse.</p>
        </header>

        <AuditEventFilters value={query} onChange={setQuery} />

        <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
          <AuditEventTable
            events={events}
            loading={loading}
            error={error}
            page={page}
            total={total}
            pageSize={pageSize}
            onPageChange={(nextPage) => setQuery((prev) => ({ ...prev, page: nextPage }))}
            onSelectEvent={selectEvent}
          />
          <AuditEventDetail event={selectedEvent} />
        </div>
      </section>
    </RequireRole>
  );
}
