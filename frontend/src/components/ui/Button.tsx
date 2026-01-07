import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
  loading?: boolean;
};

export function Button({ variant = "primary", loading, className, disabled, children, ...rest }: Props) {
  const base =
    "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400/60 disabled:opacity-50 disabled:cursor-not-allowed";

  const variants: Record<string, string> = {
    primary: "bg-cyan-400 text-black hover:bg-cyan-300",
    secondary: "bg-fuchsia-500 text-white hover:bg-fuchsia-400",
    ghost: "bg-transparent text-white hover:bg-white/10",
  };

  return (
    <button
      className={[base, variants[variant], className].filter(Boolean).join(" ")}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? "Loading…" : children}
    </button>
  );
}
