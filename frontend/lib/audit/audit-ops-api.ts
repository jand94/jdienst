import { httpClient } from "@/lib/api/http-client";
import type {
  AuditArchiveResponse,
  AuditHealthSnapshotResponse,
  AuditIntegrityVerifyResponse,
  AuditSetupRolesResponse,
  AuditSiemExportPreviewResponse,
} from "@/lib/audit/audit-types";

export function getAuditHealthSnapshot(tenantSlug: string, windowHours = 24): Promise<AuditHealthSnapshotResponse> {
  const query = new URLSearchParams({ window_hours: String(windowHours) }).toString();
  return httpClient.get<AuditHealthSnapshotResponse>(`/api/common/v1/audit-ops/health-snapshot/?${query}`, {
    auth: true,
    tenantSlug,
  });
}

export function verifyAuditIntegrity(
  tenantSlug: string,
  payload: { limit?: number; create_checkpoint?: boolean },
): Promise<AuditIntegrityVerifyResponse> {
  return httpClient.post<AuditIntegrityVerifyResponse>("/api/common/v1/audit-ops/verify-integrity/", payload, {
    auth: true,
    tenantSlug,
  });
}

export function getSiemExportPreview(tenantSlug: string, limit = 100): Promise<AuditSiemExportPreviewResponse> {
  const query = new URLSearchParams({ limit: String(limit) }).toString();
  return httpClient.get<AuditSiemExportPreviewResponse>(`/api/common/v1/audit-ops/siem-export-preview/?${query}`, {
    auth: true,
    tenantSlug,
  });
}

export function archiveAuditEvents(
  tenantSlug: string,
  payload: { before_days?: number; use_retention_policy?: boolean },
): Promise<AuditArchiveResponse> {
  return httpClient.post<AuditArchiveResponse>("/api/common/v1/audit-ops/archive-events/", payload, {
    auth: true,
    tenantSlug,
  });
}

export function setupAuditRoles(tenantSlug: string): Promise<AuditSetupRolesResponse> {
  return httpClient.post<AuditSetupRolesResponse>("/api/common/v1/audit-ops/setup-roles/", undefined, {
    auth: true,
    tenantSlug,
  });
}
