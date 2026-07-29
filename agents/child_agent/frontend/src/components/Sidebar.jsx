import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, BookOpen, CalendarDays, FileText, Target,
  BarChart3, Award, Sparkles, MessageCircle, Timer,
  Map, User, Bell, ChevronLeft, ChevronRight, Menu, X, Brain,
} from 'lucide-react';

const NAV = [
  { to: '/',              label: 'Dashboard',    icon: LayoutDashboard, group: 'main' },
  { to: '/study-hub',     label: 'Study Hub',    icon: BookOpen,        group: 'main' },
  { to: '/ai-planner',    label: 'AI Planner',   icon: CalendarDays,    group: 'ai'   },
  { to: '/assignments',   label: 'Assignments',  icon: FileText,        group: 'main' },
  { to: '/goals',         label: 'Goals',        icon: Target,          group: 'main' },
  { to: '/exams',         label: 'Exams',        icon: Award,           group: 'main' },
  { to: '/progress',      label: 'Progress',     icon: BarChart3,       group: 'main' },
  { to: '/ai-tutor',      label: 'AI Tutor',     icon: Sparkles,        group: 'ai'   },
  { to: '/ai-companion',  label: 'AI Companion', icon: Brain,           group: 'ai'   },
  { to: '/focus-habits',  label: 'Focus & Habits',icon: Timer,          group: 'main' },
  { to: '/learning-path', label: 'Learning Path',icon: Map,             group: 'main' },
  { to: '/profile',       label: 'Profile',      icon: User,            group: 'account'},
  { to: '/notifications', label: 'Notifications',icon: Bell,            group: 'account'},
];

const GROUP_LABELS = { main: 'WORKSPACE', ai: 'AI INTELLIGENCE', account: 'ACCOUNT' };

function NavItem({ item, collapsed }) {
  const Icon = item.icon;
  const isAI = item.group === 'ai';

  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      className={({ isActive }) =>
        `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 relative
         ${isActive
           ? isAI
             ? 'bg-gradient-to-r from-brand-indigo/20 to-brand-purple/15 text-white border border-indigo-500/20'
             : 'bg-white/10 text-white border border-white/10'
           : 'text-slate-400 hover:text-white hover:bg-white/6'
         }`
      }
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <motion.div
              layoutId="active-pill"
              className={`absolute inset-0 rounded-xl ${isAI ? 'gradient-indigo-purple opacity-20' : 'bg-white/8'}`}
              transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
            />
          )}
          <Icon
            size={18}
            className={`shrink-0 transition-all ${isActive ? (isAI ? 'text-indigo-400' : 'text-white') : 'text-slate-500 group-hover:text-indigo-400'}`}
          />
          {!collapsed && (
            <span className="truncate relative z-10">{item.label}</span>
          )}
          {isActive && !collapsed && isAI && (
            <span className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0 animate-pulse-soft" />
          )}
        </>
      )}
    </NavLink>
  );
}

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen]  = useState(false);

  const groups = ['main', 'ai', 'account'];

  const SidebarContent = ({ onClose }) => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-white/8">
        <AnimatePresence mode="wait">
          {!collapsed ? (
            <motion.div
              key="expanded"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x:  0  }}
              exit  ={{ opacity: 0, x: -10 }}
              className="flex items-center gap-3"
            >
              <div className="w-9 h-9 rounded-xl gradient-indigo-purple flex items-center justify-center text-white font-black text-base shadow-glow shrink-0">
                K
              </div>
              <div>
                <div className="font-extrabold text-white leading-none text-[15px]">KinNest</div>
                <div className="text-[11px] text-indigo-400 font-medium mt-0.5">Academic Companion</div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="collapsed"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1   }}
              exit  ={{ opacity: 0, scale: 0.8  }}
              className="w-9 h-9 rounded-xl gradient-indigo-purple flex items-center justify-center text-white font-black text-base shadow-glow mx-auto"
            >
              K
            </motion.div>
          )}
        </AnimatePresence>

        {onClose ? (
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
            <X size={18} />
          </button>
        ) : (
          <button
            onClick={() => setCollapsed(c => !c)}
            className="text-slate-500 hover:text-white p-1.5 rounded-lg hover:bg-white/8 transition-colors"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {groups.map(group => {
          const items = NAV.filter(n => n.group === group);
          return (
            <div key={group}>
              {!collapsed && (
                <div className="text-[10px] font-bold tracking-widest text-slate-600 px-3 mb-2 uppercase">
                  {GROUP_LABELS[group]}
                </div>
              )}
              <div className="space-y-0.5">
                {items.map(item => (
                  <NavItem key={item.to} item={item} collapsed={collapsed} />
                ))}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Footer badge */}
      {!collapsed && (
        <div className="px-4 py-4 border-t border-white/8">
          <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/15">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold text-indigo-300">AI Systems Online</span>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* ── Desktop Sidebar ──────────────────────────── */}
      <motion.aside
        animate={{ width: collapsed ? 72 : 260 }}
        transition={{ type: 'spring', damping: 22, stiffness: 220 }}
        className="hidden lg:flex flex-col fixed top-0 left-0 h-screen bg-navy-dark border-r border-white/6 z-30 overflow-hidden"
      >
        <SidebarContent />
      </motion.aside>

      {/* ── Mobile Top Bar ───────────────────────────── */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-navy-dark border-b border-white/8 z-40 flex items-center justify-between px-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg gradient-indigo-purple flex items-center justify-center text-white font-black text-sm">K</div>
          <span className="font-bold text-white text-sm">KinNest</span>
        </div>
        <button onClick={() => setMobileOpen(true)} className="text-slate-400 hover:text-white p-2">
          <Menu size={22} />
        </button>
      </div>

      {/* ── Mobile Drawer ────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
            />
            <motion.aside
              initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.25 }}
              className="lg:hidden fixed top-0 left-0 bottom-0 w-64 bg-navy-dark z-50 border-r border-white/8"
            >
              <SidebarContent onClose={() => setMobileOpen(false)} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
