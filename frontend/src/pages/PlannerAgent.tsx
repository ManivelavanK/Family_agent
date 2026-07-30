import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Plus, RefreshCw, ArrowLeft, Target, Shuffle } from 'lucide-react';
import { orchestratorApi } from '../api/orchestratorApi';

export default function PlannerAgent() {
  const { token } = useAuthStore();
  const navigate = useNavigate();
  const { activeTabs } = useActiveTabStore();
  const activeTab = activeTabs['/planner'] || 'events';

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [newEvent, setNewEvent] = useState('');
  const [updating, setUpdating] = useState(false);

  const fetchContext = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await orchestratorApi.getContextCategory('planner');
      setData(res);
      setErrorMsg('');
    } catch (err: any) { 
      setErrorMsg(err.message || 'Failed to fetch planner context'); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { fetchContext(); }, [token]);

  const addEvent = async () => {
    if (!token || !newEvent.trim()) return;
    setUpdating(true);
    try {
      const current = data?.upcoming_events || [];
      const res = await orchestratorApi.updateContextCategory('planner', { 
        upcoming_events: [...current, newEvent.trim()] 
      });
      if (res) { 
        setNewEvent(''); 
        fetchContext(); 
      }
    } catch (err: any) { 
      setErrorMsg(err.message || 'Update failed'); 
    } finally { 
      setUpdating(false); 
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => navigate('/roles')}
            className="p-2 hover:bg-slate-200 rounded-lg transition-colors text-slate-600"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Life Planner Agent</h1>
            <p className="text-slate-500 text-sm">Family Events & Planning · Port 8006</p>
          </div>
        </div>
        <button onClick={fetchContext} className="flex items-center space-x-2 text-sm text-slate-500 hover:text-slate-800 bg-white border border-slate-200 px-3 py-2 rounded-lg transition-colors shadow-sm">
          <RefreshCw className="w-4 h-4" /><span>Refresh</span>
        </button>
      </div>

      {errorMsg && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">{errorMsg}</div>}

      {loading ? (
        <div className="flex items-center justify-center h-48 text-slate-400">Loading planner data...</div>
      ) : data ? (
        <div className="space-y-6">
          {activeTab === 'events' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              {/* Upcoming Events */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center mb-4">
                  <Calendar className="w-5 h-5 text-indigo-500 mr-2" />
                  <h2 className="font-semibold text-slate-800">Upcoming Events</h2>
                </div>
                <div className="space-y-2 mb-4">
                  {(data.upcoming_events || []).length === 0 ? (
                    <p className="text-slate-400 text-sm py-3 text-center">No upcoming events. Plan something!</p>
                  ) : (data.upcoming_events as string[]).map((event, i) => (
                    <div key={i} className="flex items-center bg-indigo-50 rounded-lg px-4 py-3">
                      <span className="w-2 h-2 bg-indigo-400 rounded-full mr-3 shrink-0" />
                      <span className="text-sm text-slate-700">{event}</span>
                    </div>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <input type="text" value={newEvent} onChange={e => setNewEvent(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && addEvent()}
                    placeholder="Add event or trip..."
                    className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-300" />
                  <button onClick={addEvent} disabled={updating || !newEvent.trim()}
                    className="flex items-center space-x-1 px-4 py-2.5 bg-indigo-500 text-white rounded-xl text-sm font-medium hover:bg-indigo-600 transition-colors disabled:opacity-50">
                    <Plus className="w-4 h-4" /><span>Add</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'trips' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-2xl p-6 border border-slate-200 space-y-4">
              <h2 className="font-semibold text-slate-800 text-lg flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-indigo-500" /> Planned Family Trips
              </h2>
              <div className="space-y-2">
                {(data.trips || []).length > 0 ? (
                  data.trips.map((trip: string, i: number) => (
                    <div key={i} className="bg-blue-50 text-blue-800 rounded-lg px-4 py-2.5 text-sm flex items-center">
                      <MapPin className="w-3.5 h-3.5 mr-2 shrink-0" />{trip}
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400 text-sm">No vacation trips planned.</p>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'goals' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-2xl p-6 border border-slate-200 space-y-4">
              <h2 className="font-semibold text-slate-800 text-lg flex items-center">
                <Target className="w-5 h-5 mr-2 text-indigo-500" /> Long-term Family Goals
              </h2>
              <div className="space-y-2">
                {(data.goals || []).length > 0 ? (
                  data.goals.map((goal: string, i: number) => (
                    <div key={i} className="bg-emerald-50 text-emerald-800 rounded-lg px-4 py-2.5 text-sm">{goal}</div>
                  ))
                ) : (
                  <p className="text-slate-400 text-sm">No family goals registered.</p>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'orchestrator' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-2xl p-6 border border-slate-200 space-y-4">
              <h2 className="font-semibold text-slate-800 text-lg flex items-center">
                <Shuffle className="w-5 h-5 mr-2 text-indigo-500" /> Cross-Agent Task Orchestrator
              </h2>
              <p className="text-sm text-slate-600">
                Connected to life-planner microservice on <strong>Port 8006</strong>. Automated triggers sync calendar events, baby routines, and wellness checklists.
              </p>
            </motion.div>
          )}
        </div>
      ) : (
        <div className="text-center py-12 text-slate-400">No planner data available.</div>
      )}
    </div>
  );
}