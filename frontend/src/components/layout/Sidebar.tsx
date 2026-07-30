import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Home, Users, UserCircle, Baby, Calendar, Network, Grid,
  ChevronLeft, ChevronRight, LogOut, ArrowLeft, BarChart2,
  FileText, CreditCard,
  ShoppingCart, Star, Package, RefreshCw, Layers, Pill,
  Heart, BookOpen, Clock, Award,
  Droplets, Thermometer, ClipboardList,
  Map, Target, Shuffle, DollarSign,
  TrendingUp, Lightbulb, Bot, Scale, Shield, LineChart,
  Activity, Footprints, Mic, MessageCircle, Settings, AlertTriangle, User,
  LayoutDashboard, Book, CheckCircle, GraduationCap,
  CalendarClock, BrainCircuit, Moon, Utensils
} from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { useActiveTabStore } from '../../store/useActiveTabStore';
import { motion } from 'framer-motion';
import clsx from 'clsx';

// Dynamic Sidebar Options configured per workspace agent path
const GLOBAL_ITEMS = [
  { name: 'Roles Overview', path: '/roles', icon: Grid, color: 'text-slate-500', activeGlow: 'shadow-[0_0_12px_rgba(245,158,11,0.3)]' },
  { name: 'Dashboard', path: '/dashboard', icon: Home, color: 'text-slate-500', activeGlow: 'shadow-[0_0_12px_rgba(79,70,229,0.3)]' },
  { name: 'Father Agent', path: '/father', icon: UserCircle, color: 'text-blue-500', activeGlow: 'shadow-[0_0_12px_rgba(59,130,246,0.3)]' },
  { name: 'Mother Agent', path: '/mother', icon: UserCircle, color: 'text-pink-500', activeGlow: 'shadow-[0_0_12px_rgba(236,72,153,0.3)]' },
  { name: 'Children Agent', path: '/children', icon: Users, color: 'text-amber-500', activeGlow: 'shadow-[0_0_12px_rgba(245,158,11,0.3)]' },
  { name: 'Grandparent Agent', path: '/grandparent', icon: UserCircle, color: 'text-emerald-500', activeGlow: 'shadow-[0_0_12px_rgba(16,185,129,0.3)]' },
  { name: 'Baby Care', path: '/baby', icon: Baby, color: 'text-violet-500', activeGlow: 'shadow-[0_0_12px_rgba(139,92,246,0.3)]' },
  { name: 'Life Planner', path: '/planner', icon: Calendar, color: 'text-indigo-500', activeGlow: 'shadow-[0_0_12px_rgba(99,102,241,0.3)]' },
  { name: 'Orchestrator', path: '/orchestrator', icon: Network, color: 'text-slate-500', activeGlow: 'shadow-[0_0_12px_rgba(100,116,139,0.3)]' },
];

