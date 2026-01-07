"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

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
    <div className="min-h-screen bg-[#0a0a0f] px-6 py-16 text-white">
      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <div className="mx-auto flex max-w-md flex-col items-center gap-6">
        <div className="text-2xl font-semibold tracking-tight">2do</div>
        <Card title="Sign in">
          <form className="flex flex-col gap-4" onSubmit={onSubmit}>
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={emailError}
              placeholder="you@example.com"
              autoComplete="email"
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={passwordError}
              placeholder="••••••••"
              autoComplete="current-password"
            />

            <Button type="submit" loading={submitting} disabled={!canSubmit}>
              Sign In
            </Button>

            <button
              type="button"
              className="text-sm text-white/70 hover:text-white"
              onClick={() => router.push("/signup")}
            >
              New here? Create account
            </button>
          </form>
        </Card>
      </div>
    </div>
  );
}
