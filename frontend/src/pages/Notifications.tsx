import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { Bell, Wifi, WifiOff, Activity } from 'lucide-react';

const BASE = 'http://localhost:8000';

export default function Notifications() {
  const { token } = useAuthStore();
  const [agents, setAgents] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchStatus = async () => {
    if (!token) return;
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [agentsRes, statusRes] = await Promise.all([
        fetch(`${BASE}/orchestrator/agents`, { headers }),
        fetch(`${BASE}/orchestrator/status`, { headers }),
      ]);
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (statusRes.ok) setStatus(await statusRes.json());
      setLastUpdated(new Date());
    } catch (_) {}
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [token]);

  const AGENT_META: Record<string, { color: string; desc: string }> = {
    mother:      { color: 'pink',    desc: 'Shopping & Groceries' },
    father:      { color: 'blue',    desc: 'Budget & Finance' },
    children:    { color: 'amber',   desc: 'Education & Activities' },
    grandparent: { color: 'emerald', desc: 'Health & Wellness' },
    baby:        { color: 'violet',  desc: 'Baby Monitoring' },
    planner:     { color: 'indigo',  desc: 'Events & Planning' },
  };

  const onlineCount = agents.filter(a => a.status === 'ONLINE').length;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">System Status</h1>
          <p className="text-slate-500 text-sm mt-1">
            Live agent health monitoring
            {lastUpdated && <span className="ml-2 text-xs text-slate-400">· Updated {lastUpdated.toLocaleTimeString()}</span>}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`w-2.5 h-2.5 rounded-full ${onlineCount === 6 ? 'bg-emerald-500 animate-pulse' : onlineCount > 0 ? 'bg-amber-500 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-sm font-medium text-slate-600">
            {onlineCount === 6 ? 'All Systems Go' : `${onlineCount}/6 Online`}
          </span>
        </div>
      </div>

      {/* Orchestrator Banner */}
      {status && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="bg-slate-900 rounded-xl p-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-white font-semibold">Orchestrator Gateway</p>
              <p className="text-slate-400 text-xs">Port 8000 · JWT Auth · RBAC</p>
            </div>
          </div>
          <div className="text-right text-sm">
            <p className="text-emerald-400 font-bold">{status.online_agents}/{status.total_agents} Agents Online</p>
            <p className="text-slate-400 text-xs">{status.total_proxied_requests} requests proxied</p>
          </div>
        </motion.div>
      )}

      {/* Agent Status Cards */}
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Agent Health</h2>
        <div className="space-y-3">
          {agents.map((agent, i) => {
            const meta = AGENT_META[agent.name] || { color: 'slate', desc: 'Agent' };
            const online = agent.status === 'ONLINE';
            return (
              <motion.div key={agent.name} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${online ? 'bg-emerald-50' : 'bg-slate-100'}`}>
                    {online ? <Wifi className="w-5 h-5 text-emerald-500" /> : <WifiOff className="w-5 h-5 text-slate-400" />}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 capitalize">{agent.name} Agent</p>
                    <p className="text-xs text-slate-400">{meta.desc} · Port {agent.port}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${
                    online ? 'bg-emerald-100 text-emerald-700' : 'bg-red-50 text-red-500'}`}>
                    {online ? '● ONLINE' : '○ OFFLINE'}
                  </span>
                </div>
              </motion.div>
            );
          })}

          {agents.length === 0 && (
            <div className="text-center py-12 text-slate-400 flex flex-col items-center space-y-2">
              <Bell className="w-8 h-8" />
              <p>No agent data — is the backend running?</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}