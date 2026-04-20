export type NotificationTypeSummary = {
  id: string;
  key: string;
  title: string;
  description: string;
  default_channels: string[];
  allow_user_opt_out: boolean;
  is_active: boolean;
};

export type NotificationItem = {
  id: string;
  notification_type: NotificationTypeSummary;
  title: string;
  body: string;
  metadata: Record<string, unknown>;
  status: "unread" | "read" | "archived";
  published_at: string;
  read_at: string | null;
};

export type NotificationPreference = {
  id: string;
  notification_type: NotificationTypeSummary;
  channel: "in_app" | "email" | "realtime" | "digest";
  is_subscribed: boolean;
  updated_at: string;
};
