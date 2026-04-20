"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bell, MenuIcon, Star, Wifi } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/hooks/use-auth";
import { getVisibleNavigationItems } from "@/lib/navigation/navigation-policy";
import { getNavigationIcon } from "@/lib/navigation/icons";
import { getNavigationGroupColors } from "@/lib/navigation/group-colors";
import { getUnreadNotificationCount, listNotifications, markNotificationAsRead } from "@/lib/notifications/notification-api";
import { connectNotificationRealtime } from "@/lib/notifications/notification-realtime";
import type { NotificationItem } from "@/lib/notifications/notification-types";
import { useCurrentBreakpoint, useResponsiveValue } from "@/hooks/use-breakpoint";
import { responsiveTokens } from "@/lib/responsive-tokens";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("de-DE");
}

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const auth = useAuth();
  const currentBreakpoint = useCurrentBreakpoint();
  const mobileSheetWidth = useResponsiveValue(
    {
      xs: "w-full",
      sm: "w-80",
    },
    "w-80",
  );
  const isActiveLink = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
  const visibleItems = getVisibleNavigationItems(auth);
  const topLevelItems = visibleItems.map((item) => ({ ...item, children: [] }));
  const favoriteSet = new Set(auth.navigationFavorites);
  const [isNotificationRealtimeConnected, setIsNotificationRealtimeConnected] = useState(false);
  const [notificationDropdownOpen, setNotificationDropdownOpen] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState<NotificationItem[]>([]);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const [isUnreadLoading, setIsUnreadLoading] = useState(false);
  const [unreadError, setUnreadError] = useState<string | null>(null);
  const [markingNotificationId, setMarkingNotificationId] = useState<string | null>(null);
  const notificationDropdownRef = useRef<HTMLDivElement | null>(null);

  const loadUnreadNotifications = useCallback(
    async (options?: { silent?: boolean }) => {
      if (auth.status !== "authenticated") {
        setUnreadNotifications([]);
        setUnreadNotificationCount(0);
        setUnreadError(null);
        return;
      }

      const isSilent = Boolean(options?.silent);
      if (!isSilent) {
        setIsUnreadLoading(true);
      }
      setUnreadError(null);
      try {
        const [notificationPage, unreadCounter] = await Promise.all([
          listNotifications(auth.tenantSlug, false, 1, 10),
          getUnreadNotificationCount(auth.tenantSlug),
        ]);
        setUnreadNotifications(notificationPage.results.filter((item) => item.status === "unread"));
        setUnreadNotificationCount(unreadCounter.unread_count);
      } catch (error) {
        setUnreadError(error instanceof Error ? error.message : "Ungelesene Notifications konnten nicht geladen werden.");
      } finally {
        if (!isSilent) {
          setIsUnreadLoading(false);
        }
      }
    },
    [auth.status, auth.tenantSlug],
  );

  const handleMarkNotificationRead = async (notificationId: string) => {
    if (auth.status !== "authenticated") {
      return;
    }

    setMarkingNotificationId(notificationId);
    setUnreadError(null);
    try {
      await markNotificationAsRead(auth.tenantSlug, notificationId);
      setUnreadNotifications((prev) => prev.filter((item) => item.id !== notificationId));
      setUnreadNotificationCount((prev) => Math.max(0, prev - 1));
      toast.success("Notification als gelesen markiert.");
    } catch (error) {
      setUnreadError(error instanceof Error ? error.message : "Notification konnte nicht als gelesen markiert werden.");
    } finally {
      setMarkingNotificationId(null);
    }
  };

  useEffect(() => {
    if (auth.status !== "authenticated") {
      setIsNotificationRealtimeConnected(false);
      setUnreadNotifications([]);
      setUnreadNotificationCount(0);
      setNotificationDropdownOpen(false);
      return;
    }
    void loadUnreadNotifications();
    const disconnect = connectNotificationRealtime(
      (eventPayload) => {
        if (eventPayload.event !== "notification.created") {
          return;
        }
        const title = typeof eventPayload.data?.title === "string" ? eventPayload.data.title : "Neue Notification";
        const body = typeof eventPayload.data?.body === "string" ? eventPayload.data.body : "";
        toast.success(title, {
          description: body,
        });
        void loadUnreadNotifications({ silent: true });
      },
      () => {
        setIsNotificationRealtimeConnected(false);
      },
      {
        onOpen: () => {
          setIsNotificationRealtimeConnected(true);
        },
        onClose: () => {
          setIsNotificationRealtimeConnected(false);
        },
      },
    );
    return () => {
      disconnect?.();
      setIsNotificationRealtimeConnected(false);
    };
  }, [auth.status, loadUnreadNotifications]);

  useEffect(() => {
    if (!notificationDropdownOpen) {
      return;
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (!notificationDropdownRef.current) {
        return;
      }
      if (event.target instanceof Node && !notificationDropdownRef.current.contains(event.target)) {
        setNotificationDropdownOpen(false);
      }
    };

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setNotificationDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscapeKey);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscapeKey);
    };
  }, [notificationDropdownOpen]);

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur" data-breakpoint={currentBreakpoint}>
      <div className={cn(responsiveTokens.container, "flex h-16 items-center justify-between")}>
        <Link href="/" className="text-base font-semibold">
          jdienst
        </Link>

        <nav aria-label="Top Navigation" className="hidden items-center gap-5 md:flex">
          {topLevelItems.map((item) => {
            const isActive = isActiveLink(item.href);
            const NavIcon = getNavigationIcon(item.icon);
            const colorClasses = getNavigationGroupColors(item.group);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "inline-flex items-center gap-2 border-b-2 border-transparent pb-1 text-sm text-muted-foreground transition-colors hover:text-foreground",
                  isActive && "border-b-primary font-medium",
                  isActive && colorClasses.activeText,
                )}
              >
                <NavIcon className={cn("h-4 w-4", colorClasses.icon)} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          {auth.status === "authenticated" && (
            <div className="relative" ref={notificationDropdownRef}>
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="relative inline-flex items-center gap-2"
                aria-label="Ungelesene Notifications anzeigen"
                aria-expanded={notificationDropdownOpen}
                onClick={() => {
                  const nextOpen = !notificationDropdownOpen;
                  setNotificationDropdownOpen(nextOpen);
                  if (nextOpen) {
                    void loadUnreadNotifications();
                  }
                }}
              >
                <Bell className="h-4 w-4" />
                <span className="hidden md:inline">Notifications</span>
                {unreadNotificationCount > 0 && (
                  <span className="absolute -right-2 -top-2 rounded-full bg-destructive px-1.5 py-0.5 text-[10px] font-semibold text-destructive-foreground">
                    {unreadNotificationCount > 99 ? "99+" : unreadNotificationCount}
                  </span>
                )}
              </Button>
              {notificationDropdownOpen && (
                <div className="absolute right-0 z-50 mt-2 w-[22rem] max-w-[calc(100vw-2rem)] rounded-md border bg-popover p-3 shadow-lg">
                  <div className="space-y-1 pb-2">
                    <p className="text-sm font-semibold">Ungelesene Notifications</p>
                    <p className="text-xs text-muted-foreground">Es werden nur ungelesene Eintraege angezeigt.</p>
                  </div>
                  <div className="max-h-80 space-y-2 overflow-auto pr-1">
                    {isUnreadLoading && (
                      <p className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm text-muted-foreground">
                        Ungelesene Notifications werden geladen...
                      </p>
                    )}
                    {unreadError && (
                      <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
                        {unreadError}
                      </p>
                    )}
                    {!isUnreadLoading && unreadNotifications.length === 0 && !unreadError && (
                      <p className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
                        Keine ungelesenen Notifications.
                      </p>
                    )}
                    {unreadNotifications.length > 0 && (
                      <ul className="space-y-2">
                        {unreadNotifications.map((item) => (
                          <li key={item.id} className="rounded-md border bg-card p-3">
                            <p className="text-sm font-semibold">{item.title}</p>
                            <p className="mt-1 text-sm text-muted-foreground">{item.body}</p>
                            <p className="mt-2 text-xs text-muted-foreground">{formatDate(item.published_at)}</p>
                            <div className="mt-2">
                              <Button
                                type="button"
                                size="sm"
                                variant="outline"
                                disabled={markingNotificationId === item.id}
                                onClick={() => {
                                  void handleMarkNotificationRead(item.id);
                                }}
                              >
                                Als gelesen markieren
                              </Button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <Button asChild type="button" className="mt-3 w-full" onClick={() => setNotificationDropdownOpen(false)}>
                    <Link href="/notifications">Zu allen Nachrichten</Link>
                  </Button>
                </div>
              )}
            </div>
          )}
          {auth.status === "authenticated" && (
            <Button
              type="button"
              size="sm"
              variant="outline"
              className={cn(
                "hidden md:inline-flex items-center gap-2 border-0 text-white",
                isNotificationRealtimeConnected
                  ? "bg-emerald-600 hover:bg-emerald-700"
                  : "bg-red-600 hover:bg-red-700",
              )}
              aria-label={isNotificationRealtimeConnected ? "Notification Realtime verbunden" : "Notification Realtime getrennt"}
            >
              <Wifi className="h-4 w-4" />
              {isNotificationRealtimeConnected ? "Realtime verbunden" : "Realtime getrennt"}
            </Button>
          )}
          {auth.status === "authenticated" ? (
            <>
              <span className="hidden text-sm text-muted-foreground md:inline">
                {auth.user?.username}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  void auth.signOut().then(() => {
                    router.replace("/login");
                  });
                }}
              >
                Logout
              </Button>
            </>
          ) : (
            <Button asChild variant="default" size="sm">
              <Link href="/login">Login</Link>
            </Button>
          )}

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="md:hidden" aria-label="Mobile Navigation oeffnen">
                <MenuIcon />
                Menue
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className={cn("p-0", mobileSheetWidth)}>
              <SheetHeader className={responsiveTokens.mobilePanelHeaderPadding}>
                <SheetTitle>Navigation</SheetTitle>
                <SheetDescription>Schnellzugriff auf die wichtigsten Bereiche.</SheetDescription>
              </SheetHeader>
              <div className={responsiveTokens.mobilePanelPadding}>
                <nav aria-label="Mobile Navigation" className="w-full">
                  <ul className="space-y-1">
                    {visibleItems.map((item) => {
                      const isActive = isActiveLink(item.href);
                      const NavIcon = getNavigationIcon(item.icon);
                      const colorClasses = getNavigationGroupColors(item.group);

                      return (
                        <li key={item.href}>
                          <SheetClose asChild>
                            <Link
                              href={item.href}
                              aria-current={isActive ? "page" : undefined}
                              className={cn(
                                "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                                isActive && cn("font-medium", colorClasses.activeBorder, colorClasses.activeText),
                              )}
                            >
                              <span className="inline-flex items-center gap-2 font-medium">
                                <NavIcon className={cn("h-4 w-4", colorClasses.icon)} />
                                {item.label}
                              </span>
                              <p className="text-xs text-muted-foreground">{item.description}</p>
                            </Link>
                          </SheetClose>
                          {auth.status === "authenticated" && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="mt-1 h-8 w-8 shrink-0"
                              aria-label={favoriteSet.has(item.href) ? "Favorit entfernen" : "Als Favorit markieren"}
                              onClick={() => {
                                void auth.toggleNavigationFavorite(item.href);
                              }}
                            >
                              <Star className={cn("h-4 w-4", favoriteSet.has(item.href) && "fill-current text-amber-500")} />
                            </Button>
                          )}
                          {item.children && item.children.length > 0 && (
                            <ul className="mt-1 space-y-1 pl-6">
                              {item.children.map((child) => {
                                const isChildActive = isActiveLink(child.href);
                                const ChildIcon = getNavigationIcon(child.icon);
                                const childColorClasses = getNavigationGroupColors(child.group);
                                return (
                                  <li key={child.href}>
                                    <SheetClose asChild>
                                      <Link
                                        href={child.href}
                                        aria-current={isChildActive ? "page" : undefined}
                                        className={cn(
                                          "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                                          isChildActive &&
                                            cn("font-medium", childColorClasses.activeBorder, childColorClasses.activeText),
                                        )}
                                      >
                                        <span className="inline-flex items-center gap-2 font-medium">
                                          <ChildIcon className={cn("h-4 w-4", childColorClasses.icon)} />
                                          {child.label}
                                        </span>
                                        <p className="text-xs text-muted-foreground">{child.description}</p>
                                      </Link>
                                    </SheetClose>
                                    {auth.status === "authenticated" && (
                                      <Button
                                        type="button"
                                        variant="ghost"
                                        size="icon"
                                        className="mt-1 h-8 w-8 shrink-0"
                                        aria-label={favoriteSet.has(child.href) ? "Favorit entfernen" : "Als Favorit markieren"}
                                        onClick={() => {
                                          void auth.toggleNavigationFavorite(child.href);
                                        }}
                                      >
                                        <Star
                                          className={cn(
                                            "h-4 w-4",
                                            favoriteSet.has(child.href) && "fill-current text-amber-500",
                                          )}
                                        />
                                      </Button>
                                    )}
                                  </li>
                                );
                              })}
                            </ul>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </nav>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
