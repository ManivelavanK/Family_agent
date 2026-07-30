import { Bell, Search, ChevronDown, User, Bot } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import { useState, useEffect } from 'react';
import { useAuthStore } from '../../store/useAuthStore';

export default function Header() {
  const location = useLocation();
  const { username, role } = useAuthStore();
  const isFather = location.pathname === '/father';
  const isMother = location.pathname === '/mother';

  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [statusColor, setStatusColor] = useState('text-amber-500');

  useEffect(() => {
    if (!isFather) return;
    
    // Simulate checking backend connection
    const timer = setTimeout(() => {
      setBackendStatus('Connected');
      setStatusColor('text-emerald-500');
    }, 1500);

    return () => clearTimeout(timer);
  }, [isFather]);

  return (
    <header className={clsx(
      "h-16 border-b flex items-center justify-between px-6 shrink-0 transition-colors duration-300 z-10",
      isFather ? "bg-[#0D1520] border-slate-800 text-white" : "bg-white border-slate-200 text-slate-800"
    )}>
      {isFather ? (
        // Custom Father Agent Header
        <div className="flex flex-col">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
            <span>KinNest</span>
            <span>/</span>
            <span className="text-blue-400">Father AI Online</span>
          </div>
          <p className="text-[10px] text-slate-500 italic mt-0.5">
            "Your family's money, intelligently managed."
          </p>
        </div>
      ) : isMother ? (
        // Custom Mother Agent Header
        <div className="flex-1 flex items-center">
          <h1 className="text-xl font-bold text-slate-800 mr-8 font-serif">Dashboard</h1>
          <div className="max-w-md w-full relative text-slate-400">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Search groceries, meals..." 
              className="w-full pl-9 pr-4 py-1.5 bg-slate-100 border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow text-sm" 
            />
          </div>
        </div>
      ) : (
        // Standard Search Header
        <div className="flex-1 max-w-lg">
          <div className="relative text-slate-400">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" />
            <input 
              type="text" 
              placeholder="Global Search..." 
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" 
            />
          </div>
        </div>
      )}

      <div className="flex items-center space-x-4">
        {isFather && (
          <>
            {/* Status Indicator */}
            <div className={clsx(
              "flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50 text-[10px] font-bold tracking-wider",
              statusColor
            )}>
              <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
              <span>{backendStatus}</span>
            </div>

            {/* Family Selector */}
            <div className="relative group">
              <button className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-[#162232] border border-slate-800 hover:bg-[#1E2E44] text-[10px] font-bold text-slate-350 transition-colors">
                <User className="w-3.5 h-3.5 text-blue-400" />
                <span>Family: ID 1 (Primary)</span>
                <ChevronDown className="w-3 h-3 text-slate-500" />
              </button>
            </div>
          </>
        )}

        {/* Notification Bell */}
        <Link 
          to="/notifications" 
          className={clsx(
            "relative p-2 rounded-lg transition-colors",
            isFather ? "text-slate-450 hover:text-white hover:bg-slate-800/40" : "text-slate-400 hover:text-slate-500"
          )}
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </Link>

        {isMother && (
          <div className="flex items-center space-x-3 ml-2 pl-4 border-l border-slate-200">
            <div className="flex flex-col text-right">
              <span className="text-sm font-bold text-slate-800 leading-tight">{username || 'Meenakshi'}</span>
              <span className="text-[10px] font-semibold text-purple-600 tracking-wide uppercase">{role || 'Mother'} / Admin</span>
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-sm">
              {username ? username.charAt(0).toUpperCase() : 'M'}
            </div>
          </div>
        )}

        {isFather && (
          <button 
            onClick={() => {
              window.dispatchEvent(new CustomEvent('switch-father-tab', { detail: 'ai_advisor' }));
            }}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold shadow-md shadow-blue-500/10 hover:shadow-blue-500/20 active:scale-95 transition-all"
          >
            <Bot className="w-4 h-4" />
            <span>Consult Father AI</span>
          </button>
        )}
      </div>
    </header>
  );
}