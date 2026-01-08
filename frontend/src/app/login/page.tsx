"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Toast } from "@/components/Toast";
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
      setToast({ kind: "success", message: "Signed in" });
      router.push("/tasks");
    } catch (err) {
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Sign in failed";
      setToast({ kind: "error", message: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/30 to-slate-900 px-6 py-16 text-white">
      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mx-auto flex max-w-md flex-col items-center gap-8"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center"
        >
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            TODO APP
          </h1>
          <p className="mt-2 text-sm text-white/60">Organize your life, one task at a time</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full"
        >
          <Card
            title="Sign In"
            className="border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl"
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
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 shadow-lg shadow-purple-500/25"
              >
                Sign In
              </Button>

              <motion.button
                type="button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="text-sm text-white/70 hover:text-white transition-colors"
                onClick={() => router.push("/signup")}
              >
                New here?{" "}
                <span className="font-semibold text-cyan-400 hover:text-cyan-300">Create account</span>
              </motion.button>
            </form>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
