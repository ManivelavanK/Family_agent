import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { orchestratorApi } from '../api/orchestratorApi';

export default function Orchestrator() {
  const token = useAuthStore(state => state.token);
  const [agents, setAgents] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    if (!token) return;

    const fetchData = async () => {
      try {
        const [agentsData, tasksData] = await Promise.all([
          orchestratorApi.getAgents(),
          orchestratorApi.getTasks()
        ]);
        setAgents(agentsData);
        setTasks(tasksData);
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [token]);

  // Helper to determine if an agent is online
  const isOnline = (agentName: string) => {
    const agent = agents.find((a: any) => a.name?.toLowerCase() === agentName.toLowerCase());
    return agent && agent.status === 'ONLINE';
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center mb-8">
        <Network className="w-8 h-8 text-blue-600 mr-3" />
        <h1 className="text-2xl font-bold text-slate-900">AI Orchestrator</h1>
      </div>

      <div className="bg-slate-900 rounded-3xl p-8 shadow-xl min-h-[500px] flex flex-col items-center justify-center relative overflow-hidden">
        {/* Simple animated visualization */}
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>

        <div className="grid grid-cols-3 gap-16 relative z-10 w-full max-w-4xl">
          {/* Agents layout */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg mb-3 ${isOnline('Father') ? 'bg-blue-500 shadow-blue-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold">Father</span>
            </div>
          </motion.div>
          
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="flex flex-col items-center justify-center">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center shadow-lg mb-3 z-20 ${isOnline('Core') ? 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-purple-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold">Core</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col items-center">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg mb-3 ${isOnline('Mother') ? 'bg-pink-500 shadow-pink-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold">Mother</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="flex flex-col items-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 ${isOnline('Grandparent') ? 'bg-emerald-500 shadow-emerald-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold text-sm">Grand</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="flex flex-col items-center justify-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 ${isOnline('Planner') ? 'bg-indigo-500 shadow-indigo-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold text-sm">Planner</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="flex flex-col items-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 ${isOnline('Children') ? 'bg-amber-500 shadow-amber-500/50' : 'bg-slate-700 shadow-slate-900/50 opacity-50'}`}>
              <span className="text-white font-bold text-sm">Children</span>
            </div>
          </motion.div>
        </div>

        {/* Message Logs */}
        <div className="mt-16 w-full max-w-2xl bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <h3 className="text-slate-300 font-medium mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Live Agent Communication Stream
          </h3>
          <div className="space-y-3">
            <AnimatePresence>
              {tasks.length > 0 ? tasks.map((task: any, idx: number) => (
                <motion.div key={task.id || idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="flex items-center text-sm">
                  <span className="text-slate-500 mr-4">{new Date(task.timestamp || Date.now()).toLocaleTimeString()}</span>
                  <span className={`font-medium ${task.priority === 'CRITICAL' ? 'text-red-400' : task.priority === 'HIGH' ? 'text-orange-400' : 'text-blue-400'}`}>[{task.priority || 'NORMAL'}]</span>
                  <span className="ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md flex-1">{task.description || task.message || JSON.stringify(task)}</span>
                </motion.div>
              )) : (
                <div className="text-slate-500 text-sm">No tasks in stream...</div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}