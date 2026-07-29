import React from 'react';
import { motion } from 'framer-motion';

export const GlassCard = ({ children, className = '', glow = false, onClick, hover = true, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={hover ? { y: -4, scale: 1.01 } : {}}
      onClick={onClick}
      className={`rounded-2xl p-6 relative overflow-hidden transition-all duration-300 ${
        glow ? 'glass-panel-glow' : 'glass-panel'
      } ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {/* Decorative top right subtle gradient accent */}
      <div className="absolute -top-12 -right-12 w-28 h-28 bg-blue-500/10 rounded-full blur-xl pointer-events-none" />
      {children}
    </motion.div>
  );
};

export default GlassCard;