const AGENT_SPECIFIC_ITEMS: Record<string, { title: string; color: string; items: { id: string; name: string; icon: any }[] }> = {
  '/father': {
    title: 'Father Workspace',
    color: 'text-blue-400',
    items: []
  },
  '/mother': {
    title: 'Mother Workspace',
    color: 'text-pink-500',
    items: [
      { id: 'shopping', name: 'Shopping List', icon: ShoppingCart },
      { id: 'priority', name: 'Priority Items', icon: Star },
      { id: 'pantry', name: 'Pantry Tracker', icon: Package },
      { id: 'recurring', name: 'Recurring Orders', icon: RefreshCw },
      { id: 'preferences', name: 'Vendor Preferences', icon: Layers },
    ]
  },
  '/grandparent': {
    title: 'Grandparent Workspace',
    color: 'text-emerald-500',
    items: [
      { id: 'dashboard', name: 'Dashboard', icon: Activity },
      { id: 'profile', name: 'Profile', icon: User },
      { id: 'vitals', name: 'Health Vitals', icon: Heart },
      { id: 'medicine', name: 'Medicine', icon: Pill },
      { id: 'activity', name: 'Activity', icon: Footprints },
      { id: 'nutrition', name: 'Nutrition', icon: Droplets },
      { id: 'appointments', name: 'Appointments', icon: Calendar },
      { id: 'insurance', name: 'Insurance', icon: Shield },
      { id: 'memory', name: 'Memory Care', icon: BookOpen },
      { id: 'recommendations', name: 'AI Recommendations', icon: Lightbulb },
      { id: 'reminders', name: 'Reminders', icon: Clock },
      { id: 'forecast', name: 'Forecast', icon: TrendingUp },
      { id: 'emergency', name: 'Emergency SOS', icon: AlertTriangle },
      { id: 'voice', name: 'Voice Assistant', icon: Mic },
      { id: 'whatsapp', name: 'WhatsApp Notifications', icon: MessageCircle },
      { id: 'analytics', name: 'Analytics', icon: BarChart2 },
      { id: 'settings', name: 'Settings', icon: Settings }
    ]
  },
  '/children': {
    title: 'Children Workspace',
    color: 'text-amber-500',
    items: [
      { id: 'tasks', name: 'Tasks & Homework', icon: BookOpen },
      { id: 'activities', name: 'Extracurricular', icon: Award },
      { id: 'pocket', name: 'Pocket Money', icon: CreditCard },
      { id: 'screentime', name: 'Screen Time', icon: Clock },
    ]
  },
  '/baby': {
    title: 'Baby Care Workspace',
    color: 'text-violet-500',
    items: [
      { id: 'feeding', name: 'Feeding & Sleep Log', icon: Droplets },
      { id: 'health', name: 'Health & Temp', icon: Thermometer },
      { id: 'notes', name: 'Care Notes', icon: ClipboardList },
      { id: 'supplies', name: 'Supplies Checklist', icon: Package },
    ]
  },
  '/planner': {
    title: 'Planner Workspace',
    color: 'text-indigo-500',
    items: [
      { id: 'events', name: 'Upcoming Events', icon: Calendar },
      { id: 'trips', name: 'Trips & Vacations', icon: Map },
      { id: 'goals', name: 'Family Goals', icon: Target },
      { id: 'orchestrator', name: 'Task Orchestrator', icon: Shuffle },
    ]
  }
};

