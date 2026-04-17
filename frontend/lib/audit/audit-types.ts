export type AuditEvent = {
  id: string;
  actor: number | string | null;
  action: string;
  target_model: string;
  target_id: string;
  metadata: Record<string, unknown>;
  ip_address: string | null;
  user_agent: string;
  previous_hash: string;
  integrity_hash: string;
  archived_at: string | null;
  exported_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type AuditEventQuery = {
  page?: number;
  pageSize?: number;
  action?: string;
  targetModel?: string;
  targetId?: string;
  actor?: string;
  ordering?: "created_at" | "-created_at" | "action" | "-action";
};

export type AuditHealthSnapshotResponse = {
  window_hours: number;
  events_total: number;
  events_without_actor: number;
  events_not_exported: number;
  retention_class_counts: Record<string, number>;
  volume_by_action: Record<string, number>;
  integrity_verification: Record<string, unknown>;
  outbox: Record<string, unknown>;
};

export type AuditIntegrityVerifyResponse = {
  id: string;
  status: string;
  checked_events: number;
  last_event_hash: string;
  details: Record<string, unknown>;
  checkpoint_id: string | null;
};

export type AuditSiemExportPreviewResponse = {
  exportable_count: number;
  failure_count: number;
  event_ids: string[];
  preview: Record<string, unknown>[];
  failures: Record<string, unknown>[];
};

export type AuditArchiveResponse = {
  archived_events: number;
  mode: "before_days" | "retention_policy";
};

export type AuditSetupRolesResponse = {
  roles: string[];
  created_roles: number;
};
