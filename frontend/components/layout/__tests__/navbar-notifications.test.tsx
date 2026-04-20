import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { NotificationItem } from "@/lib/notifications/notification-types";

const {
  listNotificationsMock,
  getUnreadNotificationCountMock,
  markNotificationAsReadMock,
  connectNotificationRealtimeMock,
  toastSuccessMock,
} = vi.hoisted(() => ({
  listNotificationsMock: vi.fn(),
  getUnreadNotificationCountMock: vi.fn(),
  markNotificationAsReadMock: vi.fn(),
  connectNotificationRealtimeMock: vi.fn(),
  toastSuccessMock: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/notifications",
  useRouter: () => ({
    replace: vi.fn(),
  }),
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: ReactNode }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("sonner", () => ({
  toast: {
    success: toastSuccessMock,
  },
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    status: "authenticated",
    tenantSlug: "tenant-a",
    user: { username: "tester" },
    navigationFavorites: [],
    signOut: vi.fn().mockResolvedValue(undefined),
    toggleNavigationFavorite: vi.fn().mockResolvedValue(undefined),
  }),
}));

vi.mock("@/lib/navigation/navigation-policy", () => ({
  getVisibleNavigationItems: () => [
    {
      href: "/notifications",
      label: "Notifications",
      description: "Inbox",
      icon: "bell",
      group: "core",
      children: [],
    },
  ],
}));

vi.mock("@/lib/navigation/icons", () => ({
  getNavigationIcon: () => () => <span data-testid="nav-icon" />,
}));

vi.mock("@/lib/navigation/group-colors", () => ({
  getNavigationGroupColors: () => ({
    activeText: "",
    icon: "",
    activeBorder: "",
  }),
}));

vi.mock("@/hooks/use-breakpoint", () => ({
  useCurrentBreakpoint: () => "lg",
  useResponsiveValue: () => "w-80",
}));

vi.mock("@/lib/notifications/notification-api", () => ({
  listNotifications: listNotificationsMock,
  getUnreadNotificationCount: getUnreadNotificationCountMock,
  markNotificationAsRead: markNotificationAsReadMock,
}));

vi.mock("@/lib/notifications/notification-realtime", () => ({
  connectNotificationRealtime: connectNotificationRealtimeMock,
}));

import Navbar from "@/components/layout/Navbar";

function buildNotification(overrides?: Partial<NotificationItem>): NotificationItem {
  return {
    id: "notif-1",
    title: "Task zugewiesen",
    body: "Dir wurde eine Task zugewiesen.",
    status: "unread",
    metadata: {},
    read_at: null,
    published_at: new Date().toISOString(),
    notification_type: {
      id: "type-1",
      key: "task.assigned",
      title: "Task",
      description: "",
      default_channels: ["in_app"],
      allow_user_opt_out: true,
      is_active: true,
    },
    ...overrides,
  };
}

describe("Navbar notifications", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listNotificationsMock.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [buildNotification()],
    });
    getUnreadNotificationCountMock.mockResolvedValue({ unread_count: 1 });
    markNotificationAsReadMock.mockResolvedValue(buildNotification({ status: "read", read_at: new Date().toISOString() }));
    connectNotificationRealtimeMock.mockImplementation(() => () => undefined);
  });

  it("shows unread badge and renders unread notifications in sheet", async () => {
    render(<Navbar />);

    await waitFor(() => {
      expect(getUnreadNotificationCountMock).toHaveBeenCalledWith("tenant-a");
    });

    expect(screen.getByText("1")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Ungelesene Notifications anzeigen" }));
    expect(await screen.findByText("Task zugewiesen")).toBeInTheDocument();
    expect(screen.getByText("Dir wurde eine Task zugewiesen.")).toBeInTheDocument();
  });

  it("marks unread notification as read from sheet", async () => {
    render(<Navbar />);
    await waitFor(() => {
      expect(getUnreadNotificationCountMock).toHaveBeenCalled();
    });

    await userEvent.click(screen.getByRole("button", { name: "Ungelesene Notifications anzeigen" }));
    await screen.findByText("Task zugewiesen");

    await userEvent.click(screen.getByRole("button", { name: "Als gelesen markieren" }));

    await waitFor(() => {
      expect(markNotificationAsReadMock).toHaveBeenCalledWith("tenant-a", "notif-1");
    });
    expect(toastSuccessMock).toHaveBeenCalledWith("Notification als gelesen markiert.");
  });
});
