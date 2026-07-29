import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Receipt,
  TrendingUp,
  PieChart,
  Target,
  FileText,
  Bot,
  Sparkles,
  AlertTriangle,
  ShieldCheck,
  Brain,
  Cpu,
  BarChart3,
  Users,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

const navigationGroups = [
  {
    title: 'OVERVIEW',
    items: [
      { name: 'Overview', path: '/', icon: LayoutDashboard }
    ]
  },
  {
    title: 'MONEY',
    items: [
      { name: 'Expenses', path: '/expenses', icon: Receipt },
      { name: 'Income', path: '/income', icon: TrendingUp },
      { name: 'Budget', path: '/budget', icon: PieChart }
    ]
  },
  {
    title: 'PLANNING',
    items: [
      { name: 'Savings Goals', path: '/savings', icon: Target },
      { name: 'Bills', path: '/bills', icon: FileText }
    ]
  },
  {
    title: 'AI INTELLIGENCE',
    items: [
      { name: 'AI Advisor', path: '/ai-advisor', icon: Bot, badge: 'AI' },
      { name: 'Decision Center', path: '/decision-center', icon: Cpu, badge: 'New' },
      { name: 'Ask Before Spend', path: '/ask-before-spend', icon: ShieldCheck, badge: 'New' },
      { name: 'Predictions', path: '/predictions', icon: Sparkles },
      { name: 'Anomalies', path: '/anomalies', icon: AlertTriangle },
      { name: 'Safe to Spend', path: '/safe-to-spend', icon: ShieldCheck },
      { name: 'Early Warnings', path: '/early-warnings', icon: ShieldAlert },
      { name: 'Financial Memory', path: '/memory', icon: Brain }
    ]
  },
  {
    title: 'SIMULATION',
    items: [
      { name: 'Digital Twin', path: '/digital-twin', icon: Cpu, badge: 'Sim' }
    ]
  },
  {
    title: 'ANALYTICS',
    items: [
      { name: 'Spending Analytics', path: '/analytics', icon: BarChart3 }
    ]
  },
  {
    title: 'FAMILY',
    items: [
      { name: 'Family Intelligence', path: '/family-intelligence', icon: Users },
      { name: 'Notifications', path: '/notifications', icon: Bell },
      { name: 'Settings', path: '/settings', icon: Settings }
    ]
  },
  {
    title: 'ADMIN',
    items: [
      { name: 'AI Verification', path: '/ai-verification', icon: Cpu, badge: 'Dev' }
    ]
  }
];

export const Sidebar = ({ isCollapsed, setIsCollapsed, isMobileOpen, setIsMobileOpen }) => {
  return (
    <>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileOpen(false)}
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      <motion.aside
        className={`fixed top-0 left-0 bottom-0 z-50 flex flex-col bg-[#102A43] border-r border-[#243B53] transition-all duration-300 ${
          isCollapsed ? 'w-20' : 'w-64'
        } ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[#243B53]">
          <NavLink to="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#0F766E] to-[#D4A72C] flex items-center justify-center text-white shadow-lg shadow-emerald-950/25 shrink-0">
              <Sparkles className="w-5 h-5 animate-pulse text-[#F7F9FC]" />
            </div>
            {!isCollapsed && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col">
                <span className="font-extrabold text-lg tracking-wider text-white">
                  KINNEST
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-widest text-[#D4A72C]">
                  Father Agent AI
                </span>
              </motion.div>
            )}
          </NavLink>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg text-slate-400 hover:text-white hover:bg-[#243B53] transition-colors"
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation List */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-thin">
          {navigationGroups.map((group, idx) => (
            <div key={idx} className="space-y-1">
              {!isCollapsed && (
                <div className="px-3 text-[10px] font-bold text-slate-400/80 uppercase tracking-widest mb-2">
                  {group.title}
                </div>
              )}
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileOpen(false)}
                    className="block"
                  >
                    {({ isActive }) => (
                      <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 group relative ${
                        isActive
                          ? 'bg-[#243B53] text-[#F7F9FC] border border-[#0F766E]/30 shadow-md'
                          : 'text-slate-300 hover:text-white hover:bg-[#243B53]/40'
                      }`}>
                        {isActive && (
                          <motion.div
                            layoutId="activeIndicator"
                            className="absolute left-0 w-1 h-6 bg-[#D4A72C] rounded-r-md"
                            transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                          />
                        )}
                        <Icon className={`w-5 h-5 shrink-0 transition-transform group-hover:scale-110 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                        {!isCollapsed && (
                          <span className="truncate flex-1">{item.name}</span>
                        )}
                        {!isCollapsed && item.badge && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase rounded-md bg-[#0F766E]/30 text-emerald-300 border border-[#0F766E]/40">
                            {item.badge}
                          </span>
                        )}
                      </div>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </div>

        {/* Footer Agent Card */}
        {!isCollapsed && (
          <div className="p-3 border-t border-[#243B53]">
            <div className="p-3 rounded-xl bg-[#0B1F33] border border-[#243B53] flex items-center gap-3">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-slate-200">Financial Intelligence</span>
                <span className="text-[10px] text-slate-400">Autonomous Orchestrator</span>
              </div>
            </div>
          </div>
        )}
      </motion.aside>
    </>
  );
};

export default Sidebar;
