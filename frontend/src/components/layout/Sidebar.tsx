import { Link, useLocation } from 'react-router-dom';
import { Home, Users, UserCircle, Baby, Calendar, Network } from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: Home, color: 'text-slate-500' },
  { name: 'Father Agent', path: '/father', icon: UserCircle, color: 'text-blue-500' },
  { name: 'Mother Agent', path: '/mother', icon: UserCircle, color: 'text-pink-500' },
  { name: 'Children Agent', path: '/children', icon: Users, color: 'text-amber-500' },
  { name: 'Grandparent Agent', path: '/grandparent', icon: UserCircle, color: 'text-emerald-500' },
  { name: 'Baby Care', path: '/baby', icon: Baby, color: 'text-violet-500' },
  { name: 'Life Planner', path: '/planner', icon: Calendar, color: 'text-indigo-500' },
  { name: 'Orchestrator', path: '/orchestrator', icon: Network, color: 'text-slate-500' },
];

export default function Sidebar() {
  const location = useLocation();
  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-slate-200">
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">KinNest OS</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link key={item.path} to={item.path} className={clsx(
              'flex items-center px-6 py-3 text-sm font-medium transition-colors',
              isActive ? 'bg-slate-50 text-blue-600 border-r-2 border-blue-600' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            )}>
              <Icon className={clsx("w-5 h-5 mr-3", item.color)} />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold">U</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate">Current User</p>
          </div>
        </div>
      </div>
    </div>
  );
}