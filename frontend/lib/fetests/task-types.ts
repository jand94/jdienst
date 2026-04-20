export type FeTaskStatus = "open" | "in_progress" | "done";

export type FeTask = {
  id: string;
  tenant: string;
  title: string;
  description: string;
  status: FeTaskStatus;
  assignee: number | null;
  assigned_by: number | null;
  due_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
  updated_by: number | null;
};

export type FeTaskPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: FeTask[];
};
