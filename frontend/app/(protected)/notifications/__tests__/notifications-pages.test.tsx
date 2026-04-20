import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

const {
  listNotificationsMock,
  bulkMarkNotificationsAsReadMock,
  markNotificationAsReadMock,
  listNotificationPreferencesMock,
  updateNotificationPreferenceMock,
  getUnreadNotificationCountMock,
  archiveNotificationMock,
  bulkArchiveNotificationsMock,
} = vi.hoisted(() => ({
  listNotificationsMock: vi.fn(),
  bulkMarkNotificationsAsReadMock: vi.fn(),
  markNotificationAsReadMock: vi.fn(),
  listNotificationPreferencesMock: vi.fn(),
  updateNotificationPreferenceMock: vi.fn(),
  getUnreadNotificationCountMock: vi.fn(),
  archiveNotificationMock: vi.fn(),
  bulkArchiveNotificationsMock: vi.fn(),
}));

vi.mock("@/components/auth/RequireAuth", () => ({
  default: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    status: "authenticated",
    tenantSlug: "tenant-a",
    navigationFavorites: [],
    canAny: () => true,
  }),
}));

vi.mock("@/lib/notifications/notification-api", () => ({
  listNotifications: listNotificationsMock,
  bulkMarkNotificationsAsRead: bulkMarkNotificationsAsReadMock,
  markNotificationAsRead: markNotificationAsReadMock,
  listNotificationPreferences: listNotificationPreferencesMock,
  updateNotificationPreference: updateNotificationPreferenceMock,
  getUnreadNotificationCount: getUnreadNotificationCountMock,
  archiveNotification: archiveNotificationMock,
  bulkArchiveNotifications: bulkArchiveNotificationsMock,
}));

vi.mock("@/lib/notifications/notification-realtime", () => ({
  connectNotificationRealtime: () => () => undefined,
}));

import NotificationsPage from "@/app/(protected)/notifications/page";
import NotificationPreferencesPage from "@/app/(protected)/notifications/preferences/page";

describe("Notification pages", () => {
  it("shows empty and loading states for notifications inbox", async () => {
    listNotificationsMock.mockResolvedValueOnce({
      count: 0,
      next: null,
      previous: null,
      results: [],
    });

    render(<NotificationsPage />);

    expect(screen.getByText("Notifications werden geladen...")).toBeInTheDocument();
    expect(await screen.findByText("Keine Notifications vorhanden.")).toBeInTheDocument();
  });

  it("shows success info after bulk mark as read", async () => {
    listNotificationsMock.mockResolvedValueOnce({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: "1",
          title: "Titel",
          body: "Body",
          status: "unread",
          metadata: {},
          read_at: null,
          published_at: new Date().toISOString(),
          notification_type: {
            id: "nt-1",
            key: "build",
            title: "Build",
            description: "",
            default_channels: ["in_app"],
            allow_user_opt_out: true,
            is_active: true,
          },
        },
      ],
    });
    bulkMarkNotificationsAsReadMock.mockResolvedValue({ updated: 1 });

    render(<NotificationsPage />);

    await screen.findByText("Titel");
    await userEvent.click(screen.getByRole("button", { name: "Alle sichtbaren Ungelesenen als gelesen markieren" }));

    expect(await screen.findByText("1 Notifications wurden als gelesen markiert.")).toBeInTheDocument();
  });

  it("renders accessible preferences table and saves toggle", async () => {
    listNotificationPreferencesMock.mockResolvedValueOnce({
      count: 0,
      next: null,
      previous: null,
      results: [],
    });
    listNotificationsMock.mockResolvedValueOnce({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: "2",
          title: "Digest",
          body: "Body",
          status: "unread",
          metadata: {},
          read_at: null,
          published_at: new Date().toISOString(),
          notification_type: {
            id: "nt-2",
            key: "digest",
            title: "Digest Meldung",
            description: "Beschreibung",
            default_channels: ["in_app"],
            allow_user_opt_out: true,
            is_active: true,
          },
        },
      ],
    });
    updateNotificationPreferenceMock.mockResolvedValue({
      id: "pref-1",
      channel: "email",
      is_subscribed: true,
      updated_at: new Date().toISOString(),
      notification_type: {
        id: "nt-2",
        key: "digest",
        title: "Digest Meldung",
        description: "Beschreibung",
        default_channels: ["in_app"],
        allow_user_opt_out: true,
        is_active: true,
      },
    });

    render(<NotificationPreferencesPage />);

    await screen.findByText("Digest Meldung");
    const checkbox = screen.getByLabelText("Digest Meldung: Mail aktivieren");
    await userEvent.click(checkbox);

    await waitFor(() => {
      expect(updateNotificationPreferenceMock).toHaveBeenCalled();
    });
    expect(await screen.findByText(/Praeferenz gespeichert:/)).toBeInTheDocument();
  });
});
