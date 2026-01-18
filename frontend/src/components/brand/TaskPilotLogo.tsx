'use client';

import { motion } from 'framer-motion';

interface TaskPilotLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  animate?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { icon: 24, text: 'text-lg', gap: 'gap-1.5' },
  md: { icon: 32, text: 'text-xl', gap: 'gap-2' },
  lg: { icon: 48, text: 'text-3xl', gap: 'gap-3' },
  xl: { icon: 64, text: 'text-5xl', gap: 'gap-4' },
};

export function TaskPilotLogo({
  size = 'md',
  showText = true,
  animate = true,
  className = ''
}: TaskPilotLogoProps) {
  const config = sizeConfig[size];

  const IconComponent = (
    <svg
      width={config.icon}
      height={config.icon}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0"
    >
      <circle cx="32" cy="32" r="28" stroke="url(#gradient1)" strokeWidth="2" fill="none" />
      <circle cx="32" cy="32" r="22" stroke="url(#gradient2)" strokeWidth="1.5" fill="none" opacity="0.6" />
      <path d="M32 12L38 32L32 52L26 32L32 12Z" fill="url(#gradient3)" />
      <circle cx="32" cy="32" r="4" fill="#06b6d4" />
      <path d="M32 8L32 4" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
      <path d="M32 60L32 56" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
      <path d="M8 32L4 32" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
      <path d="M60 32L56 32" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#06b6d4" />
        </linearGradient>
        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
        <linearGradient id="gradient3" x1="32" y1="12" x2="32" y2="52">
          <stop offset="0%" stopColor="#8b5cf6" />
          <stop offset="50%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
    </svg>
  );

  return (
    <div className={`flex items-center ${config.gap} ${className}`}>
      {animate ? (
        <motion.div
          initial={{ rotate: -180, opacity: 0, scale: 0.5 }}
          animate={{ rotate: 0, opacity: 1, scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20, duration: 0.8 }}
        >
          {IconComponent}
        </motion.div>
      ) : (
        IconComponent
      )}

      {showText && (
        animate ? (
          <motion.span
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className={`font-bold ${config.text} bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent`}
          >
            TaskPilot
          </motion.span>
        ) : (
          <span className={`font-bold ${config.text} bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent`}>
            TaskPilot
          </span>
        )
      )}
    </div>
  );
}

export default TaskPilotLogo;
