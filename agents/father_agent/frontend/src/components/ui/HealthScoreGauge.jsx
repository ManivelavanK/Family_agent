import React from 'react';
import { motion } from 'framer-motion';

export const HealthScoreGauge = ({ score = 80, status = 'Healthy', size = 180 }) => {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 100);
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const getColor = (s) => {
    if (s >= 85) return { stroke: '#2F855A', text: 'text-emerald-700', bg: 'rgba(47, 133, 90, 0.15)' };
    if (s >= 70) return { stroke: '#0F766E', text: 'text-teal-700', bg: 'rgba(15, 118, 110, 0.15)' };
    if (s >= 55) return { stroke: '#D4A72C', text: 'text-amber-600', bg: 'rgba(212, 167, 44, 0.15)' };
    return { stroke: '#C53030', text: 'text-rose-700', bg: 'rgba(197, 48, 48, 0.15)' };
  };

  const theme = getColor(score);

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(16, 42, 67, 0.08)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress bar */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={theme.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          strokeLinecap="round"
          fill="transparent"
        />
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <motion.span
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-4xl font-extrabold text-[#102A43] tracking-tight"
        >
          {score}
        </motion.span>
        <span className={`text-xs font-semibold uppercase tracking-wider mt-0.5 ${theme.text}`}>
          {status}
        </span>
      </div>
    </div>
  );
};

export default HealthScoreGauge;
