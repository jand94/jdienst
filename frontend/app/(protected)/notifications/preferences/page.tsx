"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import RequireAuth from "@/components/auth/RequireAuth";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import {
  listNotificationPreferences,
  listNotifications,
  updateNotificationPreference,
} from "@/lib/notifications/notification-api";
import type { NotificationPreference, NotificationTypeSummary } from "@/lib/notifications/notification-types";

const SUPPORTED_CHANNELS: Array<"in_app" | "email"> = ["in_app", "email"];

function channelLabel(channel: "in_app" | "email"): string {
  if (channel === "in_app") {
    return "In-App";
  }
  return "Mail";
}

export default function NotificationPreferencesPage() {
  const auth = useAuth();
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [knownTypes, setKnownTypes] = useState<NotificationTypeSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const loadPreferences = useCallback(async () => {
    if (auth.status !== "authenticated") {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [loadedPreferences, loadedNotifications] = await Promise.all([
        listNotificationPreferences(auth.tenantSlug),
        listNotifications(auth.tenantSlug, true),
      ]);
      setPreferences(loadedPreferences);
      const typeMap = new Map<string, NotificationTypeSummary>();
      for (const preference of loadedPreferences) {
        typeMap.set(preference.notification_type.key, preference.notification_type);
      }
      for (const notification of loadedNotifications) {
        typeMap.set(notification.notification_type.key, notification.notification_type);
      }
      setKnownTypes(Array.from(typeMap.values()).sort((a, b) => a.title.localeCompare(b.title)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification-Praeferenzen konnten nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  }, [auth.status, auth.tenantSlug]);

  useEffect(() => {
    let active = true;
    const run = async () => {
      if (!active) {
        return;
      }
      await loadPreferences();
    };
    void run();
    return () => {
      active = false;
    };
  }, [loadPreferences]);

  const preferenceMap = useMemo(() => {
    const map = new Map<string, NotificationPreference>();
    for (const preference of preferences) {
      map.set(`${preference.notification_type.key}:${preference.channel}`, preference);
    }
    return map;
  }, [preferences]);

  const resolveChecked = (typeKey: string, channel: "in_app" | "email"): boolean => {
    const existing = preferenceMap.get(`${typeKey}:${channel}`);
    if (existing) {
      return existing.is_subscribed;
    }
    const type = knownTypes.find((candidate) => candidate.key === typeKey);
    if (!type) {
      return false;
    }
    return type.default_channels.includes(channel);
  };

  const onToggle = async (typeKey: string, channel: "in_app" | "email", nextValue: boolean) => {
    if (auth.status !== "authenticated") {
      return;
    }
    const token = `${typeKey}:${channel}`;
    setSavingKey(token);
    setError(null);
    setInfo(null);
    try {
      const updated = await updateNotificationPreference(auth.tenantSlug, {
        notification_type_key: typeKey,
        channel,
        is_subscribed: nextValue,
      });
      setPreferences((prev) => {
        const filtered = prev.filter(
          (entry) => !(entry.notification_type.key === updated.notification_type.key && entry.channel === updated.channel),
        );
        return [...filtered, updated];
      });
      setInfo(`Praeferenz gespeichert: ${typeKey} / ${channelLabel(channel)}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Praeferenz konnte nicht gespeichert werden.");
    } finally {
      setSavingKey(null);
    }
  };

  return (
    <RequireAuth>
      <section className="space-y-5">
        <header className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">Notification Praeferenzen</h1>
          <p className="text-sm text-muted-foreground">
            Lege pro Notification-Typ fest, ob du In-App und/oder Mail Benachrichtigungen erhalten moechtest.
          </p>
        </header>

        <div aria-live="polite" className="space-y-2">
          {loading && (
            <p className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm text-muted-foreground">
              Praeferenzen werden geladen...
            </p>
          )}
          {error && <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{error}</p>}
          {info && <p className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{info}</p>}
        </div>

        {!loading && knownTypes.length === 0 ? (
          <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
            Noch keine Notification-Typen gefunden. Sobald Notifications vorliegen, kannst du sie hier konfigurieren.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="min-w-full border-collapse text-sm">
              <caption className="sr-only">
                Notification-Praeferenzen je Notification-Typ mit Kanaelen In-App und Mail.
              </caption>
              <thead className="bg-muted/50">
                <tr>
                  <th scope="col" className="px-3 py-2 text-left font-medium">Notification-Typ</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium">Schluessel</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium">In-App</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium">Mail</th>
                </tr>
              </thead>
              <tbody>
                {knownTypes.map((typeItem) => (
                  <tr key={typeItem.key} className="border-t">
                    <th scope="row" className="px-3 py-2 text-left">
                      <p className="font-medium">{typeItem.title}</p>
                      {typeItem.description && <p className="text-xs text-muted-foreground">{typeItem.description}</p>}
                    </th>
                    <td className="px-3 py-2 text-xs text-muted-foreground">{typeItem.key}</td>
                    {SUPPORTED_CHANNELS.map((channel) => {
                      const checked = resolveChecked(typeItem.key, channel);
                      const rowKey = `${typeItem.key}:${channel}`;
                      const inputId = `pref-${typeItem.key}-${channel}`;
                      return (
                        <td key={rowKey} className="px-3 py-2">
                          <label htmlFor={inputId} className="inline-flex items-center gap-2">
                            <input
                              id={inputId}
                              type="checkbox"
                              checked={checked}
                              disabled={savingKey === rowKey}
                              aria-label={`${typeItem.title}: ${channelLabel(channel)} aktivieren`}
                              onChange={(event) => {
                                void onToggle(typeItem.key, channel, event.target.checked);
                              }}
                            />
                            <span>{channelLabel(channel)}</span>
                          </label>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              void loadPreferences();
            }}
            disabled={loading}
          >
            Aktualisieren
          </Button>
        </div>
      </section>
    </RequireAuth>
  );
}
