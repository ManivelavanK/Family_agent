import { 
  LayoutDashboard, 
  CalendarCheck, 
  Calendar, 
  CheckSquare, 
  Target, 
  Activity, 
  Users, 
  Bot, 
  Sparkles, 
  Bell, 
  Cpu,
  Settings
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  notificationsCount: number;
}

export default function Sidebar({ activeTab, setActiveTab, notificationsCount }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'todays-plan', label: "Today's Plan", icon: CalendarCheck },
    { id: 'calendar', label: 'Calendar', icon: Calendar },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'goals', label: 'Goals', icon: Target },
    { id: 'habits', label: 'Habits', icon: Activity },
    { id: 'family-schedule', label: 'Family Schedule', icon: Users },
    { id: 'ai-planner', label: 'AI Planner', icon: Bot, isAi: true },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles },
    { id: 'digital-twin', label: 'Digital Twin', icon: Cpu },
    { id: 'notifications', label: 'Notifications', icon: Bell, badge: notificationsCount },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 sidebar-navy flex flex-col justify-between shrink-0 h-screen select-none border-r border-[#1D3A5F]">
      <div>
        {/* Sidebar Brand Header */}
        <div className="p-6 border-b border-[#1D3A5F] flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 shrink-0">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">KinNest</h1>
            <p className="text-[10px] text-indigo-300 font-semibold uppercase tracking-wider">Planner Agent</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1 overflow-y-auto max-h-[calc(100vh-170px)]">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl transition-all duration-200 ${
                  active 
                    ? 'bg-[#1D4ED8] text-white font-medium shadow-md shadow-[#1D4ED8]/20' 
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4.5 w-4.5 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span className="text-sm">{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-[#EF4444] text-white rounded-full">
                    {item.badge}
                  </span>
                ) : null}
                {item.isAi && !active && (
                  <span className="h-2 w-2 rounded-full bg-[#7C3AED] animate-pulse"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Online Status Widget */}
      <div className="p-4 border-t border-[#1D3A5F] bg-[#0C1F35] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span className="text-xs font-semibold text-slate-200">AI Planner Online</span>
        </div>
        <div className="h-7 w-7 rounded-full bg-white/10 flex items-center justify-center text-xs font-bold text-white uppercase">
          LA
        </div>
      </div>
    </aside>
  );
}
