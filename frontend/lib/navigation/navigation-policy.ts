import type { AppPermission } from "@/lib/auth/session-types";
import { navigationItems } from "@/lib/navigation/navigation.config";
import type { NavigationIconKey, NavigationItem, NavigationGroupKey } from "@/lib/navigation/navigation.config";

export type NavigationAuthState = {
  status: "loading" | "authenticated" | "unauthenticated" | "error";
  canAny: (...permissions: string[]) => boolean;
};

function isVisible(requiredPermissions: AppPermission[] | undefined, canAny: (...permissions: string[]) => boolean): boolean {
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true;
  }
  return canAny(...requiredPermissions);
}

export function getVisibleNavigationItems(auth: NavigationAuthState): NavigationItem[] {
  return navigationItems.reduce<NavigationItem[]>((accumulator, item) => {
    if (item.requiresAuth && auth.status !== "authenticated") {
      return accumulator;
    }
    const visibleChildren = (item.children ?? []).filter((child) => isVisible(child.requiredPermissions, auth.canAny));
    const parentVisible = isVisible(item.requiredPermissions, auth.canAny);
    if (!parentVisible && visibleChildren.length === 0) {
      return accumulator;
    }
    accumulator.push({
      ...item,
      children: visibleChildren,
    });
    return accumulator;
  }, []);
}

export type FlatNavigationItem = {
  href: string;
  label: string;
  description: string;
  icon: NavigationIconKey;
  group: NavigationGroupKey;
  parentHref: string | null;
};

export function flattenVisibleNavigationItems(items: NavigationItem[]): FlatNavigationItem[] {
  return items.flatMap((item) => [
    {
      href: item.href,
      label: item.label,
      description: item.description,
      icon: item.icon,
      group: item.group,
      parentHref: null,
    },
    ...(item.children ?? []).map((child) => ({
      href: child.href,
      label: child.label,
      description: child.description,
      icon: child.icon,
      group: child.group,
      parentHref: item.href,
    })),
  ]);
}
