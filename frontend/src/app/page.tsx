import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] px-6 py-16 text-white">
      <div className="mx-auto flex max-w-md flex-col gap-4 rounded-xl border border-white/10 bg-white/5 p-6">
        <div className="text-2xl font-semibold tracking-tight">2do</div>
        <p className="text-white/70">Welcome. Sign in to manage your tasks.</p>
        <div className="flex gap-2">
          <Link className="rounded-md bg-cyan-400 px-4 py-2 text-sm font-medium text-black" href="/login">
            Sign in
          </Link>
          <Link className="rounded-md bg-fuchsia-500 px-4 py-2 text-sm font-medium text-white" href="/signup">
            Create account
          </Link>
        </div>
      </div>
    </div>
  );
}
