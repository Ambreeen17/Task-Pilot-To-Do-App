'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Github, Heart } from 'lucide-react';
import { TaskPilotLogo } from '../brand/TaskPilotLogo';

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-slate-950 py-12">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-center gap-8 md:flex-row md:justify-between">
          {/* Logo and description */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center md:text-left"
          >
            <TaskPilotLogo size="sm" animate={false} className="mb-3 justify-center md:justify-start" />
            <p className="max-w-xs text-sm text-white/50">
              An AI-Powered Task Copilot. Smart, autonomous, and privacy-first task management.
            </p>
          </motion.div>

          {/* Links */}
          <div className="flex flex-wrap items-center justify-center gap-6">
            <Link
              href="/login"
              className="text-sm text-white/60 transition-colors hover:text-white"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="text-sm text-white/60 transition-colors hover:text-white"
            >
              Get Started
            </Link>
            <a
              href="https://github.com/Ambreeen17/TO-DO-APP-PHASE1"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-white/60 transition-colors hover:text-white"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </div>
        </div>

        {/* Divider */}
        <div className="my-8 h-px bg-white/10" />

        {/* Bottom row */}
        <div className="flex flex-col items-center gap-4 text-center text-xs text-white/40 md:flex-row md:justify-between">
          <p>
            &copy; {new Date().getFullYear()} TaskPilot. Built with{' '}
            <Heart className="inline h-3 w-3 text-red-400" /> as a spec-driven AI-native project.
          </p>
          <p className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
            Phase 1-5 Implementation Complete
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
