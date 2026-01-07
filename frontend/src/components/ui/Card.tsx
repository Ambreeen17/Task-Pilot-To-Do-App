import type { ReactNode } from "react";

type Props = { title?: string; children: ReactNode };

export function Card({ title, children }: Props) {
  return (
    <div className="w-full max-w-md rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg backdrop-blur">
      {title ? <h1 className="mb-4 text-xl font-semibold text-white">{title}</h1> : null}
      {children}
    </div>
  );
}
