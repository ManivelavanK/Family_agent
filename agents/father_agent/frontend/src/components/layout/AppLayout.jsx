import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { motion, AnimatePresence } from 'framer-motion';

export const AppLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col relative overflow-x-hidden">
      {/* Ambient background particles and grid overlay */}
      <div className="ambient-bg">
        <div className="grid-pattern" />
        <div className="ambient-orb-1" />
        <div className="ambient-orb-2" />
        <div className="ambient-orb-3" />
      </div>

      {/* Sidebar Navigation */}
      <Sidebar
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Top Header */}
      <TopNav isCollapsed={isCollapsed} setIsMobileOpen={setIsMobileOpen} />

      {/* Main Workspace with Page Transitions */}
      <main
        className={`flex-1 transition-all duration-300 relative z-10 px-4 sm:px-6 lg:px-8 py-8 ${
          isCollapsed ? 'lg:ml-20' : 'lg:ml-64'
        }`}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
            className="max-w-7xl mx-auto"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};

export default AppLayout;
