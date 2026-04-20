"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, ChevronRight, PanelLeftClose, PanelLeftOpen, Star } from "lucide-react";
import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/use-auth";
import { listNotifications } from "@/lib/notifications/notification-api";
import { flattenVisibleNavigationItems, getVisibleNavigationItems } from "@/lib/navigation/navigation-policy";
import { getNavigationIcon } from "@/lib/navigation/icons";
import { getNavigationGroupColors } from "@/lib/navigation/group-colors";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

function NavigationList({ compact = false }: { compact?: boolean }) {
  const pathname = usePathname();
  const auth = useAuth();
  const isCollapsed = compact;
  const favoriteSet = new Set(auth.navigationFavorites);
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({
    "/settings": true,
  });
  const [notificationUnreadCount, setNotificationUnreadCount] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    if (auth.status !== "authenticated") {
      return () => {
        active = false;
      };
    }
    const loadUnreadCount = async () => {
      try {
        const notifications = await listNotifications(auth.tenantSlug);
        if (!active) {
          return;
        }
        const unread = notifications.filter((item) => item.status === "unread").length;
        setNotificationUnreadCount(unread);
      } catch {
        if (active) {
          setNotificationUnreadCount(null);
        }
      }
    };
    void loadUnreadCount();
    const interval = window.setInterval(() => {
      void loadUnreadCount();
    }, 60000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [auth.status, auth.tenantSlug, pathname]);

  const isActiveLink = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  const visibleItems = getVisibleNavigationItems(auth);
  const flatVisibleItems = flattenVisibleNavigationItems(visibleItems);
  const itemByHref = new Map(flatVisibleItems.map((item) => [item.href, item] as const));
  const favoriteItems = auth.navigationFavorites
    .map((href) => itemByHref.get(href))
    .filter((item): item is NonNullable<typeof item> => Boolean(item));
  const regularItems = visibleItems.filter((item) => !favoriteSet.has(item.href));
  const displayedItems = isCollapsed ? visibleItems : regularItems;

  const renderLinkBody = (
    href: string,
    label: string,
    description: string,
    iconKey: Parameters<typeof getNavigationIcon>[0],
    group: Parameters<typeof getNavigationGroupColors>[0],
    isChild = false,
  ) => {
    const isActive = isActiveLink(href);
    const isFavorite = favoriteSet.has(href);
    const NavIcon = getNavigationIcon(iconKey);
    const colorClasses = getNavigationGroupColors(group);
    const showNotificationBadge = href === "/notifications" && (notificationUnreadCount ?? 0) > 0 && !isCollapsed;

    return (
      <div
        className={cn(
          "flex items-start gap-1 rounded-md border border-transparent px-1 py-1",
          isFavorite && !isCollapsed && colorClasses.badgeBg,
        )}
      >
        <Link
          href={href}
          aria-current={isActive ? "page" : undefined}
          title={isCollapsed ? label : undefined}
          className={cn(
            "flex flex-1 items-center gap-2 border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
            isActive && cn("font-medium", colorClasses.activeBorder, colorClasses.activeText),
            compact ? "pl-2" : "",
            isChild && !isCollapsed && "pl-8",
            isCollapsed && "justify-center px-1",
          )}
        >
          <NavIcon className={cn("h-4 w-4 shrink-0", colorClasses.icon)} />
          {!isCollapsed && (
            <span>
              <span className="inline-flex items-center gap-2 font-medium">
                {label}
                {showNotificationBadge && (
                  <span
                    aria-label={`${notificationUnreadCount} ungelesene Notifications`}
                    className="inline-flex min-w-5 items-center justify-center rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-800"
                  >
                    {notificationUnreadCount}
                  </span>
                )}
              </span>
              <p className="text-xs text-muted-foreground">{description}</p>
            </span>
          )}
        </Link>
        {auth.status === "authenticated" && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className={cn("mt-1 h-8 w-8 shrink-0", isCollapsed && "hidden")}
            aria-label={isFavorite ? "Favorit entfernen" : "Als Favorit markieren"}
            onClick={() => {
              void auth.toggleNavigationFavorite(href);
            }}
          >
            <Star className={cn("h-4 w-4", isFavorite && "fill-current text-amber-500")} />
          </Button>
        )}
      </div>
    );
  };

  const renderFavoriteItem = (
    href: string,
    label: string,
    description: string,
    iconKey: Parameters<typeof getNavigationIcon>[0],
    group: Parameters<typeof getNavigationGroupColors>[0],
  ) => {
    return (
      <li
        key={href}
        draggable
        onDragStart={(event) => {
          event.dataTransfer.setData("text/favorite-href", href);
          event.dataTransfer.effectAllowed = "move";
        }}
        onDragOver={(event) => {
          event.preventDefault();
          event.dataTransfer.dropEffect = "move";
        }}
        onDrop={(event) => {
          event.preventDefault();
          const sourceHref = event.dataTransfer.getData("text/favorite-href");
          if (!sourceHref || sourceHref === href) {
            return;
          }
          void auth.reorderNavigationFavorites(sourceHref, href);
        }}
      >
        {renderLinkBody(href, label, description, iconKey, group)}
      </li>
    );
  };

  if (visibleItems.length === 0) {
    return <p className="px-3 py-2 text-sm text-muted-foreground">Melde dich an, um Navigationseintraege zu sehen.</p>;
  }

  return (
    <div className="space-y-4">
      {favoriteItems.length > 0 && !isCollapsed && (
        <section>
          <h3 className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Favoriten</h3>
          <ul className="space-y-1">
            {favoriteItems.map((item) => renderFavoriteItem(item.href, item.label, item.description, item.icon, item.group))}
          </ul>
        </section>
      )}
      <section>
        {!isCollapsed && (
          <h3 className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Alle Bereiche</h3>
        )}
        <ul className="space-y-1">
          {displayedItems.map((item) => {
            const hasChildren = Boolean(item.children && item.children.length > 0);
            const isExpanded = expandedItems[item.href] ?? false;
            return (
              <li key={item.href}>
                <div className="flex items-start gap-1 rounded-md border border-transparent px-1 py-1">
                  <div className="flex-1">{renderLinkBody(item.href, item.label, item.description, item.icon, item.group)}</div>
                  {!isCollapsed && hasChildren && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="mt-1 h-8 w-8 shrink-0"
                      aria-label={isExpanded ? "Unterseiten einklappen" : "Unterseiten ausklappen"}
                      onClick={() => {
                        setExpandedItems((prev) => ({ ...prev, [item.href]: !isExpanded }));
                      }}
                    >
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </Button>
                  )}
                </div>
                {!isCollapsed && hasChildren && isExpanded && (
                  <ul className="mt-1 space-y-1">
                    {item.children!.map((child) => (
                      <li key={child.href}>
                        {renderLinkBody(child.href, child.label, child.description, child.icon, child.group, true)}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}

export function MobileSidebarMenu() {
  return (
    <nav aria-label="Mobile Navigation" className="w-full">
      <NavigationList compact />
    </nav>
  );
}

export default function Sidebar() {
  const auth = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside className={cn("hidden border-r bg-card px-4 py-6 md:block", isCollapsed ? "w-20" : "w-72")} aria-label="Hauptnavigation">
      <div className="mb-4">
        <div className="flex items-center justify-between gap-2">
          {!isCollapsed && <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Navigation</h2>}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            aria-label={isCollapsed ? "Sidebar ausklappen" : "Sidebar einklappen"}
            onClick={() => setIsCollapsed((prev) => !prev)}
          >
            {isCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </Button>
        </div>
        {auth.status === "authenticated" && (
          <p className={cn("mt-1 text-xs text-muted-foreground", isCollapsed && "hidden")}>
            Tenant: {auth.tenantSlug || "nicht gesetzt"}
          </p>
        )}
      </div>
      <nav aria-label="Desktop Navigation">
        <NavigationList compact={isCollapsed} />
      </nav>
    </aside>
  );
}
