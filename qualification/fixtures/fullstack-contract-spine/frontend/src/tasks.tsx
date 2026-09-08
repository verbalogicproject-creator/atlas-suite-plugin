export type Task = { id: number; title: string };

export async function listTasks(token: string): Promise<Task[]> {
  const response = await fetch("/api/tasks", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (response.status === 401) throw new Error("unauthorized");
  if (!response.ok) throw new Error("task-list-failed");
  return (await response.json()) as Task[];
}
