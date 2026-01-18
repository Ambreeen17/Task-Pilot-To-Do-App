"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Toast } from "@/components/Toast";
import { TaskPilotLogo } from "@/components/brand/TaskPilotLogo";
import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ kind: "error" | "success"; message: string } | null>(null);

  const emailError = useMemo(() => {
    if (!email) return null;
    return isValidEmail(email) ? null : "Please enter a valid email";
  }, [email]);

  const passwordError = useMemo(() => {
    if (!password) return null;
    return password.length >= 8 ? null : "Password must be at least 8 characters";
  }, [password]);

  const canSubmit = !emailError && !passwordError && email.length > 0 && password.length > 0;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setToast(null);
    try {
      const res = await login(email, password);
      setToken(res.access_token);
      setToast({ kind: "success", message: "Welcome back!" });
      router.push("/tasks");
    } catch (err) {
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Sign in failed";
      setToast({ kind: "error", message: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 px-6 py-16 text-white relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-violet-600/20 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-cyan-600/20 blur-3xl" />
      </div>

      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <div className="relative mx-auto flex max-w-md flex-col items-center gap-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Link href="/">
            <TaskPilotLogo size="lg" animate={true} />
          </Link>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-white/60 text-center"
        >
          Welcome back! Sign in to continue.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full"
        >
          <Card
            title="Sign In"
            className="border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl max-w-md"
          >
            <form className="flex flex-col gap-5" onSubmit={onSubmit}>
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={emailError}
                placeholder="you@example.com"
                autoComplete="email"
                className="bg-white/5 border-white/10"
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={passwordError}
                placeholder="••••••••"
                autoComplete="current-password"
                className="bg-white/5 border-white/10"
              />

              <Button
                type="submit"
                loading={submitting}
                disabled={!canSubmit}
                className="bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 shadow-lg shadow-violet-500/25"
              >
                Sign In
              </Button>

              <motion.div
                className="text-sm text-white/70 text-center"
              >
                New here?{" "}
                <Link href="/signup" className="font-semibold text-cyan-400 hover:text-cyan-300 transition-colors">
                  Create account
                </Link>
              </motion.div>
            </form>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
