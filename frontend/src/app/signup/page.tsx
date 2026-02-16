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
import { register, login } from "@/lib/api";
import { setToken, setUsername } from "@/lib/auth";

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default function SignupPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ kind: "error" | "success"; message: string } | null>(null);

  const fullNameError = useMemo(() => {
    if (!fullName) return null;
    return fullName.trim().length >= 1 ? null : "Please enter your full name";
  }, [fullName]);

  const emailError = useMemo(() => {
    if (!email) return null;
    return isValidEmail(email) ? null : "Please enter a valid email";
  }, [email]);

  const passwordError = useMemo(() => {
    if (!password) return null;
    return password.length >= 8 ? null : "Password must be at least 8 characters";
  }, [password]);

  const canSubmit = !fullNameError && !emailError && !passwordError && fullName.length > 0 && email.length > 0 && password.length > 0;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setToast(null);
    try {
      await register(email, fullName, password);
      setToast({ kind: "success", message: "Account created successfully!" });
      // Auto-login after signup and redirect to tasks
      const loginResponse = await login(email, password);
      setToken(loginResponse.access_token);
      setUsername(loginResponse.user_name);
      router.push("/tasks");
    } catch (err) {
      const msg = typeof err === "object" && err && "detail" in err ? String((err as { detail: unknown }).detail) : "Sign up failed";
      setToast({ kind: "error", message: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 px-6 py-16 text-white relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-80 w-80 rounded-full bg-cyan-600/20 blur-3xl" />
        <div className="absolute bottom-1/3 -right-40 h-96 w-96 rounded-full bg-violet-600/20 blur-3xl" />
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
          Create your account and start navigating tasks smarter.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full"
        >
          <Card
            title="Create Account"
            className="border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl max-w-md"
          >
            <form className="flex flex-col gap-5" onSubmit={onSubmit}>
              <Input
                label="Full Name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                error={fullNameError}
                placeholder="John Doe"
                autoComplete="name"
                className="bg-white/5 border-white/10"
              />
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
                autoComplete="new-password"
                className="bg-white/5 border-white/10"
              />

              <Button
                type="submit"
                loading={submitting}
                disabled={!canSubmit}
                variant="secondary"
                className="bg-gradient-to-r from-cyan-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 shadow-lg shadow-cyan-500/25"
              >
                Create Account
              </Button>

              <motion.div className="text-sm text-white/70 text-center">
                Already have an account?{" "}
                <Link href="/login" className="font-semibold text-violet-400 hover:text-violet-300 transition-colors">
                  Sign in
                </Link>
              </motion.div>
            </form>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
