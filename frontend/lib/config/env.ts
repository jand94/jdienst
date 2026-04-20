const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const defaultTenantSlug = process.env.NEXT_PUBLIC_DEFAULT_TENANT_SLUG;
const notificationWsBaseUrl = process.env.NEXT_PUBLIC_NOTIFICATION_WS_BASE_URL;
const notificationWsPath = process.env.NEXT_PUBLIC_NOTIFICATION_WS_PATH;

export const env = {
  apiBaseUrl: (apiBaseUrl || "http://localhost:8000").replace(/\/+$/, ""),
  defaultTenantSlug: defaultTenantSlug?.trim() || "",
  notificationWsBaseUrl: notificationWsBaseUrl?.trim().replace(/\/+$/, "") || "",
  notificationWsPath: notificationWsPath?.trim() || "/ws/notifications/",
};
