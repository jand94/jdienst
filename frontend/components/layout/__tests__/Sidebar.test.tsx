import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { listNotificationsMock } = vi.hoisted(() => ({
  listNotificationsMock: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    status: "authenticated",
    tenantSlug: "tenant-a",
    navigationFavorites: [],
    canAny: () => true,
    toggleNavigationFavorite: vi.fn(),
    reorderNavigationFavorites: vi.fn(),
  }),
}));

vi.mock("@/lib/notifications/notification-api", () => ({
  listNotifications: listNotificationsMock,
}));

import Sidebar from "@/components/layout/Sidebar";

describe("Sidebar notification badge", () => {
  it("shows unread badge when unread notifications exist", async () => {
    listNotificationsMock.mockResolvedValue([
      {
        id: "n-1",
        status: "unread",
      },
      {
        id: "n-2",
        status: "read",
      },
    ]);

    render(<Sidebar />);

    await waitFor(() => {
      expect(screen.getByLabelText("1 ungelesene Notifications")).toBeInTheDocument();
    });
  });
});
