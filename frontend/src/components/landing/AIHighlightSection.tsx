'use client';

import { motion } from 'framer-motion';
import { Bot, Lightbulb, TrendingUp, Clock } from 'lucide-react';

const highlights = [
  { icon: Bot, label: 'Autonomous Actions' },
  { icon: Lightbulb, label: 'Smart Suggestions' },
  { icon: TrendingUp, label: 'Pattern Learning' },
  { icon: Clock, label: 'Time Optimization' }
];

export function AIHighlightSection() {
  return (
    <section className="relative overflow-hidden py-24">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-900/50 via-slate-900 to-cyan-900/50" />

      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear'
          }}
          className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-violet-600/20 blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'linear'
          }}
          className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-cyan-600/20 blur-3xl"
        />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          {/* Content */}
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            whileInView={{ x: 0, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <span className="mb-4 inline-block rounded-full bg-violet-500/20 px-4 py-1.5 text-sm font-medium text-violet-300">
              Powered by AI
            </span>
            <h2 className="mb-6 text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Intelligence That{' '}
              <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                Adapts to You
              </span>
            </h2>
            <p className="mb-8 text-lg text-white/60">
              TaskPilot&apos;s adaptive AI learns from your behavior patterns, understands your productivity peaks,
              and continuously optimizes your task management experience. All while keeping your data private and secure.
            </p>

            {/* Highlight badges */}
            <div className="flex flex-wrap gap-3">
              {highlights.map((item, index) => (
                <motion.div
                  key={item.label}
                  initial={{ scale: 0.8, opacity: 0 }}
                  whileInView={{ scale: 1, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1, duration: 0.4 }}
                  className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-sm"
                >
                  <item.icon className="h-4 w-4 text-cyan-400" />
                  <span className="text-sm text-white/80">{item.label}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Visual element */}
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            whileInView={{ x: 0, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="relative mx-auto aspect-square max-w-md">
              {/* Outer ring */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0 rounded-full border-2 border-dashed border-violet-500/30"
              />

              {/* Middle ring */}
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-8 rounded-full border-2 border-dashed border-cyan-500/30"
              />

              {/* Inner circle with content */}
              <div className="absolute inset-16 flex items-center justify-center rounded-full border border-white/20 bg-slate-900/80 backdrop-blur-xl">
                <div className="text-center">
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="mb-2 text-4xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent"
                  >
                    AI
                  </motion.div>
                  <div className="text-sm text-white/60">Autonomous</div>
                  <div className="text-sm text-white/60">Intelligence</div>
                </div>
              </div>

              {/* Floating icons */}
              {[
                { Icon: Bot, position: 'top-0 left-1/2 -translate-x-1/2', delay: 0 },
                { Icon: Lightbulb, position: 'right-0 top-1/2 -translate-y-1/2', delay: 0.5 },
                { Icon: TrendingUp, position: 'bottom-0 left-1/2 -translate-x-1/2', delay: 1 },
                { Icon: Clock, position: 'left-0 top-1/2 -translate-y-1/2', delay: 1.5 }
              ].map(({ Icon, position, delay }) => (
                <motion.div
                  key={position}
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay, type: 'spring' }}
                  className={`absolute ${position} flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 border border-white/20`}
                >
                  <Icon className="h-5 w-5 text-cyan-400" />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

export default AIHighlightSection;
