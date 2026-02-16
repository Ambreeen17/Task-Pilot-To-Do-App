import type { ReactNode } from "react";

type Props = { title?: string; children: ReactNode; className?: string };

export function Card({ title, children, className = "" }: Props) {
  return (
    <div className={`w-full rounded-xl border border-white/10 bg-white/5 p-6 shadow-lg backdrop-blur ${className}`}>
      {title ? <h1 className="mb-4 text-xl font-semibold text-white">{title}</h1> : null}
      {children}
    </div>
  );
}
