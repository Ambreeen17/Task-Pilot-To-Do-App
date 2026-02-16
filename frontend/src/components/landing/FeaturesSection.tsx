'use client';

import { motion } from 'framer-motion';
import { Sparkles, Brain, Zap, Shield } from 'lucide-react';

const features = [
  {
    icon: Sparkles,
    title: 'Smart Task Creation',
    description: 'Natural language processing understands your intent and creates structured tasks automatically.',
    gradient: 'from-violet-500 to-purple-500'
  },
  {
    icon: Brain,
    title: 'AI Assistance',
    description: 'Get intelligent suggestions for task prioritization, deadlines, and optimal scheduling.',
    gradient: 'from-cyan-500 to-blue-500'
  },
  {
    icon: Zap,
    title: 'Autonomous Suggestions',
    description: 'TaskPilot learns your patterns and proactively suggests improvements to your workflow.',
    gradient: 'from-amber-500 to-orange-500'
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your data stays yours. Privacy-first design with GDPR compliance and local-first processing.',
    gradient: 'from-emerald-500 to-green-500'
  }
];

export function FeaturesSection() {
  return (
    <section className="relative bg-slate-900 py-24">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-violet-600/5 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
            Powerful Features for{' '}
            <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Modern Productivity
            </span>
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-white/60">
            Everything you need to manage tasks efficiently, powered by cutting-edge AI technology.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ y: 40, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -8 }}
              className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition-colors hover:border-white/20 hover:bg-white/10"
            >
              <div className={`absolute -inset-px rounded-2xl bg-gradient-to-r ${feature.gradient} opacity-0 blur-xl transition-opacity group-hover:opacity-20`} />
              <div className="relative">
                <div className={`mb-4 inline-flex rounded-xl bg-gradient-to-r ${feature.gradient} p-3`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-white">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-white/60">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;
