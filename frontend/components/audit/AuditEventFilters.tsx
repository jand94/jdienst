"use client";

import { ChangeEvent } from "react";

import type { AuditEventQuery } from "@/lib/audit/audit-types";

type AuditEventFiltersProps = {
  value: AuditEventQuery;
  onChange: (next: AuditEventQuery) => void;
};

function handleFieldChange(
  value: AuditEventQuery,
  onChange: (next: AuditEventQuery) => void,
  field: keyof AuditEventQuery,
) {
  return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onChange({
      ...value,
      [field]: event.target.value || undefined,
      page: 1,
    });
  };
}

export default function AuditEventFilters({ value, onChange }: AuditEventFiltersProps) {
  return (
    <div className="grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-5">
      <label className="space-y-1 text-sm">
        <span className="font-medium">Action</span>
        <input
          value={value.action ?? ""}
          onChange={handleFieldChange(value, onChange, "action")}
          className="w-full rounded-md border px-2 py-1.5"
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium">Target Model</span>
        <input
          value={value.targetModel ?? ""}
          onChange={handleFieldChange(value, onChange, "targetModel")}
          className="w-full rounded-md border px-2 py-1.5"
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium">Target ID</span>
        <input
          value={value.targetId ?? ""}
          onChange={handleFieldChange(value, onChange, "targetId")}
          className="w-full rounded-md border px-2 py-1.5"
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium">Actor</span>
        <input
          value={value.actor ?? ""}
          onChange={handleFieldChange(value, onChange, "actor")}
          className="w-full rounded-md border px-2 py-1.5"
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium">Sortierung</span>
        <select
          value={value.ordering ?? "-created_at"}
          onChange={handleFieldChange(value, onChange, "ordering")}
          className="w-full rounded-md border px-2 py-1.5"
        >
          <option value="-created_at">Neueste zuerst</option>
          <option value="created_at">Aelteste zuerst</option>
          <option value="action">Action A-Z</option>
          <option value="-action">Action Z-A</option>
        </select>
      </label>
    </div>
  );
}
