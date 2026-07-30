import { useState, useEffect } from 'react';
import { Users, Bell, Calendar, UserCircle, Baby, Wifi, WifiOff, TrendingUp, ShoppingCart, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { orchestratorApi } from '../api/orchestratorApi';

const AGENT_CONFIG = [
  { name: 'father',      label: 'Father Agent',      icon: UserCircle, color: 'blue',    path: '/father',      desc: 'Budget & Finance' },
  { name: 'mother',      label: 'Mother Agent',       icon: ShoppingCart, color: 'pink', path: '/mother',      desc: 'Shopping & Groceries' },
  { name: 'children',   label: 'Children Agent',      icon: Users,      color: 'amber',   path: '/children',    desc: 'Education & Activities' },
  { name: 'grandparent',label: 'Grandparent Agent',   icon: Heart,      color: 'emerald', path: '/grandparent', desc: 'Health & Wellness' },
  { name: 'baby',        label: 'Baby Care Agent',     icon: Baby,       color: 'violet',  path: '/baby',        desc: 'Baby Monitoring' },
  { name: 'planner',    label: 'Life Planner',         icon: Calendar,   color: 'indigo',  path: '/planner',     desc: 'Events & Planning' },
];

const COLOR_MAP: Record<string, { bar: string; icon: string; badge: string }> = {
  blue:    { bar: 'bg-blue-500',    icon: 'text-blue-500',    badge: 'bg-blue-100' },
  pink:    { bar: 'bg-pink-500',    icon: 'text-pink-500',    badge: 'bg-pink-100' },
  amber:   { bar: 'bg-amber-500',   icon: 'text-amber-500',   badge: 'bg-amber-100' },
  emerald: { bar: 'bg-emerald-500', icon: 'text-emerald-500', badge: 'bg-emerald-100' },
  violet:  { bar: 'bg-violet-500',  icon: 'text-violet-500',  badge: 'bg-violet-100' },
  indigo:  { bar: 'bg-indigo-500',  icon: 'text-indigo-500',  badge: 'bg-indigo-100' },
};

export default function Dashboard() {
  const { token, username, role, familyId } = useAuthStore();
  const [agents, setAgents] = useState<any[]>([]);
  const [budgetData, setBudgetData] = useState<any>(null);
  const [shoppingData, setShoppingData] = useState<any>(null);
  const [healthData, setHealthData] = useState<any>(null);
  const [childData, setChildData] = useState<any>(null);
  const [babyData, setBabyData] = useState<any>(null);
  const [plannerData, setPlannerData] = useState<any>(null);
  const [orchestratorStatus, setOrchestratorStatus] = useState<any>(null);

  const fetchData = async () => {
    if (!token) return;
    try {
      // Get statuses
      const agentsData = await orchestratorApi.getAgents();
      const statusData = await orchestratorApi.getStatus();
      setAgents(agentsData);
      setOrchestratorStatus(statusData);

      // Attempt to load context details for all agents dynamically
      try {
        const data = await orchestratorApi.getContextCategory('budget');
        setBudgetData(data);
      } catch (_) {}

      try {
        const data = await orchestratorApi.getContextCategory('shopping');
        setShoppingData(data);
      } catch (_) {}

      try {
        const data = await orchestratorApi.getContextCategory('health');
        setHealthData(data);
      } catch (_) {}

      try {
        const data = await orchestratorApi.getContextCategory('child');
        setChildData(data);
      } catch (_) {}

      try {
        const data = await orchestratorApi.getContextCategory('baby');
        setBabyData(data);
      } catch (_) {}

      try {
        const data = await orchestratorApi.getContextCategory('planner');
        setPlannerData(data);
      } catch (_) {}

    } catch (_) {}
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [token]);

  const getAgentStatus = (name: string) => {
    const a = agents.find(a => a.name === name);
    return a ? a.status : 'OFFLINE';
  };

  const onlineCount = agents.filter(a => a.status === 'ONLINE').length;

  // Active status cards
  const statCards = [
    {
      label: 'Active Agents',
      value: `${onlineCount}/6`,
      icon: Wifi,
      color: 'bg-blue-100',
      iconColor: 'text-blue-600',
    },
    {
      label: 'Remaining Budget',
      value: budgetData ? `₹${budgetData.remaining_budget?.toLocaleString() ?? '--'}` : '--',
      icon: TrendingUp,
      color: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
    },
    {
      label: 'Shopping Items',
      value: shoppingData?.items ? `${shoppingData.items.length} items` : '0 items',
      icon: ShoppingCart,
      color: 'bg-pink-100',
      iconColor: 'text-pink-600',
    },
    {
      label: 'System Status',
      value: onlineCount === 6 ? 'All Systems Go' : 'Offline warnings',
      icon: Bell,
      color: onlineCount === 6 ? 'bg-indigo-100' : 'bg-rose-100',
      iconColor: onlineCount === 6 ? 'text-indigo-600' : 'text-rose-600',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">KinNest Family Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">
            Logged in as <span className="font-semibold text-amber-700">{username || 'User'}</span>
            {role && <span className="ml-2 text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">{role}</span>}
            {familyId && <span className="ml-2 text-xs text-slate-400">· Family: {familyId}</span>}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`w-2.5 h-2.5 rounded-full ${onlineCount > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-sm text-slate-500">{onlineCount > 0 ? 'System Online' : 'System Offline'}</span>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center"
          >
            <div className={`w-12 h-12 ${card.color} rounded-xl flex items-center justify-center mr-4 shrink-0`}>
              <card.icon className={`w-6 h-6 ${card.iconColor}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">{card.label}</p>
              <p className="text-2xl font-bold text-slate-900">{card.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Interactive Core Agent Boards */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4">Core Agent Working</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {AGENT_CONFIG.map((agent, i) => {
            const status = getAgentStatus(agent.name);
            const online = status === 'ONLINE';
            const colors = COLOR_MAP[agent.color];
            const Icon = agent.icon;

            // Get dynamic content for preview
            let preview = 'No data fetched yet.';
            if (agent.name === 'father' && budgetData) {
              preview = `Spent ₹${budgetData.current_spending?.toLocaleString()} of ₹${budgetData.monthly_budget?.toLocaleString()}`;
            } else if (agent.name === 'mother' && shoppingData) {
              preview = shoppingData.items?.length > 0 ? `To buy: ${shoppingData.items.slice(0, 3).join(', ')}...` : 'Shopping list is empty.';
            } else if (agent.name === 'children' && childData) {
              preview = childData.tasks?.length > 0 ? `Active Task: "${childData.tasks[0]}"` : 'All tasks completed!';
            } else if (agent.name === 'grandparent' && healthData) {
              preview = `Health score: ${healthData.health_score ?? '--'} | Meds: ${healthData.medications?.length ?? 0}`;
            } else if (agent.name === 'baby' && babyData) {
              preview = babyData.status || `Temp: ${babyData.temperature}°C | Sleep: ${babyData.sleep_hours}h`;
            } else if (agent.name === 'planner' && plannerData) {
              preview = plannerData.upcoming_events?.length > 0 ? `Next event: "${plannerData.upcoming_events[0]}"` : 'No upcoming events.';
            }

            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.07 }}
              >
                <Link
                  to={agent.path}
                  className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-all relative overflow-hidden group"
                >
                  <div className={`absolute top-0 left-0 w-1 h-full ${colors.bar}`} />
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center">
                      <div className={`w-10 h-10 ${colors.badge} rounded-xl flex items-center justify-center mr-3`}>
                        <Icon className={`w-5 h-5 ${colors.icon}`} />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-900 text-sm">{agent.label}</h3>
                        <p className="text-xs text-slate-400">{agent.desc}</p>
                      </div>
                    </div>
                    <span className={`flex items-center text-xs font-semibold px-2 py-1 rounded-full ${
                      online ? 'text-emerald-600 bg-emerald-50' : 'text-red-500 bg-red-50'
                    }`}>
                      {online
                        ? <><span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1 animate-pulse" />Online</>
                        : <><WifiOff className="w-3 h-3 mr-1" />Offline</>
                      }
                    </span>
                  </div>
                  <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 text-xs text-slate-600 mb-4 h-14 flex items-center">
                    {preview}
                  </div>
                  <p className="text-xs text-slate-400 group-hover:text-slate-600 transition-colors">
                    Click to interact & edit →
                  </p>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Orchestrator Status Bar */}
      {orchestratorStatus && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
          <div className="bg-slate-900 rounded-xl p-5 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse" />
              <span className="text-white font-semibold">Orchestrator Gateway</span>
              <span className="text-slate-400 text-sm">Port 8000</span>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <span className="text-slate-300">{orchestratorStatus.online_agents}/{orchestratorStatus.total_agents} agents online</span>
              <span className="text-slate-400">{orchestratorStatus.total_proxied_requests} requests proxied</span>
              <Link to="/orchestrator" className="text-amber-400 hover:text-amber-300 transition-colors font-medium">
                View Details →
              </Link>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}