import { httpClient } from "@/lib/api/http-client";
import type { NotificationItem, NotificationPreference } from "@/lib/notifications/notification-types";

export async function listNotifications(tenantSlug: string, includeArchived = false): Promise<NotificationItem[]> {
  const query = includeArchived ? "?include_archived=true" : "";
  return httpClient.get<NotificationItem[]>(`/api/notification/v1/notifications/${query}`, {
    auth: true,
    tenantSlug,
  });
}

export async function markNotificationAsRead(tenantSlug: string, notificationId: string): Promise<NotificationItem> {
  return httpClient.post<NotificationItem>(`/api/notification/v1/notifications/${notificationId}/mark-read/`, undefined, {
    auth: true,
    tenantSlug,
  });
}

export async function bulkMarkNotificationsAsRead(
  tenantSlug: string,
  notificationIds: string[],
): Promise<{ updated: number }> {
  return httpClient.post<{ updated: number }>(
    "/api/notification/v1/notifications/bulk-mark-read/",
    { notification_ids: notificationIds },
    {
      auth: true,
      tenantSlug,
    },
  );
}

export async function listNotificationPreferences(tenantSlug: string): Promise<NotificationPreference[]> {
  return httpClient.get<NotificationPreference[]>("/api/notification/v1/preferences/", {
    auth: true,
    tenantSlug,
  });
}

export async function updateNotificationPreference(
  tenantSlug: string,
  payload: {
    notification_type_key: string;
    channel: "in_app" | "email";
    is_subscribed: boolean;
  },
): Promise<NotificationPreference> {
  return httpClient.post<NotificationPreference>("/api/notification/v1/preferences/", payload, {
    auth: true,
    tenantSlug,
  });
}
