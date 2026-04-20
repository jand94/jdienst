import { httpClient } from "@/lib/api/http-client";
import type {
  NotificationItem,
  NotificationPage,
  NotificationPreference,
  NotificationPreferencePage,
} from "@/lib/notifications/notification-types";

export async function listNotifications(
  tenantSlug: string,
  includeArchived = false,
  page = 1,
  pageSize = 20,
): Promise<NotificationPage> {
  const query = new URLSearchParams({
    include_archived: includeArchived ? "true" : "false",
    page: String(page),
    page_size: String(pageSize),
  }).toString();
  return httpClient.get<NotificationPage>(`/api/notification/v1/notifications/?${query}`, {
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

export async function bulkArchiveNotifications(
  tenantSlug: string,
  notificationIds: string[],
): Promise<{ updated: number }> {
  return httpClient.post<{ updated: number }>(
    "/api/notification/v1/notifications/bulk-archive/",
    { notification_ids: notificationIds },
    {
      auth: true,
      tenantSlug,
    },
  );
}

export async function archiveNotification(tenantSlug: string, notificationId: string): Promise<NotificationItem> {
  return httpClient.post<NotificationItem>(`/api/notification/v1/notifications/${notificationId}/archive/`, undefined, {
    auth: true,
    tenantSlug,
  });
}

export async function getUnreadNotificationCount(tenantSlug: string): Promise<{ unread_count: number }> {
  return httpClient.get<{ unread_count: number }>("/api/notification/v1/notifications/unread-count/", {
    auth: true,
    tenantSlug,
  });
}

export async function listNotificationPreferences(
  tenantSlug: string,
  page = 1,
  pageSize = 50,
): Promise<NotificationPreferencePage> {
  const query = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  }).toString();
  return httpClient.get<NotificationPreferencePage>(`/api/notification/v1/preferences/?${query}`, {
    auth: true,
    tenantSlug,
  });
}

export async function updateNotificationPreference(
  tenantSlug: string,
  payload: {
    notification_type_key: string;
    channel: "in_app" | "email" | "realtime" | "digest";
    is_subscribed: boolean;
  },
): Promise<NotificationPreference> {
  return httpClient.post<NotificationPreference>("/api/notification/v1/preferences/", payload, {
    auth: true,
    tenantSlug,
  });
}
