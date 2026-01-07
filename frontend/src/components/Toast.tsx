"use client";

import { AnimatePresence, motion } from "framer-motion";

export function Toast({ message, kind }: { message: string; kind: "error" | "success" }) {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className={[
          "fixed left-1/2 top-6 z-50 -translate-x-1/2 rounded-md px-4 py-2 text-sm shadow-lg",
          kind === "error" ? "bg-fuchsia-600 text-white" : "bg-cyan-300 text-black",
        ].join(" ")}
      >
        {message}
      </motion.div>
    </AnimatePresence>
  );
}
