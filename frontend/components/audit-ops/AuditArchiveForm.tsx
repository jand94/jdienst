"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { archiveAuditEvents } from "@/lib/audit/audit-ops-api";
import type { AuditArchiveResponse } from "@/lib/audit/audit-types";

type AuditArchiveFormProps = {
  tenantSlug: string;
};

export default function AuditArchiveForm({ tenantSlug }: AuditArchiveFormProps) {
  const [beforeDays, setBeforeDays] = useState(90);
  const [useRetentionPolicy, setUseRetentionPolicy] = useState(false);
  const [result, setResult] = useState<AuditArchiveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const confirmed = window.confirm(
      "Diese Aktion kann viele Events archivieren. Soll die Archivierung wirklich gestartet werden?",
    );
    if (!confirmed) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await archiveAuditEvents(tenantSlug, {
        before_days: beforeDays,
        use_retention_policy: useRetentionPolicy,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Archivierung fehlgeschlagen.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <h2 className="text-base font-semibold">Archive Events</h2>
      <form className="space-y-3" onSubmit={onSubmit}>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Before days</span>
          <input
            type="number"
            min={1}
            max={36500}
            value={beforeDays}
            onChange={(event) => setBeforeDays(Number(event.target.value))}
            className="w-full rounded-md border px-2 py-1.5"
            disabled={useRetentionPolicy}
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={useRetentionPolicy}
            onChange={(event) => setUseRetentionPolicy(event.target.checked)}
          />
          Retention Policy statt before days nutzen
        </label>
        <Button type="submit" variant="destructive" disabled={loading}>
          {loading ? "Archiviere..." : "Archivierung starten"}
        </Button>
      </form>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {result && (
        <p className="rounded-md bg-muted p-3 text-sm">
          Archiviert: {result.archived_events} (Modus: {result.mode})
        </p>
      )}
    </article>
  );
}
