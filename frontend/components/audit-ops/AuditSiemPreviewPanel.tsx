"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { getSiemExportPreview } from "@/lib/audit/audit-ops-api";
import type { AuditSiemExportPreviewResponse } from "@/lib/audit/audit-types";

type AuditSiemPreviewPanelProps = {
  tenantSlug: string;
};

export default function AuditSiemPreviewPanel({ tenantSlug }: AuditSiemPreviewPanelProps) {
  const [limit, setLimit] = useState(100);
  const [result, setResult] = useState<AuditSiemExportPreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadPreview = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getSiemExportPreview(tenantSlug, limit);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "SIEM Preview konnte nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="space-y-3 rounded-md border bg-card p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-base font-semibold">SIEM Export Preview</h2>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min={1}
            max={500}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
            className="w-20 rounded-md border px-2 py-1.5 text-sm"
          />
          <Button size="sm" variant="outline" onClick={() => void loadPreview()} disabled={loading}>
            {loading ? "Lade..." : "Preview"}
          </Button>
        </div>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!result ? (
        <p className="text-sm text-muted-foreground">Noch keine SIEM-Vorschau geladen.</p>
      ) : (
        <div className="space-y-2 text-sm">
          <p>Exportierbar: {result.exportable_count}</p>
          <p>Fehler: {result.failure_count}</p>
          <pre className="max-h-52 overflow-auto rounded-md bg-muted p-2 text-xs">
            {JSON.stringify(result.preview.slice(0, 3), null, 2)}
          </pre>
        </div>
      )}
    </article>
  );
}
