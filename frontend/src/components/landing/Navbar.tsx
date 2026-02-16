'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { TaskPilotLogo } from '../brand/TaskPilotLogo';

export function Navbar() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-900/80 backdrop-blur-xl"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center">
          <TaskPilotLogo size="sm" animate={false} />
        </Link>

        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="rounded-lg px-4 py-2 text-sm font-medium text-white/80 transition-colors hover:text-white"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 px-4 py-2 text-sm font-medium text-white transition-all hover:from-violet-500 hover:to-cyan-500 hover:shadow-lg hover:shadow-violet-500/25"
          >
            Get Started
          </Link>
        </div>
      </div>
    </motion.nav>
  );
}

export default Navbar;
