import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  Sparkles,
  Baby,
  Milk,
  Moon,
  Layers,
  TrendingUp,
  Syringe,
  HeartPulse,
  Bell,
  Settings,
  ChevronDown,
  Users,
} from 'lucide-react';
import { db } from '../../data/mockData';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const navItems = [
  { name: 'Dashboard', path: '/', icon: Home },
  { name: 'AI Assistant', path: '/ai', icon: Sparkles },
  { name: 'Baby Profile', path: '/profile', icon: Baby },
  { name: 'Feeding', path: '/feeding', icon: Milk },
  { name: 'Sleep', path: '/sleep', icon: Moon },
  { name: 'Diapers', path: '/diapers', icon: Layers },
  { name: 'Growth', path: '/growth', icon: TrendingUp },
  { name: 'Vaccinations', path: '/vaccinations', icon: Syringe },
  { name: 'Health Logs', path: '/health-logs', icon: HeartPulse },
  { name: 'Alerts', path: '/alerts', icon: Bell },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, setIsOpen }) => {
  const [familyOpen, setFamilyOpen] = React.useState(false);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white px-5 py-6
          transition-transform duration-300 md:static md:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="mb-8 flex items-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-600 text-white font-bold text-xl shadow-md shadow-violet-100">
            K
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-slate-900 leading-none">KinNest</h1>
            <span className="text-xs font-medium text-violet-600">Baby Care Agent</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              onClick={() => setIsOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                ${isActive
                  ? 'bg-violet-50 text-violet-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Family Switcher */}
        <div className="relative border-t border-slate-100 pt-4">
          <button
            onClick={() => setFamilyOpen(!familyOpen)}
            className="flex w-full items-center justify-between rounded-lg p-2 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-100 text-violet-600">
                <Users className="h-4 w-4" />
              </div>
              <div>
                <span className="block text-xs text-slate-400 font-medium">Family</span>
                <span className="block text-sm font-semibold text-slate-800">{db.familyContext.name}</span>
              </div>
            </div>
            <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${familyOpen ? 'rotate-180' : ''}`} />
          </button>

          {familyOpen && (
            <div className="absolute bottom-full left-0 right-0 z-50 mb-2 rounded-lg border border-slate-100 bg-white p-1 shadow-lg">
              <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Switch Household
              </div>
              <button
                onClick={() => setFamilyOpen(false)}
                className="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm text-left font-medium text-slate-800 bg-slate-50"
              >
                <span>{db.familyContext.name}</span>
                <span className="text-xs text-violet-600 font-bold">Active</span>
              </button>
              <button
                onClick={() => setFamilyOpen(false)}
                className="flex w-full items-center rounded-md px-3 py-2 text-sm text-left text-slate-500 hover:bg-slate-50 transition-colors"
              >
                <span>Krishnan Family (Demo)</span>
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
