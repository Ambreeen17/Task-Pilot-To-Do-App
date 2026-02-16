'use client';

import { motion } from 'framer-motion';

interface TaskPilotLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  animate?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { icon: 28, text: 'text-xl', gap: 'gap-2' },
  md: { icon: 36, text: 'text-2xl', gap: 'gap-2.5' },
  lg: { icon: 52, text: 'text-4xl', gap: 'gap-3' },
  xl: { icon: 72, text: 'text-6xl', gap: 'gap-4' },
};

export function TaskPilotLogo({
  size = 'md',
  showText = true,
  animate = true,
  className = ''
}: TaskPilotLogoProps) {
  const config = sizeConfig[size];

  return (
    <div className={`flex items-center ${config.gap} ${className}`}>
      {/* Animated Icon */}
      <motion.div
        initial={animate ? { rotate: -180, scale: 0 } : false}
        animate={{ rotate: 0, scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15, duration: 0.8 }}
        className="relative"
      >
        <svg
          width={config.icon}
          height={config.icon}
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="flex-shrink-0"
        >
          {/* Outer rotating ring */}
          <motion.circle
            cx="32"
            cy="32"
            r="28"
            stroke="url(#logoGradient1)"
            strokeWidth="2"
            fill="none"
            initial={animate ? { pathLength: 0 } : { pathLength: 1 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
          />
          
          {/* Inner pulsing ring */}
          <motion.circle
            cx="32"
            cy="32"
            r="22"
            stroke="url(#logoGradient2)"
            strokeWidth="1.5"
            fill="none"
            initial={{ opacity: 0.3 }}
            animate={{ opacity: [0.3, 0.7, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          
          {/* Compass needle - animated */}
          <motion.path
            d="M32 10L40 32L32 54L24 32L32 10Z"
            fill="url(#logoGradient3)"
            initial={animate ? { scale: 0, opacity: 0 } : false}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          />
          
          {/* Center dot - pulsing */}
          <motion.circle
            cx="32"
            cy="32"
            r="5"
            fill="#06b6d4"
            animate={{ 
              scale: [1, 1.2, 1],
              boxShadow: ['0 0 0 0 rgba(6, 182, 212, 0.4)', '0 0 0 10px rgba(6, 182, 212, 0)', '0 0 0 0 rgba(6, 182, 212, 0.4)']
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          
          {/* Cardinal points - staggered animation */}
          <motion.g
            initial={animate ? { opacity: 0 } : { opacity: 1 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            <motion.path d="M32 6L32 2" stroke="#8b5cf6" strokeWidth="2.5" strokeLinecap="round"
              animate={{ y: [0, -2, 0] }} transition={{ duration: 1.5, repeat: Infinity, delay: 0 }} />
            <motion.path d="M32 62L32 58" stroke="#8b5cf6" strokeWidth="2.5" strokeLinecap="round"
              animate={{ y: [0, 2, 0] }} transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }} />
            <motion.path d="M6 32L2 32" stroke="#06b6d4" strokeWidth="2.5" strokeLinecap="round"
              animate={{ x: [0, -2, 0] }} transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }} />
            <motion.path d="M62 32L58 32" stroke="#06b6d4" strokeWidth="2.5" strokeLinecap="round"
              animate={{ x: [0, 2, 0] }} transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }} />
          </motion.g>
          
          {/* Gradients */}
          <defs>
            <linearGradient id="logoGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
            <linearGradient id="logoGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
            <linearGradient id="logoGradient3" x1="32" y1="10" x2="32" y2="54">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="50%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>
        </svg>
      </motion.div>

      {/* Animated Text */}
      {showText && (
        <motion.div
          initial={animate ? { opacity: 0, x: -20 } : false}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="flex flex-col"
        >
          <motion.span
            className={`font-bold ${config.text} bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto]`}
            animate={{ backgroundPosition: ['0% center', '200% center'] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          >
            TaskPilot
          </motion.span>
          {size !== 'sm' && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              transition={{ delay: 0.8 }}
              className="text-xs text-white/60 tracking-wider"
            >
              Navigate Smarter
            </motion.span>
          )}
        </motion.div>
      )}
    </div>
  );
}

export default TaskPilotLogo;
