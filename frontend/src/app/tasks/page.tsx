"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Toast } from "@/components/Toast";
import { clearToken, getToken } from "@/lib/auth";
import { createTask, deleteTask, listTasks, toggleTask, type Task, type TaskPriority } from "@/lib/api";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
  exit: {
    x: -100,
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

function priorityBadge(priority: TaskPriority) {
  const colors = {
    High: "bg-gradient-to-r from-red-500/20 to-pink-500/20 text-red-400 border border-red-500/30",
    Medium: "bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border border-amber-500/30",
    Low: "bg-gradient-to-r from-emerald-500/20 to-green-500/20 text-emerald-400 border border-emerald-500/30",
  };

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold tracking-wide shadow-lg ${colors[priority]}`}>
      {priority}
    </span>
  );
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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-6 py-16 text-white">
        <div className="mx-auto max-w-md">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card title="Not signed in">
              <div className="flex flex-col gap-3">
                <p className="text-white/70">Please sign in to view your tasks.</p>
                <Button onClick={() => (window.location.href = "/login")}>Go to login</Button>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 px-6 py-12 text-white">
      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              TODO APP
            </h1>
            <p className="mt-1 text-sm text-white/60">Organize your life, one task at a time</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              onClick={logout}
              className="rounded-xl border border-white/10 hover:bg-white/10 hover:border-white/20"
            >
              Logout
            </Button>
          </div>
        </motion.header>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl">
            <div className="flex flex-col gap-6 p-6">
              <motion.div
                className="flex flex-col gap-3 sm:flex-row sm:items-end"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <div className="flex-1">
                  <Input
                    label="Search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search tasks..."
                    className="bg-white/5 border-white/10"
                  />
                </div>
                <label className="flex flex-col gap-1 text-sm">
                  <span className="text-white/80 font-medium">Status</span>
                  <select
                    className="rounded-xl border border-white/10 bg-black px-4 py-2.5 text-white font-sans transition-all hover:border-cyan-500/50 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
                    value={status}
                    onChange={(e) => setStatus(e.target.value as "" | "completed" | "incomplete")}
                  >
                    <option value="">All</option>
                    <option value="incomplete">Active</option>
                    <option value="completed">Completed</option>
                  </select>
                </label>
                <label className="flex flex-col gap-1 text-sm">
                  <span className="text-white/80 font-medium">Priority</span>
                  <select
                    className="rounded-xl border border-white/10 bg-black px-4 py-2.5 text-white font-sans transition-all hover:border-purple-500/50 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as "" | TaskPriority)}
                  >
                    <option value="">All</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </label>
              </motion.div>

              <motion.form
                onSubmit={onCreate}
                className="flex flex-col gap-3 border-t border-white/10 pt-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="text-sm font-semibold text-white/90 uppercase tracking-wider">Create New Task</div>
                <Input
                  label="Title"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="What do you need to do?"
                  className="bg-white/5 border-white/10"
                />
                <Input
                  label="Description"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Optional description..."
                  className="bg-white/5 border-white/10"
                />
                <label className="flex flex-col gap-1 text-sm">
                  <span className="text-white/80 font-medium">Priority</span>
                  <select
                    className="rounded-xl border border-white/10 bg-black px-4 py-2.5 text-white font-sans transition-all hover:border-pink-500/50 focus:border-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20"
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value as TaskPriority)}
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </label>
                <Button
                  type="submit"
                  loading={creating}
                  disabled={!newTitle.trim()}
                  className="mt-2 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 shadow-lg shadow-purple-500/25"
                >
                  Create Task
                </Button>
              </motion.form>

              <div className="border-t border-white/10 pt-6">
                <div className="mb-4 flex items-center justify-between">
                  <div className="text-sm font-semibold text-white/90 uppercase tracking-wider">Your Tasks</div>
                  <div className="text-xs text-white/50">{tasks.length} tasks</div>
                </div>
                {loading ? (
                  <div className="flex items-center justify-center py-8 text-white/60">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-8 w-8 rounded-full border-2 border-cyan-500 border-t-transparent"
                    />
                  </div>
                ) : null}
                {!loading && tasks.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-12 text-white/60"
                  >
                    <svg className="mb-4 h-16 w-16 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    <p>No tasks yet. Create your first task above!</p>
                  </motion.div>
                ) : null}
                <AnimatePresence mode="popLayout">
                  {tasks.map((t, index) => (
                    <motion.li
                      key={t.id}
                      variants={itemVariants}
                      initial="hidden"
                      animate="visible"
                      exit="exit"
                      transition={{ delay: index * 0.05 }}
                      className="group flex items-center justify-between rounded-2xl border border-white/10 bg-gradient-to-r from-white/5 to-white/0 p-4 transition-all hover:border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-500/10"
                    >
                      <div className="flex items-center gap-4">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => void onToggle(t.id)}
                          className={`flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all ${
                            t.completed
                              ? "border-cyan-500 bg-cyan-500"
                              : "border-white/30 hover:border-cyan-400"
                          }`}
                        >
                          {t.completed && (
                            <motion.svg
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="h-4 w-4 text-black"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </motion.svg>
                          )}
                        </motion.button>
                        <div className="flex flex-col">
                          <div
                            className={`text-base font-medium transition-all ${
                              t.completed ? "text-white/40 line-through" : "text-white"
                            }`}
                          >
                            {t.title}
                          </div>
                          {t.description ? (
                            <div className="mt-1 text-xs text-white/60">{t.description}</div>
                          ) : null}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {priorityBadge(t.priority)}
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => void onDelete(t.id)}
                          className="rounded-lg border border-red-500/30 px-3 py-1.5 text-sm text-red-400 transition-all hover:bg-red-500/20 hover:border-red-500/50"
                        >
                          Delete
                        </motion.button>
                      </div>
                    </motion.li>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
