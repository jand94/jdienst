import { getAccessToken } from "@/lib/auth/token-store";
import { env } from "@/lib/config/env";

type NotificationRealtimeEvent = {
  event: string;
  data: Record<string, unknown>;
};

function notificationWebSocketUrl(): string | null {
  const token = getAccessToken();
  if (!token) {
    return null;
  }
  const baseUrl = env.apiBaseUrl.replace(/^http/, "ws");
  return `${baseUrl}/ws/notifications/?token=${encodeURIComponent(token)}`;
}

export function connectNotificationRealtime(
  onEvent: (payload: NotificationRealtimeEvent) => void,
  onError?: (error: Event) => void,
): (() => void) | null {
  if (typeof window === "undefined") {
    return null;
  }
  const targetUrl = notificationWebSocketUrl();
  if (!targetUrl) {
    return null;
  }
  const socket = new WebSocket(targetUrl);
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
  return () => {
    socket.close();
  };
}
