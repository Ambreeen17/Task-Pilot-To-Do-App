"use client";

import { motion } from "framer-motion";
import { useTheme } from "@/context/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-xl transition-all hover:border-purple-500/50 hover:bg-white/10"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <div className="flex items-center gap-2">
        <motion.div
          initial={false}
          animate={{
            rotate: isDark ? 180 : 0,
            scale: [1, 1.2, 1],
          }}
          transition={{
            rotate: { duration: 0.5, ease: "easeInOut" },
            scale: { duration: 0.3, repeat: Infinity, repeatDelay: 2 },
          }}
          className="relative h-5 w-5"
        >
          {isDark ? (
            // Moon Icon
            <svg
              className="h-5 w-5 text-yellow-300"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          ) : (
            // Sun Icon
            <svg
              className="h-5 w-5 text-orange-400"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </motion.div>
        <span className="text-sm font-medium text-white/90">
          {theme === "dark" ? "Dark" : "Light"}
        </span>
      </div>

      {/* Animated background glow */}
      <motion.div
        className="absolute inset-0 opacity-0"
        animate={{
          opacity: [0, 0.3, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{
          background: isDark
            ? "radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%)"
            : "radial-gradient(circle, rgba(251, 146, 60, 0.3) 0%, transparent 70%)",
        }}
      />
    </motion.button>
  );
}
