'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Play } from 'lucide-react';
import { TaskPilotLogo } from '../brand/TaskPilotLogo';

export function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-slate-900 pt-24">
      {/* Background gradient effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-violet-600/20 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-cyan-600/20 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-64 w-64 rounded-full bg-violet-500/10 blur-3xl" />
      </div>

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />

      <div className="relative mx-auto max-w-7xl px-6 py-20 lg:py-32">
        <div className="flex flex-col items-center text-center">
          {/* Animated Logo */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="mb-8"
          >
            <TaskPilotLogo size="xl" showText={false} animate={true} />
          </motion.div>

          {/* Main headline */}
          <motion.h1
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mb-4 text-5xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl"
          >
            <span className="bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
              TaskPilot
            </span>
          </motion.h1>

          {/* Tagline */}
          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="mb-4 text-xl font-medium text-cyan-400"
          >
            Your Smart Copilot for Tasks
          </motion.p>

          {/* Subtitle */}
          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mb-10 max-w-2xl text-lg text-white/60"
          >
            AI-powered autonomous task management that learns your habits,
            suggests optimizations, and helps you stay productive. Navigate your tasks smarter.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="flex flex-col gap-4 sm:flex-row"
          >
            <Link
              href="/signup"
              className="group flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:from-violet-500 hover:to-cyan-500 hover:shadow-2xl hover:shadow-violet-500/30"
            >
              Get Started Free
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/login"
              className="group flex items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/5 px-8 py-4 text-lg font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/10 hover:border-white/30"
            >
              <Play className="h-5 w-5" />
              View Demo
            </Link>
          </motion.div>

          {/* Stats or trust indicators */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="mt-16 flex flex-wrap items-center justify-center gap-8 text-white/40"
          >
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm">AI-Powered</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-cyan-500" />
              <span className="text-sm">Privacy-First</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-violet-500" />
              <span className="text-sm">Adaptive Learning</span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-900 to-transparent" />
    </section>
  );
}

export default HeroSection;
