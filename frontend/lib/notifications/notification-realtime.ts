import { getAccessToken } from "@/lib/auth/token-store";
import { env } from "@/lib/config/env";

type NotificationRealtimeEvent = {
  event: string;
  data: Record<string, unknown>;
};

type RealtimeConnectionOptions = {
  onOpen?: () => void;
  onClose?: () => void;
};

function notificationWebSocketUrl(): string | null {
  const token = getAccessToken();
  if (!token) {
    return null;
  }
  const baseUrl = (env.notificationWsBaseUrl || env.apiBaseUrl).replace(/^http/, "ws");
  const normalizedPath = env.notificationWsPath.startsWith("/") ? env.notificationWsPath : `/${env.notificationWsPath}`;
  const pathWithSlash = normalizedPath.endsWith("/") ? normalizedPath : `${normalizedPath}/`;
  return `${baseUrl}${pathWithSlash}?token=${encodeURIComponent(token)}`;
}

export function connectNotificationRealtime(
  onEvent: (payload: NotificationRealtimeEvent) => void,
  onError?: (error: Event) => void,
  options?: RealtimeConnectionOptions,
): (() => void) | null {
  if (typeof window === "undefined") {
    return null;
  }
  const targetUrl = notificationWebSocketUrl();
  if (!targetUrl) {
    return null;
  }
  const socket = new WebSocket(targetUrl);
  socket.onopen = () => {
    options?.onOpen?.();
  };
  socket.onmessage = (messageEvent) => {
    try {
      const payload = JSON.parse(messageEvent.data) as NotificationRealtimeEvent;
      onEvent(payload);
    } catch {
      // Ignore malformed websocket payloads.
    }
  };
  if (onError) {
    socket.onerror = onError;
  }
  socket.onclose = () => {
    options?.onClose?.();
  };
  return () => {
    socket.close();
  };
}
