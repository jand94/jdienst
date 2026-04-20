"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import RequireAuth from "@/components/auth/RequireAuth";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import {
  archiveNotification,
  bulkArchiveNotifications,
  bulkMarkNotificationsAsRead,
  getUnreadNotificationCount,
  listNotifications,
  markNotificationAsRead,
} from "@/lib/notifications/notification-api";
import { connectNotificationRealtime } from "@/lib/notifications/notification-realtime";
import type { NotificationItem } from "@/lib/notifications/notification-types";

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("de-DE");
}

export default function NotificationsPage() {
  const auth = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [includeArchived, setIncludeArchived] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const loadNotifications = useCallback(
    async (options?: { silent?: boolean }) => {
      if (auth.status !== "authenticated") {
        return;
      }
      const isSilent = Boolean(options?.silent);
      if (!isSilent) {
        setLoading(true);
      }
      setError(null);
      try {
        const payload = await listNotifications(auth.tenantSlug, includeArchived, page, pageSize);
        setNotifications(payload.results);
        setTotalCount(payload.count);
        setHasNextPage(Boolean(payload.next));
        setHasPreviousPage(Boolean(payload.previous));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Notifications konnten nicht geladen werden.");
      } finally {
        if (!isSilent) {
          setLoading(false);
        }
      }
    },
    [auth.status, auth.tenantSlug, includeArchived, page, pageSize],
  );

  useEffect(() => {
    let active = true;
    const run = async () => {
      if (!active) {
        return;
      }
      await loadNotifications();
    };
    void run();
    return () => {
      active = false;
    };
  }, [loadNotifications]);

  useEffect(() => {
    if (auth.status !== "authenticated") {
      return;
    }
    const disconnect = connectNotificationRealtime(
      (eventPayload) => {
        if (eventPayload.event === "notification.created") {
          void loadNotifications({ silent: true });
          setInfo("Neue Notification eingegangen.");
        }
      },
      () => {
        setError("Realtime-Verbindung fuer Notifications ist aktuell nicht verfuegbar.");
      },
    );
    return () => {
      disconnect?.();
    };
  }, [auth.status, loadNotifications]);

  const unreadCount = useMemo(
    () => notifications.filter((notification) => notification.status === "unread").length,
    [notifications],
  );
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const onMarkSingle = async (notificationId: string) => {
    if (auth.status !== "authenticated") {
      return;
    }
    setActionLoading(true);
    setError(null);
    setInfo(null);
    try {
      const updated = await markNotificationAsRead(auth.tenantSlug, notificationId);
      setNotifications((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setInfo("Notification wurde als gelesen markiert.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification konnte nicht aktualisiert werden.");
    } finally {
      setActionLoading(false);
    }
  };

  const onMarkAllVisibleUnread = async () => {
    if (auth.status !== "authenticated") {
      return;
    }
    const unreadIds = notifications.filter((item) => item.status === "unread").map((item) => item.id);
    if (unreadIds.length === 0) {
      return;
    }
    setActionLoading(true);
    setError(null);
    setInfo(null);
    try {
      await bulkMarkNotificationsAsRead(auth.tenantSlug, unreadIds);
      setNotifications((prev) =>
        prev.map((item) => (item.status === "unread" ? { ...item, status: "read", read_at: new Date().toISOString() } : item)),
      );
      setInfo(`${unreadIds.length} Notifications wurden als gelesen markiert.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bulk-Markierung fehlgeschlagen.");
    } finally {
      setActionLoading(false);
    }
  };

  const onArchiveSingle = async (notificationId: string) => {
    if (auth.status !== "authenticated") {
      return;
    }
    setActionLoading(true);
    setError(null);
    setInfo(null);
    try {
      const updated = await archiveNotification(auth.tenantSlug, notificationId);
      setNotifications((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      const counter = await getUnreadNotificationCount(auth.tenantSlug);
      setInfo(`Notification archiviert. Ungelesen gesamt: ${counter.unread_count}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification konnte nicht archiviert werden.");
    } finally {
      setActionLoading(false);
    }
  };

  const onArchiveAllVisible = async () => {
    if (auth.status !== "authenticated") {
      return;
    }
    const visibleIds = notifications.map((item) => item.id);
    if (visibleIds.length === 0) {
      return;
    }
    setActionLoading(true);
    setError(null);
    setInfo(null);
    try {
      await bulkArchiveNotifications(auth.tenantSlug, visibleIds);
      await loadNotifications({ silent: true });
      setInfo(`${visibleIds.length} sichtbare Notifications archiviert.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bulk-Archivierung fehlgeschlagen.");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <RequireAuth>
      <section className="space-y-5">
        <header className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Notifications</h1>
          <p className="text-sm text-muted-foreground">
            In-App Benachrichtigungen inklusive Read-Status. Ungelesen: <strong>{unreadCount}</strong>
          </p>
        </header>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setIncludeArchived((prev) => !prev);
              setPage(1);
            }}
          >
            {includeArchived ? "Archivierte ausblenden" : "Archivierte einblenden"}
          </Button>
          <Button type="button" onClick={onMarkAllVisibleUnread} disabled={actionLoading || unreadCount === 0}>
            Alle sichtbaren Ungelesenen als gelesen markieren
          </Button>
          <Button type="button" variant="outline" onClick={onArchiveAllVisible} disabled={actionLoading || notifications.length === 0}>
            Sichtbare archivieren
          </Button>
          <Button type="button" variant="outline" onClick={() => void loadNotifications()} disabled={loading || actionLoading}>
            Liste aktualisieren
          </Button>
        </div>

        <div aria-live="polite" className="space-y-2">
          {loading && (
            <p className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm text-muted-foreground">
              Notifications werden geladen...
            </p>
          )}
          {error && <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{error}</p>}
          {info && <p className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{info}</p>}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 rounded-md border bg-muted/20 px-3 py-2 text-sm">
          <div className="text-muted-foreground">
            Seite <strong>{page}</strong> von <strong>{totalPages}</strong> | Eintraege gesamt: <strong>{totalCount}</strong>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              Seite groesse
              <select
                className="rounded border bg-background px-2 py-1 text-xs"
                value={pageSize}
                onChange={(event) => {
                  setPageSize(Number(event.target.value));
                  setPage(1);
                }}
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </label>
            <Button type="button" size="sm" variant="outline" disabled={!hasPreviousPage || loading} onClick={() => setPage((prev) => Math.max(1, prev - 1))}>
              Zurueck
            </Button>
            <Button type="button" size="sm" variant="outline" disabled={!hasNextPage || loading} onClick={() => setPage((prev) => prev + 1)}>
              Weiter
            </Button>
          </div>
        </div>

        {!loading && notifications.length === 0 ? (
          <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
            Keine Notifications vorhanden.
          </p>
        ) : (
          <ul aria-busy={loading || actionLoading} className="space-y-3">
            {notifications.map((item) => (
              <li key={item.id} className="rounded-lg border bg-card p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="space-y-1">
                    <p className="text-sm font-semibold">{item.title}</p>
                    <p className="text-xs text-muted-foreground">
                      Typ: {item.notification_type.title} ({item.notification_type.key})
                    </p>
                  </div>
                  <span
                    aria-label={`Status ${item.status}`}
                    className={`rounded px-2 py-1 text-xs font-medium ${
                      item.status === "unread"
                        ? "bg-amber-100 text-amber-800"
                        : item.status === "read"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <p className="mt-2 text-sm">{item.body}</p>
                <p className="mt-2 text-xs text-muted-foreground">Veroeffentlicht: {formatDate(item.published_at)}</p>
                <div className="mt-3 flex items-center gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void onMarkSingle(item.id)}
                    disabled={actionLoading || item.status !== "unread"}
                  >
                    Als gelesen markieren
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void onArchiveSingle(item.id)}
                    disabled={actionLoading || item.status === "archived"}
                  >
                    Archivieren
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </RequireAuth>
  );
}
