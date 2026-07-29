import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Network, ArrowRight, RefreshCw } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';

interface AgentNode {
  name: str;
  status: str;
  port: number;
  version: str;
}

interface TaskLog {
  task_id: str;
  priority: str;
  status: str;
  logs: str[];
  workflow_name?: str;
  created_at: str;
}

export default function Orchestrator() {
  const token = useAuthStore(state => state.token);
  
  const [agents, setAgents] = useState<AgentNode[]>([]);
  const [tasks, setTasks] = useState<TaskLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchOrchestratorData = async () => {
    if (!token) return;
    try {
      // 1. Fetch agents
      const resAgents = await fetch('http://localhost:8000/orchestrator/agents', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resAgents.ok) {
        const dataAgents = await resAgents.json();
        setAgents(dataAgents);
      }

      // 2. Fetch tasks
      const resTasks = await fetch('http://localhost:8000/orchestrator/tasks', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resTasks.ok) {
        const dataTasks = await resTasks.json();
        setTasks(dataTasks);
      }
    } catch (e) {
      console.error("Error fetching orchestrator metrics:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOrchestratorData();
    // Poll every 5 seconds for status updates
    const interval = setInterval(fetchOrchestratorData, 5000);
    return () => clearInterval(interval);
  }, [token]);

  // Helper to resolve colors based on status
  const getStatusColor = (agentName: string) => {
    const agent = agents.find(a => a.name.toLowerCase() === agentName.toLowerCase());
    return agent?.status === 'ONLINE' ? 'bg-green-500 shadow-green-500/50' : 'bg-red-500 shadow-red-500/50';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <Network className="w-8 h-8 text-blue-600 mr-3" />
          <h1 className="text-2xl font-bold text-slate-900">AI Orchestrator</h1>
        </div>
        <button 
          onClick={fetchOrchestratorData}
          className="p-2 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors"
          title="Refresh Metrics"
        >
          <RefreshCw className="w-5 h-5 text-slate-600" />
        </button>
      </div>

      <div className="bg-slate-900 rounded-3xl p-8 shadow-xl min-h-[500px] flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>

        {isLoading ? (
          <div className="text-slate-400 font-medium z-10 flex flex-col items-center">
            <RefreshCw className="w-8 h-8 animate-spin mb-2 text-blue-500" />
            Loading Orchestrator topology...
          </div>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-16 relative z-10 w-full max-w-4xl">
              {/* Father Node */}
              <div className="flex flex-col items-center">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg mb-3 text-white font-bold transition-all ${getStatusColor('father')}`}>
                  Father
                </div>
                <span className="text-xs text-slate-400">Port 8002</span>
              </div>
              
              {/* Core Orchestrator Hub */}
              <div className="flex flex-col items-center justify-center">
                <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50 mb-3 z-20 text-white font-bold text-lg animate-pulse">
                  Gateway
                </div>
                <span className="text-xs text-indigo-400 font-semibold">Port 8000</span>
              </div>

              {/* Mother Node */}
              <div className="flex flex-col items-center">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg mb-3 text-white font-bold transition-all ${getStatusColor('mother')}`}>
                  Mother
                </div>
                <span className="text-xs text-slate-400">Port 8001</span>
              </div>

              {/* Grandparent Node */}
              <div className="flex flex-col items-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 text-white font-bold text-sm transition-all ${getStatusColor('grandparent')}`}>
                  Grand
                </div>
                <span className="text-xs text-slate-400">Port 8004</span>
              </div>

              {/* Life Planner Node */}
              <div className="flex flex-col items-center justify-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 text-white font-bold text-sm transition-all ${getStatusColor('planner')}`}>
                  Planner
                </div>
                <span className="text-xs text-slate-400">Port 8006</span>
              </div>

              {/* Children Node */}
              <div className="flex flex-col items-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg mb-3 text-white font-bold text-sm transition-all ${getStatusColor('children')}`}>
                  Children
                </div>
                <span className="text-xs text-slate-400">Port 8003</span>
              </div>
            </div>

            {/* Message Logs */}
            <div className="mt-16 w-full max-w-3xl bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-slate-300 font-medium mb-4 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                Active Priority Task Execution Stream
              </h3>
              
              <div className="space-y-4 max-h-[250px] overflow-y-auto pr-2">
                {tasks.length === 0 ? (
                  <p className="text-slate-500 text-sm">No scheduled tasks or active workflows logged.</p>
                ) : (
                  tasks.slice().reverse().map((task, idx) => (
                    <div key={task.task_id} className="border-b border-slate-700/50 pb-3 last:border-b-0">
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-slate-500 font-mono">{task.task_id.substring(0, 8)}</span>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            task.priority === 'CRITICAL' ? 'bg-red-900/50 text-red-300' :
                            task.priority === 'HIGH' ? 'bg-amber-900/50 text-amber-300' : 'bg-slate-700 text-slate-300'
                          }`}>{task.priority}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            task.status === 'COMPLETED' ? 'bg-green-900/50 text-green-300' :
                            task.status === 'FAILED' ? 'bg-red-900/50 text-red-300' : 'bg-blue-900/50 text-blue-300'
                          }`}>{task.status}</span>
                        </div>
                      </div>
                      <div className="space-y-1.5 pl-3 border-l-2 border-slate-700">
                        {task.logs.slice(-3).map((log, lIdx) => (
                          <div key={lIdx} className="text-xs text-slate-300 flex items-center">
                            <span className="text-slate-500 mr-2">></span>
                            <span>{log}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
