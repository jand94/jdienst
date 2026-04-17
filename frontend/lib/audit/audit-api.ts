import { httpClient } from "@/lib/api/http-client";
import type { AuditEvent, AuditEventQuery, PaginatedResponse } from "@/lib/audit/audit-types";

function buildQuery(params: AuditEventQuery): string {
  const query = new URLSearchParams();
  if (params.page) {
    query.set("page", String(params.page));
  }
  if (params.pageSize) {
    query.set("page_size", String(params.pageSize));
  }
  if (params.action) {
    query.set("action", params.action);
  }
  if (params.targetModel) {
    query.set("target_model", params.targetModel);
  }
  if (params.targetId) {
    query.set("target_id", params.targetId);
  }
  if (params.actor) {
    query.set("actor", params.actor);
  }
  if (params.ordering) {
    query.set("ordering", params.ordering);
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function listAuditEvents(
  tenantSlug: string,
  params: AuditEventQuery,
): Promise<PaginatedResponse<AuditEvent>> {
  return httpClient.get<PaginatedResponse<AuditEvent>>(`/api/common/v1/audit-events/${buildQuery(params)}`, {
    auth: true,
    tenantSlug,
  });
}

export async function getAuditEvent(tenantSlug: string, id: string): Promise<AuditEvent> {
  return httpClient.get<AuditEvent>(`/api/common/v1/audit-events/${id}/`, {
    auth: true,
    tenantSlug,
  });
}
