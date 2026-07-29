import React from 'react';
import { motion } from 'framer-motion';

const STATE_CONFIG = {
  idle: {
    gradient: 'from-indigo-500 via-violet-500 to-purple-600',
    glow: 'rgba(99,102,241,0.5)',
    animate: { y: [0, -10, 0], scale: [1, 1.04, 1] },
    transition: { duration: 4, repeat: Infinity, ease: 'easeInOut' },
    label: 'Ready',
  },
  thinking: {
    gradient: 'from-violet-500 via-purple-600 to-fuchsia-700',
    glow: 'rgba(124,58,237,0.6)',
    animate: { rotate: [0, 360], scale: [1, 1.12, 1, 1.08, 1] },
    transition: { rotate: { duration: 2, repeat: Infinity, ease: 'linear' }, scale: { duration: 1.2, repeat: Infinity } },
    label: 'Thinking…',
  },
  responding: {
    gradient: 'from-emerald-400 via-teal-500 to-indigo-500',
    glow: 'rgba(52,211,153,0.5)',
    animate: { scale: [1, 1.08, 1.02, 1.08, 1] },
    transition: { duration: 1.8, repeat: Infinity, ease: 'easeInOut' },
    label: 'Responding',
  },
  error: {
    gradient: 'from-amber-400 via-orange-500 to-red-500',
    glow: 'rgba(245,158,11,0.5)',
    animate: { x: [-4, 4, -4, 4, 0], scale: [1, 1, 1] },
    transition: { duration: 0.5, repeat: 2 },
    label: 'Error',
  },
};

export default function AIOrb({ status = 'idle', size = 'md' }) {
  const cfg = STATE_CONFIG[status] ?? STATE_CONFIG.idle;

  const sizes = {
    sm:  { outer: 'w-12 h-12', inner: 'w-8 h-8',  glare: 'w-2.5 h-2.5' },
    md:  { outer: 'w-24 h-24', inner: 'w-16 h-16', glare: 'w-4  h-4'   },
    lg:  { outer: 'w-32 h-32', inner: 'w-22 h-22', glare: 'w-5  h-5'   },
  };
  const s = sizes[size] ?? sizes.md;

  return (
    <div className={`relative flex items-center justify-center ${s.outer}`}>
      {/* Ambient glow */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{ background: cfg.glow, filter: 'blur(18px)', opacity: 0.6 }}
        animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0.7, 0.4] }}
        transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Main orb */}
      <motion.div
        animate={cfg.animate}
        transition={cfg.transition}
        className={`${s.inner} rounded-full bg-gradient-to-br ${cfg.gradient} relative border border-white/20`}
        style={{ boxShadow: `0 0 24px ${cfg.glow}, inset 0 0 20px rgba(255,255,255,0.1)` }}
      >
        {/* Glare */}
        <div className={`absolute top-1.5 left-1.5 ${s.glare} rounded-full bg-white/50 blur-[1px]`} />
        {/* Inner ring */}
        <div className="absolute inset-2 rounded-full border border-white/15" />
      </motion.div>
    </div>
  );
}
