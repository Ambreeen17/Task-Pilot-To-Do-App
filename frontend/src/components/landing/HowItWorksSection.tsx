'use client';

import { motion } from 'framer-motion';
import { PenLine, Cpu, Rocket } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: PenLine,
    title: 'Create Tasks',
    description: 'Add tasks using natural language or traditional input. TaskPilot understands your intent.',
    color: 'violet'
  },
  {
    number: '02',
    icon: Cpu,
    title: 'AI Assists',
    description: 'Our AI analyzes your tasks, suggests priorities, and identifies patterns in your workflow.',
    color: 'cyan'
  },
  {
    number: '03',
    icon: Rocket,
    title: 'TaskPilot Optimizes',
    description: 'Get proactive suggestions, deadline alerts, and autonomous optimizations to boost productivity.',
    color: 'violet'
  }
];

export function HowItWorksSection() {
  return (
    <section className="relative bg-slate-950 py-24">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 h-64 w-64 rounded-full bg-cyan-600/10 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-64 w-64 rounded-full bg-violet-600/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        {/* Section header */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
            How{' '}
            <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
              TaskPilot
            </span>{' '}
            Works
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-white/60">
            Three simple steps to transform your productivity
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connection line */}
          <div className="absolute left-1/2 top-0 hidden h-full w-px -translate-x-1/2 bg-gradient-to-b from-violet-500/50 via-cyan-500/50 to-violet-500/50 lg:block" />

          <div className="space-y-12 lg:space-y-24">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ x: index % 2 === 0 ? -50 : 50, opacity: 0 }}
                whileInView={{ x: 0, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                className={`flex flex-col items-center gap-8 lg:flex-row ${
                  index % 2 === 1 ? 'lg:flex-row-reverse' : ''
                }`}
              >
                {/* Content */}
                <div className={`flex-1 text-center ${index % 2 === 0 ? 'lg:text-right' : 'lg:text-left'}`}>
                  <span className={`mb-2 inline-block text-sm font-bold ${
                    step.color === 'cyan' ? 'text-cyan-400' : 'text-violet-400'
                  }`}>
                    STEP {step.number}
                  </span>
                  <h3 className="mb-3 text-2xl font-bold text-white">{step.title}</h3>
                  <p className="text-white/60">{step.description}</p>
                </div>

                {/* Icon circle */}
                <div className="relative z-10 flex h-20 w-20 items-center justify-center rounded-full border-2 border-white/20 bg-slate-900">
                  <div className={`absolute inset-2 rounded-full bg-gradient-to-br ${
                    step.color === 'cyan' ? 'from-cyan-500 to-blue-600' : 'from-violet-500 to-purple-600'
                  }`} />
                  <step.icon className="relative z-10 h-8 w-8 text-white" />
                </div>

                {/* Spacer for alignment */}
                <div className="hidden flex-1 lg:block" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export default HowItWorksSection;
