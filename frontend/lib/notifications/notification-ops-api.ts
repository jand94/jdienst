import { httpClient } from "@/lib/api/http-client";
import type { NotificationOpsHealthSnapshot } from "@/lib/notifications/notification-ops-types";

export function getNotificationOpsHealthSnapshot(
  tenantSlug: string,
  windowHours = 24,
): Promise<NotificationOpsHealthSnapshot> {
  const query = new URLSearchParams({ window_hours: String(windowHours) }).toString();
  return httpClient.get<NotificationOpsHealthSnapshot>(`/api/notification/v1/ops/health-snapshot/?${query}`, {
    auth: true,
    tenantSlug,
  });
}
