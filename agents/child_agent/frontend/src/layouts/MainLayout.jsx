import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0  },
  exit:    { opacity: 0, y: -8 },
};

const pageTransition = {
  type: 'tween',
  ease: [0.25, 0.46, 0.45, 0.94],
  duration: 0.28,
};

export default function MainLayout() {
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />

      {/* Main content — offset by sidebar width on desktop */}
      <main className="flex-1 lg:pl-[260px] pt-14 lg:pt-0 min-w-0">
        <div className="max-w-[1400px] mx-auto px-4 md:px-6 lg:px-8 py-6 lg:py-8">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={pageTransition}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
