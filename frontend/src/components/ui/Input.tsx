import type { InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string | null;
};

export function Input({ label, error, className, ...rest }: Props) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-white/80">{label}</span>
      <input
        className={[
          "rounded-md border bg-white/5 px-3 py-2 text-white placeholder:text-white/40",
          "border-white/10 focus:border-cyan-400/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20",
          error ? "border-fuchsia-500/70" : "",
          className,
        ]
          .filter(Boolean)
          .join(" ")}
        {...rest}
      />
      {error ? <span className="text-xs text-fuchsia-400">{error}</span> : null}
    </label>
  );
}
