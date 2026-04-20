"use client";

import { useEffect, useMemo, useState } from "react";

import RequireAuth from "@/components/auth/RequireAuth";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import {
  assignFeTask,
  completeFeTask,
  createFeTask,
  listFeTasks,
  updateFeTask,
} from "@/lib/fetests/task-api";
import type { FeTask } from "@/lib/fetests/task-types";

function statusBadge(status: FeTask["status"]): string {
  if (status === "done") {
    return "bg-emerald-100 text-emerald-800";
  }
  if (status === "in_progress") {
    return "bg-amber-100 text-amber-800";
  }
  return "bg-slate-100 text-slate-700";
}

export default function FeTestsTasksPage() {
  const auth = useAuth();
  const [tasks, setTasks] = useState<FeTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assigneeId, setAssigneeId] = useState("");

  const unreadLikeCount = useMemo(() => tasks.filter((item) => item.status !== "done").length, [tasks]);

  const reload = async () => {
    if (auth.status !== "authenticated") {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const payload = await listFeTasks(auth.tenantSlug, 1, 100);
      setTasks(payload.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tasks konnten nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void reload();
  }, [auth.status, auth.tenantSlug]);

  const createTask = async () => {
    if (auth.status !== "authenticated") {
      return;
    }
    if (!title.trim()) {
      setError("Bitte einen Titel angeben.");
      return;
    }
    const normalizedAssignee = assigneeId.trim();
    if (normalizedAssignee && !/^\d+$/.test(normalizedAssignee)) {
      setError("Assignee-ID muss eine numerische User-ID sein.");
      return;
    }

    setSaving(true);
    setError(null);
    setInfo(null);
    try {
      await createFeTask(auth.tenantSlug, {
        title: title.trim(),
        description: description.trim(),
        assignee_id: normalizedAssignee ? Number(normalizedAssignee) : undefined,
      });
      setInfo("Task wurde erstellt. Bei Zuweisung wurde eine Notification erzeugt.");
      setTitle("");
      setDescription("");
      setAssigneeId("");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Task konnte nicht erstellt werden.");
    } finally {
      setSaving(false);
    }
  };

  const assignTask = async (taskId: string, targetAssigneeId: string) => {
    if (auth.status !== "authenticated") {
      return;
    }
    const normalizedAssignee = targetAssigneeId.trim();
    if (!normalizedAssignee) {
      setError("Bitte Assignee-ID fuer die Zuweisung eingeben.");
      return;
    }
    if (!/^\d+$/.test(normalizedAssignee)) {
      setError("Assignee-ID muss eine numerische User-ID sein.");
      return;
    }
    setSaving(true);
    setError(null);
    setInfo(null);
    try {
      await assignFeTask(auth.tenantSlug, taskId, { assignee_id: Number(normalizedAssignee) });
      setInfo("Task wurde zugewiesen. Notification wurde versendet.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Task konnte nicht zugewiesen werden.");
    } finally {
      setSaving(false);
    }
  };

  const completeTask = async (taskId: string) => {
    if (auth.status !== "authenticated") {
      return;
    }
    setSaving(true);
    setError(null);
    setInfo(null);
    try {
      await completeFeTask(auth.tenantSlug, taskId);
      setInfo("Task wurde erledigt markiert. Completion-Notification wurde versendet.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Task konnte nicht abgeschlossen werden.");
    } finally {
      setSaving(false);
    }
  };

  const renameTask = async (task: FeTask) => {
    if (auth.status !== "authenticated") {
      return;
    }
    setSaving(true);
    setError(null);
    setInfo(null);
    try {
      await updateFeTask(auth.tenantSlug, task.id, {
        title: `${task.title} (updated)`,
      });
      setInfo("Task wurde aktualisiert. Update-Notification wurde versendet.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Task konnte nicht aktualisiert werden.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <RequireAuth>
      <section className="space-y-5">
        <header className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight">FE Tests: Tasks</h1>
          <p className="text-sm text-muted-foreground">
            Einfache Task-Flows fuer Frontend-Tests. Offen/In Progress: <strong>{unreadLikeCount}</strong>
          </p>
        </header>

        <div className="rounded-lg border bg-card p-4 space-y-3">
          <h2 className="text-base font-semibold">Neue Task anlegen</h2>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="Titel"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="Beschreibung"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="Assignee User-ID (optional)"
            value={assigneeId}
            onChange={(event) => setAssigneeId(event.target.value)}
          />
          <div className="flex gap-2">
            <Button type="button" onClick={() => void createTask()} disabled={saving}>
              Task erstellen
            </Button>
            <Button type="button" variant="outline" onClick={() => void reload()} disabled={loading || saving}>
              Neu laden
            </Button>
          </div>
        </div>

        <div aria-live="polite" className="space-y-2">
          {loading && (
            <p className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm text-muted-foreground">
              Tasks werden geladen...
            </p>
          )}
          {error && <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{error}</p>}
          {info && <p className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{info}</p>}
        </div>

        <ul className="space-y-3">
          {tasks.map((task) => (
            <li key={task.id} className="rounded-lg border bg-card p-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="font-semibold">{task.title}</p>
                  <p className="text-xs text-muted-foreground">
                    Task-ID: {task.id} | Assignee: {task.assignee ?? "none"}
                  </p>
                </div>
                <span className={`rounded px-2 py-1 text-xs font-medium ${statusBadge(task.status)}`}>{task.status}</span>
              </div>
              {task.description && <p className="text-sm">{task.description}</p>}
              <div className="flex flex-wrap gap-2">
                <Button type="button" size="sm" variant="outline" onClick={() => void renameTask(task)} disabled={saving || task.status === "done"}>
                  Schnell-Update
                </Button>
                <Button type="button" size="sm" variant="outline" onClick={() => void completeTask(task.id)} disabled={saving || task.status === "done"}>
                  Erledigen
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void assignTask(task.id, assigneeId || String(auth.user?.id ?? ""))}
                  disabled={saving}
                >
                  Zuweisen (Assignee-ID Feld oder ich selbst)
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </RequireAuth>
  );
}
