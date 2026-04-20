import { describe, expect, it } from "vitest";

import { getVisibleNavigationItems } from "@/lib/navigation/navigation-policy";

describe("navigation-policy", () => {
  it("hides protected routes when user is unauthenticated", () => {
    const visibleItems = getVisibleNavigationItems({
      status: "unauthenticated",
      canAny: () => false,
    });

    expect(visibleItems).toHaveLength(0);
  });

  it("returns permission-based navigation for authenticated users", () => {
    const visibleItems = getVisibleNavigationItems({
      status: "authenticated",
      canAny: (...permissions) =>
        permissions.includes("dashboard.view") || permissions.includes("audit.events.read"),
    });

    expect(visibleItems.map((item) => item.href)).toEqual(["/", "/notifications", "/audit"]);
  });

  it("includes visible child routes for settings dropdown", () => {
    const visibleItems = getVisibleNavigationItems({
      status: "authenticated",
      canAny: (...permissions) => permissions.includes("settings.view"),
    });

    const settings = visibleItems.find((item) => item.href === "/settings");
    expect(settings).toBeDefined();
    expect(settings?.children?.map((child) => child.href)).toEqual(["/settings/users", "/settings/crm"]);
  });
});
