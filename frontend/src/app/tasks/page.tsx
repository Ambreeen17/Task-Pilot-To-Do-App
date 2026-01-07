"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Toast } from "@/components/Toast";
import { clearToken, getToken } from "@/lib/auth";
import { createTask, deleteTask, listTasks, toggleTask, type Task, type TaskPriority } from "@/lib/api";

function priorityBadge(priority: TaskPriority) {
  const cls =
    priority === "High"
      ? "bg-[#ff0066]/20 text-[#ff0066]"
      : priority === "Medium"
        ? "bg-[#ffaa00]/20 text-[#ffaa00]"
        : "bg-[#00ff88]/20 text-[#00ff88]";

  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>{priority}</span>;
}

export default function TasksPage() {
  const [token, setToken] = useState<string | null>(null);
  const [toast, setToast] = useState<{ kind: "error" | "success"; message: string } | null>(null);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<"" | "completed" | "incomplete">("");
  const [priority, setPriority] = useState<"" | TaskPriority>("");

  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newPriority, setNewPriority] = useState<TaskPriority>("Medium");

  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const t = getToken();
    setToken(t);
  }, []);

  async function refresh(currentToken: string) {
    setLoading(true);
    setToast(null);
    try {
      const res = await listTasks(currentToken, {
        search: search || undefined,
        status: status || undefined,
        priority: priority || "",
      });
      setTasks(res.tasks);
    } catch (err) {
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Failed to load";
      setToast({ kind: "error", message: msg });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) return;
    void refresh(token);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const filteredQuery = useMemo(() => ({ search, status, priority }), [search, status, priority]);

  useEffect(() => {
    if (!token) return;
    const id = window.setTimeout(() => void refresh(token), 300);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, filteredQuery]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    if (!newTitle.trim()) return;

    setCreating(true);
    try {
      const created = await createTask(token, {
        title: newTitle.trim(),
        description: newDesc.trim() ? newDesc.trim() : undefined,
        priority: newPriority,
      });
      setNewTitle("");
      setNewDesc("");
      setTasks((prev) => [created, ...prev]);
    } catch (err) {
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Create failed";
      setToast({ kind: "error", message: msg });
    } finally {
      setCreating(false);
    }
  }

  async function onToggle(id: string) {
    if (!token) return;
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)));
    try {
      await toggleTask(token, id);
    } catch (err) {
      // revert
      setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)));
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Toggle failed";
      setToast({ kind: "error", message: msg });
    }
  }

  async function onDelete(id: string) {
    if (!token) return;
    const before = tasks;
    setTasks((prev) => prev.filter((t) => t.id !== id));
    try {
      await deleteTask(token, id);
    } catch (err) {
      setTasks(before);
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Delete failed";
      setToast({ kind: "error", message: msg });
    }
  }

  function logout() {
    clearToken();
    setToken(null);
    window.location.href = "/login";
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] px-6 py-16 text-white">
        <div className="mx-auto max-w-md">
          <Card title="Not signed in">
            <div className="flex flex-col gap-3">
              <p className="text-white/70">Please sign in to view your tasks.</p>
              <Button onClick={() => (window.location.href = "/login")}>Go to login</Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] px-6 py-12 text-white">
      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-2xl font-semibold tracking-tight">2do</div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={logout}>
              Logout
            </Button>
          </div>
        </header>

        <Card>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1">
                <Input label="Search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search tasks" />
              </div>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-white/80">Status</span>
                <select
                  className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-white"
                  value={status}
                  onChange={(e) => setStatus(e.target.value as "" | "completed" | "incomplete")}
                >
                  <option value="">All</option>
                  <option value="incomplete">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-white/80">Priority</span>
                <select
                  className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-white"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as "" | TaskPriority)}
                >
                  <option value="">All</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
            </div>

            <form onSubmit={onCreate} className="flex flex-col gap-3 border-t border-white/10 pt-4">
              <div className="text-sm font-medium text-white/90">New Task</div>
              <Input label="Title" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="What do you need to do?" />
              <Input
                label="Description"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Optional"
              />
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-white/80">Priority</span>
                <select
                  className="rounded-md border border-white/10 bg-white/5 px-3 py-2 text-white"
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as TaskPriority)}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
              <Button type="submit" loading={creating} disabled={!newTitle.trim()}>
                Create Task
              </Button>
            </form>

            <div className="border-t border-white/10 pt-4">
              <div className="mb-3 text-sm font-medium text-white/90">Tasks</div>
              {loading ? <div className="text-white/60">Loading…</div> : null}
              {!loading && tasks.length === 0 ? <div className="text-white/60">No tasks yet.</div> : null}
              <ul className="flex flex-col gap-2">
                {tasks.map((t) => (
                  <li key={t.id} className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-2">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={t.completed}
                        onChange={() => void onToggle(t.id)}
                        className="h-4 w-4 accent-cyan-400"
                      />
                      <div className="flex flex-col">
                        <div className={t.completed ? "text-white/50 line-through" : "text-white"}>{t.title}</div>
                        {t.description ? <div className="text-xs text-white/60">{t.description}</div> : null}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {priorityBadge(t.priority)}
                      <Button variant="ghost" onClick={() => void onDelete(t.id)}>
                        Delete
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
