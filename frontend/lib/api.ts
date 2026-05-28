const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TaskResponse {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  output: string | null;
}

export async function askDigitalTwin(question: string): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_type: "digital_twin", input: question }),
  });
  if (!res.ok) throw new Error("Failed to submit question");
  return res.json();
}

export async function pollTask(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!res.ok) throw new Error("Failed to poll task");
  return res.json();
}

export function getVoiceUrl(taskId: string): string {
  return `${API_BASE}/voice/task/${taskId}`;
}
