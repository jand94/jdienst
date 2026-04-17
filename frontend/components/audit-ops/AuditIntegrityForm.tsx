"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { verifyAuditIntegrity } from "@/lib/audit/audit-ops-api";
import type { AuditIntegrityVerifyResponse } from "@/lib/audit/audit-types";

type AuditIntegrityFormProps = {
  tenantSlug: string;
};

export default function AuditIntegrityForm({ tenantSlug }: AuditIntegrityFormProps) {
  const [limit, setLimit] = useState(100);
  const [createCheckpoint, setCreateCheckpoint] = useState(false);
  const [result, setResult] = useState<AuditIntegrityVerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await verifyAuditIntegrity(tenantSlug, {
        limit,
        create_checkpoint: createCheckpoint,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Integritaet konnte nicht geprueft werden.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <h2 className="text-base font-semibold">Integrity Verify</h2>
      <form className="space-y-3" onSubmit={onSubmit}>
        <label className="block text-sm">
          <span className="mb-1 block font-medium">Limit</span>
          <input
            type="number"
            min={1}
            max={10000}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
            className="w-full rounded-md border px-2 py-1.5"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={createCheckpoint}
            onChange={(event) => setCreateCheckpoint(event.target.checked)}
          />
          Checkpoint erstellen
        </label>
        <Button type="submit" disabled={loading}>
          {loading ? "Pruefe..." : "Integritaet pruefen"}
        </Button>
      </form>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {result && (
        <div className="rounded-md bg-muted p-3 text-sm">
          <p>Status: {result.status}</p>
          <p>Checked events: {result.checked_events}</p>
          <p>Checkpoint: {result.checkpoint_id ?? "-"}</p>
        </div>
      )}
    </article>
  );
}
