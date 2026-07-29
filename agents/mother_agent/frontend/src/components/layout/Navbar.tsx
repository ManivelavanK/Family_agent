import React from 'react';
import { Menu, Bell, Search, ChevronDown } from 'lucide-react';
import { db } from '../../data/mockData';

interface NavbarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  title: string;
}

export const Navbar: React.FC<NavbarProps> = ({ sidebarOpen, setSidebarOpen, title }) => {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/80 px-6 backdrop-blur-md">
      {/* Left section: Toggle + Title */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="rounded-lg p-1.5 hover:bg-slate-50 text-slate-600 md:hidden transition-colors"
          aria-label="Toggle Sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h2 className="text-lg font-bold text-slate-800 leading-none">{title}</h2>
        </div>
      </div>

      {/* Right section: Search, Actions, Profile */}
      <div className="flex items-center gap-4">
        {/* Search Bar - hidden on small screens */}
        <div className="relative hidden max-w-xs md:block">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
            <Search className="h-4 w-4" />
          </span>
          <input 
            type="text" 
            placeholder="Search groceries, meals..."
            className="w-56 rounded-lg border border-slate-200 bg-slate-50 py-1.5 pl-9 pr-4 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none transition-colors"
          />
        </div>

        {/* Alerts Notification Button */}
        <div className="relative">
          <button className="relative rounded-lg p-1.5 hover:bg-slate-50 text-slate-500 hover:text-slate-800 transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-rose-500 ring-2 ring-white animate-pulse" />
          </button>
        </div>

        {/* User profile & selector */}
        <div className="flex items-center gap-3 border-l border-slate-100 pl-4">
          <div className="text-right hidden sm:block">
            <span className="block text-xs font-semibold text-slate-800">Meenakshi</span>
            <span className="block text-[10px] font-medium text-slate-400">Mother / Admin</span>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm border border-indigo-200 shadow-inner">
            M
          </div>
        </div>
      </div>
    </header>
  );
};
export default Navbar;
