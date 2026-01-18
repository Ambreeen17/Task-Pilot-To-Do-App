'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, CheckCircle } from 'lucide-react';

const benefits = [
  'Free to get started',
  'No credit card required',
  'AI features included',
  'Privacy-first design'
];

export function CTASection() {
  return (
    <section className="relative bg-slate-900 py-24">
      {/* Background gradient */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-violet-900/20 to-transparent" />
      </div>

      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-6 text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
            Ready to{' '}
            <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Navigate Smarter
            </span>
            ?
          </h2>
          <p className="mb-8 text-lg text-white/60">
            Join TaskPilot today and experience the future of intelligent task management.
          </p>

          {/* Benefits */}
          <div className="mb-10 flex flex-wrap items-center justify-center gap-4">
            {benefits.map((benefit, index) => (
              <motion.div
                key={benefit}
                initial={{ scale: 0.8, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-2 text-sm text-white/70"
              >
                <CheckCircle className="h-4 w-4 text-cyan-400" />
                {benefit}
              </motion.div>
            ))}
          </div>

          {/* CTA Button */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Link
              href="/signup"
              className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 px-10 py-5 text-xl font-bold text-white shadow-2xl shadow-violet-500/30 transition-all hover:from-violet-500 hover:to-cyan-500 hover:shadow-violet-500/50"
            >
              Start Using TaskPilot
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

export default CTASection;
