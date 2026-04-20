import { httpClient } from "@/lib/api/http-client";
import type { FeTask, FeTaskPage } from "@/lib/fetests/task-types";

export async function listFeTasks(tenantSlug: string, page = 1, pageSize = 50): Promise<FeTaskPage> {
  const query = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  }).toString();
  return httpClient.get<FeTaskPage>(`/api/fetests/v1/tasks/?${query}`, {
    auth: true,
    tenantSlug,
  });
}

export async function createFeTask(
  tenantSlug: string,
  payload: {
    title: string;
    description?: string;
    assignee_id?: number;
    due_at?: string | null;
  },
): Promise<FeTask> {
  return httpClient.post<FeTask>("/api/fetests/v1/tasks/", payload, {
    auth: true,
    tenantSlug,
  });
}

export async function assignFeTask(
  tenantSlug: string,
  taskId: string,
  payload: { assignee_id: number },
): Promise<FeTask> {
  return httpClient.post<FeTask>(`/api/fetests/v1/tasks/${taskId}/assign/`, payload, {
    auth: true,
    tenantSlug,
  });
}

export async function updateFeTask(
  tenantSlug: string,
  taskId: string,
  payload: {
    title?: string;
    description?: string;
    due_at?: string | null;
  },
): Promise<FeTask> {
  return httpClient.patch<FeTask>(`/api/fetests/v1/tasks/${taskId}/`, payload, {
    auth: true,
    tenantSlug,
  });
}

export async function completeFeTask(tenantSlug: string, taskId: string): Promise<FeTask> {
  return httpClient.post<FeTask>(`/api/fetests/v1/tasks/${taskId}/complete/`, {}, {
    auth: true,
    tenantSlug,
  });
}