const FATHER_CATEGORIES = [
  {
    title: 'OVERVIEW',
    items: [
      { id: 'overview', name: 'Overview', icon: BarChart2 }
    ]
  },
  {
    title: 'MONEY',
    items: [
      { id: 'expenses', name: 'Expenses', icon: DollarSign },
      { id: 'income', name: 'Income', icon: TrendingUp },
      { id: 'budget', name: 'Budget', icon: Lightbulb }
    ]
  },
  {
    title: 'PLANNING',
    items: [
      { id: 'savings', name: 'Savings Goals', icon: Target },
      { id: 'bills', name: 'Bills', icon: FileText }
    ]
  },
  {
    title: 'AI INTELLIGENCE',
    items: [
      { id: 'ai_advisor', name: 'AI Advisor', icon: Bot, badge: 'AI', badgeColor: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' },
      { id: 'decision_center', name: 'Decision Center', icon: Scale, badge: 'NEW', badgeColor: 'bg-blue-500/20 text-blue-400 border border-blue-500/30' },
      { id: 'ask_before_spend', name: 'Ask Before Spend', icon: Shield, badge: 'NEW', badgeColor: 'bg-blue-500/20 text-blue-400 border border-blue-500/30' },
      { id: 'predictions', name: 'Predictions', icon: LineChart }
    ]
  }
];

const CHILDREN_CATEGORIES = [
  {
    title: 'WORKSPACE',
    items: [
      { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
      { id: 'study_hub', name: 'Study Hub', icon: Book },
      { id: 'assignments', name: 'Assignments', icon: FileText },
      { id: 'goals', name: 'Goals', icon: CheckCircle },
      { id: 'exams', name: 'Exams', icon: GraduationCap },
      { id: 'progress', name: 'Progress', icon: Activity },
      { id: 'focus', name: 'Focus & Habits', icon: Clock },
      { id: 'learning_path', name: 'Learning Path', icon: Map }
    ]
  },
  {
    title: 'AI INTELLIGENCE',
    items: [
      { id: 'ai_planner', name: 'AI Planner', icon: CalendarClock },
      { id: 'ai_tutor', name: 'AI Tutor', icon: BrainCircuit },
      { id: 'ai_companion', name: 'AI Companion', icon: Bot }
    ]
  }
];

const BABY_CATEGORIES = [
  {
    title: 'CARE DASHBOARD',
    items: [
      { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
      { id: 'ai_assistant', name: 'AI Assistant', icon: Bot },
      { id: 'profile', name: 'Baby Profile', icon: Baby }
    ]
  },
  {
    title: 'LOGS & TRACKING',
    items: [
      { id: 'feeding', name: 'Feeding', icon: Droplets },
      { id: 'sleep', name: 'Sleep', icon: Moon },
      { id: 'diapers', name: 'Diapers', icon: Package },
      { id: 'growth', name: 'Growth', icon: TrendingUp }
    ]
  },
  {
    title: 'HEALTH',
    items: [
      { id: 'vaccinations', name: 'Vaccinations', icon: Shield },
      { id: 'health_logs', name: 'Health Logs', icon: ClipboardList },
      { id: 'alerts', name: 'Alerts', icon: AlertTriangle },
      { id: 'settings', name: 'Settings', icon: Settings }
    ]
  }
];

const MOTHER_CATEGORIES = [
  {
    title: 'MANAGEMENT',
    items: [
      { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
      { id: 'ai_assistant', name: 'AI Assistant', icon: Bot },
    ]
  },
  {
    title: 'HOUSEHOLD',
    items: [
      { id: 'inventory', name: 'Inventory', icon: Package },
      { id: 'shopping_list', name: 'Shopping List', icon: ShoppingCart },
      { id: 'meal_planner', name: 'Meal Planner', icon: Utensils },
      { id: 'purchases', name: 'Purchases', icon: CreditCard }
    ]
  },
  {
    title: 'ANALYTICS',
    items: [
      { id: 'insights', name: 'Insights', icon: BarChart2 },
      { id: 'alerts', name: 'Alerts', icon: AlertTriangle },
      { id: 'settings', name: 'Settings', icon: Settings }
    ]
  }
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { username, role, logout } = useAuthStore();
  const { activeTabs, setActiveTab } = useActiveTabStore();
  const [collapsed, setCollapsed] = useState(false);

  // Check if we are inside a dedicated agent path
  const currentBasePath = '/' + location.pathname.split('/')[1];
  const agentWorkspace = AGENT_SPECIFIC_ITEMS[currentBasePath];
  const isFather = currentBasePath === '/father';
  const isMother = currentBasePath === '/mother';
  const isChildren = currentBasePath === '/children';
  const isBaby = currentBasePath === '/baby';

  const handleLogout = () => {
    logout();
    navigate('/workspace');
  };

  return (
    <motion.div 
      animate={{ width: collapsed ? 80 : 256 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={clsx(
        "flex flex-col h-screen relative shrink-0 z-20 transition-colors duration-300",
        isFather 
          ? "bg-[#0D1520] border-r border-slate-800 text-slate-300" 
          : isChildren
          ? "bg-[#0B1320] border-r border-slate-800/60 text-slate-300"
          : "bg-white/80 backdrop-blur-md border-r border-slate-200/80 text-slate-800"
      )}
    >
      {/* Brand Header */}
      <div className={clsx(
        "h-16 flex items-center justify-between px-4 border-b overflow-hidden",
        (isFather || isChildren) ? "border-slate-800" : "border-slate-200/60"
      )}>
        {!collapsed && (
          <div className="flex items-center space-x-2 pl-2">
            {isFather ? (
              <div className="flex flex-col">
                <span className="text-base font-black tracking-wider text-white font-serif">
                  KinNest
                </span>
                <span className="text-[9px] font-bold text-amber-500 tracking-widest uppercase">
                  FATHER AGENT AI
                </span>
              </div>
            ) : isChildren ? (
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-blue-500 text-white flex items-center justify-center font-bold text-lg">K</div>
                <div className="flex flex-col">
                  <span className="text-base font-bold text-white leading-tight">KinNest</span>
                  <span className="text-[10px] text-blue-400 font-semibold tracking-wide">Academic Companion</span>
                </div>
              </div>
            ) : isBaby ? (
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-purple-500 text-white flex items-center justify-center font-bold text-lg">K</div>
                <div className="flex flex-col">
                  <span className="text-base font-bold text-slate-800 leading-tight">KinNest</span>
                  <span className="text-[10px] text-purple-600 font-semibold tracking-wide">Baby Care Agent</span>
                </div>
              </div>
            ) : isMother ? (
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-lg">K</div>
                <div className="flex flex-col">
                  <span className="text-base font-bold text-slate-800 leading-tight">KinNest</span>
                  <span className="text-[10px] text-indigo-600 font-semibold tracking-wide">Mother Agent</span>
                </div>
              </div>
            ) : (
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 font-serif">
                {agentWorkspace ? agentWorkspace.title : 'KinNest'}
              </span>
            )}
          </div>
        )}
        {collapsed && (
          <Link to="/roles" className="w-full flex justify-center text-xl">
            🏠
          </Link>
        )}
        
        <button 
          onClick={() => setCollapsed(!collapsed)}
          className={clsx(
            "p-1.5 rounded-lg transition-colors",
            (isFather || isChildren)
              ? "hover:bg-slate-800 text-slate-500 hover:text-slate-200" 
              : "hover:bg-slate-100 text-slate-400 hover:text-slate-700",
            collapsed && "mx-auto"
          )}
          title="Toggle Sidebar"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Switch Workspace back button */}
      {agentWorkspace && !collapsed && (
        <div className="px-3 pt-3">
          <Link 
            to="/roles" 
            className={clsx(
              "flex items-center justify-center space-x-2 px-4 py-2 border text-xs font-semibold rounded-xl transition-all shadow-sm w-full",
              isFather 
                ? "border-slate-800 bg-[#162232] text-slate-400 hover:bg-[#1C2C40] hover:text-white" 
                : isChildren
                ? "border-slate-800 bg-[#121A28] text-slate-400 hover:bg-[#1A2536] hover:text-white"
                : "border-slate-200 bg-white hover:bg-slate-50 text-slate-500"
            )}
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Switch Family Agent</span>
          </Link>
        </div>
      )}

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-3">
        {isFather ? (
          // Grouped Father Navigation
          <div className="space-y-4">
            {FATHER_CATEGORIES.map((category) => (
              <div key={category.title} className="space-y-1">
                {!collapsed && (
                  <p className="px-4 text-[9px] font-bold text-slate-500 tracking-wider uppercase mb-1">
                    {category.title}
                  </p>
                )}
                {category.items.map((tab) => {
                  const Icon = tab.icon;
                  const currentActiveTab = activeTabs['/father'] || 'overview';
                  const isActive = currentActiveTab === tab.id;
                  return (
                    <button 
                      key={tab.id} 
                      onClick={() => setActiveTab('/father', tab.id)}
                      className={clsx(
                        'w-full flex items-center py-2.5 text-xs font-medium rounded-xl transition-all relative group',
                        isActive 
                          ? 'bg-[#1A2638] text-white font-bold shadow-md border border-blue-500/30'
                          : 'text-slate-400 hover:bg-[#152030] hover:text-white',
                        collapsed ? 'justify-center px-0' : 'px-4'
                      )}
                    >
                      <Icon className={clsx("w-4.5 h-4.5 shrink-0", isActive ? "text-blue-400" : "text-slate-500", !collapsed && "mr-3")} />
                      {!collapsed && <span className="flex-1 text-left">{tab.name}</span>}
                      {!collapsed && tab.badge && (
                        <span className={clsx("text-[9px] px-1.5 py-0.5 rounded font-extrabold shrink-0 scale-90 origin-right", tab.badgeColor)}>
                          {tab.badge}
                        </span>
                      )}
                      
                      {collapsed && (
                        <div className="absolute left-full ml-4 px-3 py-1.5 bg-[#152030] border border-slate-700 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                          {tab.name}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        ) : isChildren ? (
          // Grouped Children Navigation
          <div className="space-y-4">
            {CHILDREN_CATEGORIES.map((category) => (
              <div key={category.title} className="space-y-1">
                {!collapsed && (
                  <p className="px-4 text-[9px] font-bold text-slate-500 tracking-wider uppercase mb-1">
                    {category.title}
                  </p>
                )}
                {category.items.map((tab) => {
                  const Icon = tab.icon;
                  const currentActiveTab = activeTabs['/children'] || 'dashboard';
                  const isActive = currentActiveTab === tab.id;
                  return (
                    <button 
                      key={tab.id} 
                      onClick={() => setActiveTab('/children', tab.id)}
                      className={clsx(
                        'w-full flex items-center py-2.5 text-xs font-medium rounded-xl transition-all relative group',
                        isActive 
                          ? 'bg-[#182436] text-blue-400 font-bold shadow-md border border-blue-500/20'
                          : 'text-slate-400 hover:bg-[#151E2D] hover:text-white',
                        collapsed ? 'justify-center px-0' : 'px-4'
                      )}
                    >
                      <Icon className={clsx("w-4 h-4 shrink-0", isActive ? "text-blue-400" : "text-slate-500", !collapsed && "mr-3")} />
                      {!collapsed && <span className="flex-1 text-left">{tab.name}</span>}
                      
                      {collapsed && (
                        <div className="absolute left-full ml-4 px-3 py-1.5 bg-[#151E2D] border border-slate-700 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                          {tab.name}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        ) : isBaby ? (
          // Grouped Baby Navigation
          <div className="space-y-4">
            {BABY_CATEGORIES.map((category) => (
              <div key={category.title} className="space-y-1">
                {!collapsed && (
                  <p className="px-4 text-[9px] font-bold text-slate-400 tracking-wider uppercase mb-1">
                    {category.title}
                  </p>
                )}
                {category.items.map((tab) => {
                  const Icon = tab.icon;
                  const currentActiveTab = activeTabs['/baby'] || 'dashboard';
                  const isActive = currentActiveTab === tab.id;
                  return (
                    <button 
                      key={tab.id} 
                      onClick={() => setActiveTab('/baby', tab.id)}
                      className={clsx(
                        'w-full flex items-center py-2.5 text-xs font-medium rounded-xl transition-all relative group',
                        isActive 
                          ? 'bg-purple-50 text-purple-700 font-bold shadow-sm border border-purple-200/50'
                          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900',
                        collapsed ? 'justify-center px-0' : 'px-4'
                      )}
                    >
                      <Icon className={clsx("w-4 h-4 shrink-0", isActive ? "text-purple-600" : "text-slate-400", !collapsed && "mr-3")} />
                      {!collapsed && <span className="flex-1 text-left">{tab.name}</span>}
                      
                      {collapsed && (
                        <div className="absolute left-full ml-4 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                          {tab.name}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        ) : isMother ? (
          // Grouped Mother Navigation
          <div className="space-y-4">
            {MOTHER_CATEGORIES.map((category) => (
              <div key={category.title} className="space-y-1">
                {!collapsed && (
                  <p className="px-4 text-[9px] font-bold text-slate-400 tracking-wider uppercase mb-1">
                    {category.title}
                  </p>
                )}
                {category.items.map((tab) => {
                  const Icon = tab.icon;
                  const currentActiveTab = activeTabs['/mother'] || 'dashboard';
                  const isActive = currentActiveTab === tab.id;
                  return (
                    <button 
                      key={tab.id} 
                      onClick={() => setActiveTab('/mother', tab.id)}
                      className={clsx(
                        'w-full flex items-center py-2.5 text-xs font-medium rounded-xl transition-all relative group',
                        isActive 
                          ? 'bg-indigo-50 text-indigo-700 font-bold shadow-sm border border-indigo-200/50'
                          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900',
                        collapsed ? 'justify-center px-0' : 'px-4'
                      )}
                    >
                      <Icon className={clsx("w-4 h-4 shrink-0", isActive ? "text-indigo-600" : "text-slate-400", !collapsed && "mr-3")} />
                      {!collapsed && <span className="flex-1 text-left">{tab.name}</span>}
                      
                      {collapsed && (
                        <div className="absolute left-full ml-4 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                          {tab.name}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        ) : agentWorkspace ? (
          // Dedicated Agent Navigation
          agentWorkspace.items.map((tab) => {
            const Icon = tab.icon;
            const currentActiveTab = activeTabs[currentBasePath];
            const isActive = currentActiveTab === tab.id;
            return (
              <button 
                key={tab.id} 
                onClick={() => setActiveTab(currentBasePath, tab.id)}
                className={clsx(
                  'w-full flex items-center py-3 text-sm font-medium rounded-xl transition-all relative group',
                  isActive 
                    ? 'bg-slate-100 text-slate-900 font-bold shadow-sm'
                    : 'text-slate-600 hover:bg-slate-50/50 hover:text-slate-900',
                  collapsed ? 'justify-center px-0' : 'px-4'
                )}
              >
                <Icon className={clsx("w-5 h-5 shrink-0", agentWorkspace.color, !collapsed && "mr-3")} />
                {!collapsed && <span>{tab.name}</span>}
                
                {collapsed && (
                  <div className="absolute left-full ml-4 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                    {tab.name}
                  </div>
                )}
              </button>
            );
          })
        ) : (
          // Global Switcher Navigation
          GLOBAL_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.path} 
                to={item.path} 
                className={clsx(
                  'flex items-center py-3 text-sm font-medium rounded-xl transition-all relative group',
                  isActive 
                    ? 'bg-slate-50 text-blue-600 font-bold ' + item.activeGlow
                    : 'text-slate-600 hover:bg-slate-50/50 hover:text-slate-900',
                  collapsed ? 'justify-center px-0' : 'px-4'
                )}
              >
                <Icon className={clsx("w-5 h-5 shrink-0", item.color, !collapsed && "mr-3")} />
                {!collapsed && <span>{item.name}</span>}
                
                {collapsed && (
                  <div className="absolute left-full ml-4 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                    {item.name}
                  </div>
                )}
              </Link>
            );
          })
        )}
      </nav>

      {/* Footer Area */}
      {isFather ? (
        <div className="p-4 border-t border-[#1B293A] bg-[#0A1018]">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0" />
            {!collapsed && (
              <div className="min-w-0">
                <p className="text-[10px] font-bold text-slate-200 truncate">Financial Intelligence</p>
                <p className="text-[8px] text-slate-500 font-bold uppercase tracking-wider truncate">Autonomous Orchestrator</p>
              </div>
            )}
          </div>
        </div>
      ) : isChildren ? (
        <div className="p-4 border-t border-[#1B293A]/50 bg-[#0A1018]">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shrink-0 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
            {!collapsed && (
              <div className="min-w-0">
                <p className="text-[11px] font-bold text-slate-300 truncate">AI Systems Online</p>
              </div>
            )}
          </div>
        </div>
      ) : isBaby ? (
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 text-slate-800">
          <div className={clsx("flex items-center overflow-hidden", collapsed ? "justify-center" : "space-x-3")}>
            <div className="w-8 h-8 rounded-xl bg-purple-100 flex items-center justify-center text-purple-600 font-bold text-xs uppercase shrink-0">
              <Users className="w-4 h-4" />
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-slate-800 truncate">Arunachalam Family</p>
                <p className="text-[10px] text-slate-500 font-semibold truncate flex items-center">
                  Family Workspace <ChevronRight className="w-3 h-3 ml-1" />
                </p>
              </div>
            )}
          </div>
        </div>
      ) : isMother ? (
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 text-slate-800">
          <div className={clsx("flex items-center overflow-hidden", collapsed ? "justify-center" : "space-x-3")}>
            <div className="w-8 h-8 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-xs uppercase shrink-0">
              <Users className="w-4 h-4" />
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-slate-800 truncate">Arunachalam Family</p>
                <p className="text-[10px] text-slate-500 font-semibold truncate flex items-center">
                  Family Workspace <ChevronRight className="w-3 h-3 ml-1" />
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 text-slate-800">
          <div className={clsx("flex items-center mb-3 overflow-hidden", collapsed ? "justify-center" : "space-x-3")}>
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white font-bold text-xs uppercase shrink-0 shadow-sm shadow-amber-500/20">
              {username ? username.substring(0, 2) : 'U'}
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-slate-800 truncate">{username || 'User'}</p>
                <p className="text-[10px] text-slate-400 font-semibold capitalize truncate">{role || 'Pending'}</p>
              </div>
            )}
          </div>
          
          {collapsed ? (
            <button 
              onClick={handleLogout}
              className="w-full flex justify-center p-2 text-red-500 hover:bg-red-50 hover:text-red-700 rounded-lg transition-colors group relative"
            >
              <LogOut className="w-4 h-4" />
              <div className="absolute left-full ml-4 px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg z-30">
                Sign Out
              </div>
            </button>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full text-center text-xs py-2 bg-white hover:bg-red-50 border border-red-200 hover:border-red-300 text-red-600 font-bold rounded-xl transition-all shadow-sm"
            >
              Sign Out
            </button>
          )}
        </div>
      )}
    </motion.div>
  );
}
