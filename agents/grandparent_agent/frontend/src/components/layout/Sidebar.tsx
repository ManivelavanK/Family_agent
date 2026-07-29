import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  User, 
  Activity, 
  Pill, 
  Footprints, 
  Apple, 
  Calendar, 
  ShieldCheck, 
  BrainCircuit, 
  Lightbulb, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  Mic, 
  MessageSquare, 
  BarChart3, 
  Settings,
  Heart
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, setIsOpen }) => {
  const menuItems = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Profile', path: '/profile', icon: User },
    { name: 'Health Vitals', path: '/vitals', icon: Heart },
    { name: 'Medicine', path: '/medicine', icon: Pill },
    { name: 'Activity', path: '/activity', icon: Footprints },
    { name: 'Nutrition', path: '/nutrition', icon: Apple },
    { name: 'Appointments', path: '/appointments', icon: Calendar },
    { name: 'Insurance', path: '/insurance', icon: ShieldCheck },
    { name: 'Memory Care', path: '/memory', icon: BrainCircuit },
    { name: 'AI Recommendations', path: '/recommendations', icon: Lightbulb },
    { name: 'Reminders', path: '/reminders', icon: Clock },
    { name: 'Forecast', path: '/forecast', icon: TrendingUp },
    { name: 'Emergency SOS', path: '/emergency', icon: AlertTriangle, highlight: true },
    { name: 'Voice Assistant', path: '/voice', icon: Mic },
    { name: 'WhatsApp Notifications', path: '/whatsapp', icon: MessageSquare },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-900/30 backdrop-blur-xs md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Navigation */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-sky-100 bg-white px-5 py-6 transition-transform duration-300 md:static md:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Brand Header */}
        <div className="mb-6 flex items-center gap-3 px-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-500 text-white font-extrabold text-2xl shadow-md shadow-sky-100">
            K
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-800 leading-none">KinNest</h1>
            <span className="text-xs font-semibold text-emerald-600">Grandparent Agent</span>
          </div>
        </div>

        {/* Scrollable Navigation Area */}
        <nav className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-base font-semibold transition-all
                ${item.highlight 
                  ? 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200/50' 
                  : isActive 
                    ? 'bg-sky-50 text-sky-700 shadow-xs border-l-4 border-sky-500 rounded-l-none' 
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}
              `}
            >
              <item.icon className={`h-5 w-5 ${item.highlight ? 'text-rose-600 animate-pulse' : ''}`} />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* User context footer */}
        <div className="border-t border-slate-100 pt-4 mt-2">
          <div className="flex items-center gap-3 px-2">
            <div className="h-10 w-10 rounded-full bg-emerald-100 border border-emerald-200 text-emerald-700 font-bold flex items-center justify-center text-lg">
              G
            </div>
            <div>
              <span className="block text-sm font-bold text-slate-800">G. Srinivasan</span>
              <span className="block text-xs font-semibold text-slate-400">Grandfather / Elder</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;
