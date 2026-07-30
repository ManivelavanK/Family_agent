import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { motion } from 'framer-motion';
import { 
  Droplets, Moon, Package, TrendingUp, Shield,
  Sparkles, ChevronRight, Bell, Activity, Plus
} from 'lucide-react';

import { babyApi } from '../api/babyApi';

export default function BabyAgent() {
  const { token } = useAuthStore();
  const { activeTabs } = useActiveTabStore();
  const activeTab = activeTabs['/baby'] || 'dashboard';

  const [data, setData] = useState<any>(null);

  const fetchDashboardData = async () => {
    try {
      const res = await babyApi.getSummary(1);
      if (res && res.success) {
        setData(res.data);
      }
    } catch (error) {
      console.error("Error fetching baby data:", error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  // Derived metrics with safe fallbacks
  const feedingsCount = data?.feedings_today ?? 8;
  const nextFeed = data?.next_feed ?? "1:30 PM";
  
  const sleepHours = data?.total_sleep ?? 13.2;
  const sleepStatus = data?.sleep_status ?? "Excellent";
  
  const diapersCount = data?.diapers_today ?? 6;
  const dirtyDiapers = data?.dirty_diapers ?? 2;
  const wetDiapers = data?.wet_diapers ?? 4;
  
  const currentWeight = data?.current_weight ?? 8.4;
  const weightGain = data?.weight_gain ?? "+0.5";
  
  const nextVaccineDays = data?.next_vaccine_days ?? 6;
  const activeAlerts = data?.active_alerts ?? 2;
  
  const aiSummary = data?.ai_summary ?? "Aarav slept well last night for 8.5 hours. His feeding schedule is on track with 8 feeds today. Vaccination (Measles / MR) is due in 5 days...";

  const logAction = async (type: string) => {
    try {
      if (type === 'feeding') {
        await babyApi.logFeeding({ timestamp: new Date().toISOString() });
      } else if (type === 'sleep') {
        await babyApi.logSleep({ timestamp: new Date().toISOString() });
      }
      fetchDashboardData();
    } catch (error) {
      console.error(`Error logging ${type}:`, error);
    }
  };

  return (
    <div className="min-h-full bg-slate-50 text-slate-800 p-8 pb-12">
      
      {/* Header Summary Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-500 rounded-3xl p-8 mb-8 flex flex-col lg:flex-row items-start lg:items-center justify-between shadow-[0_10px_40px_rgba(124,58,237,0.2)] relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-[80px] pointer-events-none" />
        
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center bg-white/20 backdrop-blur-md border border-white/30 text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider mb-4 shadow-sm">
            <Sparkles className="w-3 h-3 mr-1.5" /> AI BABY SUMMARY
          </div>
          <p className="text-xl md:text-2xl text-white font-medium leading-relaxed drop-shadow-sm">
            {aiSummary}
          </p>
        </div>
        
        <div className="mt-6 lg:mt-0 relative z-10 flex flex-wrap gap-3">
          <button className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/30 text-white rounded-xl text-sm font-semibold transition-colors flex items-center shadow-sm">
            View Schedule <ChevronRight className="w-4 h-4 ml-1" />
          </button>
          <button className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/30 text-white rounded-xl text-sm font-semibold transition-colors flex items-center shadow-sm">
            Open Health Logs <ChevronRight className="w-4 h-4 ml-1" />
          </button>
          <button className="px-4 py-2 bg-white text-purple-700 hover:bg-slate-50 rounded-xl text-sm font-bold transition-colors flex items-center shadow-md">
            Ask AI <Sparkles className="w-4 h-4 ml-1.5 text-purple-500" />
          </button>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
          
          {/* Top KPI Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            
            {/* Feedings */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
              <Droplets className="w-6 h-6 text-purple-500 mb-3" />
              <div>
                <p className="text-3xl font-extrabold text-slate-800 mb-1">{feedingsCount}</p>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Today's Feedings</p>
                <p className="text-[10px] text-purple-600 font-medium mt-1.5 bg-purple-50 inline-block px-2 py-0.5 rounded-full">{nextFeed} Next Feed</p>
              </div>
            </div>

            {/* Sleep */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between relative hover:shadow-md transition-shadow">
              <div className="absolute top-4 right-4 bg-emerald-100 text-emerald-700 text-[9px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">
                {sleepStatus}
              </div>
              <Moon className="w-6 h-6 text-indigo-500 mb-3" />
              <div>
                <p className="text-3xl font-extrabold text-slate-800 mb-1">{sleepHours}h</p>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Total Sleep</p>
              </div>
            </div>

            {/* Diapers */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
              <Package className="w-6 h-6 text-sky-500 mb-3" />
              <div>
                <p className="text-3xl font-extrabold text-slate-800 mb-1">{diapersCount}</p>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Diaper Changes</p>
                <p className="text-[10px] text-slate-500 font-medium mt-1.5">
                  <span className="text-amber-600 font-bold">{dirtyDiapers} Dirty</span> · <span className="text-sky-600 font-bold">{wetDiapers} Wet</span>
                </p>
              </div>
            </div>

            {/* Weight */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
              <TrendingUp className="w-6 h-6 text-emerald-500 mb-3" />
              <div>
                <p className="text-3xl font-extrabold text-slate-800 mb-1">{currentWeight} <span className="text-lg text-slate-400 font-medium">kg</span></p>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Current Weight</p>
                <p className="text-[10px] text-emerald-600 font-bold mt-1.5 bg-emerald-50 inline-block px-2 py-0.5 rounded-full">{weightGain} kg Monthly Gain</p>
              </div>
            </div>

            {/* Vaccine */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between relative hover:shadow-md transition-shadow">
              {activeAlerts > 0 && (
                <div className="absolute top-4 right-4 bg-red-100 text-red-700 text-[9px] font-bold px-2 py-1 rounded-full uppercase tracking-wider animate-pulse">
                  {activeAlerts} Alerts
                </div>
              )}
              <Shield className="w-6 h-6 text-rose-500 mb-3" />
              <div>
                <p className="text-3xl font-extrabold text-slate-800 mb-1">{nextVaccineDays}d</p>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Next Vaccine</p>
                <p className="text-[10px] text-rose-600 font-medium mt-1.5 flex items-center"><Activity className="w-3 h-3 mr-1"/> AI Needs Attention</p>
              </div>
            </div>

          </div>

          {/* Bottom Split Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Card: BABY CARE INSIGHT */}
            <div className="lg:col-span-2 bg-white rounded-3xl p-8 border border-slate-200 shadow-sm">
              <h2 className="text-lg font-black text-slate-800 flex items-center mb-6">
                <Sparkles className="w-5 h-5 text-purple-500 mr-2" /> BABY CARE INSIGHT
              </h2>
              
              <ul className="space-y-4 mb-8">
                <li className="flex items-start">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-500 mt-1.5 mr-3 shrink-0 shadow-[0_0_8px_rgba(168,85,247,0.5)]" />
                  <p className="text-sm text-slate-700 leading-relaxed font-medium"><strong className="text-slate-900">Feeding observation:</strong> Aarav has been feeding more frequently over the past two days — possibly a growth spurt.</p>
                </li>
                <li className="flex items-start">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mt-1.5 mr-3 shrink-0 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                  <p className="text-sm text-slate-700 leading-relaxed font-medium"><strong className="text-slate-900">Sleep status:</strong> Sleep quality remains excellent — 8.5 hours last night with no disruptions.</p>
                </li>
                <li className="flex items-start">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500 mt-1.5 mr-3 shrink-0 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                  <p className="text-sm text-slate-700 leading-relaxed font-medium"><strong className="text-slate-900">Growth milestone:</strong> Growth is perfectly on track at the 50th WHO percentile.</p>
                </li>
                <li className="flex items-start bg-rose-50 p-3 rounded-xl border border-rose-100">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 mt-1.5 mr-3 shrink-0 shadow-[0_0_8px_rgba(244,63,94,0.5)] animate-pulse" />
                  <p className="text-sm text-rose-800 leading-relaxed font-medium"><strong className="text-rose-900">Health alert:</strong> Measles / MR Vaccination is due in 5 days. Schedule an appointment with Dr. Priya now.</p>
                </li>
              </ul>

              <div className="flex flex-wrap gap-3">
                <button className="px-6 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-bold transition-colors shadow-md shadow-purple-600/20">
                  View Schedule
                </button>
                <button className="px-6 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-sm font-bold transition-colors">
                  Open Health Logs
                </button>
              </div>
            </div>

            {/* Right Card: QUICK ACTIONS */}
            <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col">
              <h2 className="text-lg font-black text-slate-800 mb-6 uppercase tracking-tight">
                Quick Actions
              </h2>
              
              <div className="space-y-4 flex-1">
                <button onClick={() => logAction('feeding')} className="w-full flex items-center justify-between p-4 rounded-2xl bg-purple-50 hover:bg-purple-100 transition-colors border border-purple-100 group">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-xl bg-purple-200 text-purple-700 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                      <Droplets className="w-5 h-5" />
                    </div>
                    <span className="font-bold text-slate-800">Log a Feeding</span>
                  </div>
                  <Plus className="w-5 h-5 text-purple-500 group-hover:rotate-90 transition-transform" />
                </button>
                
                <button onClick={() => logAction('sleep')} className="w-full flex items-center justify-between p-4 rounded-2xl bg-indigo-50 hover:bg-indigo-100 transition-colors border border-indigo-100 group">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-xl bg-indigo-200 text-indigo-700 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                      <Moon className="w-5 h-5" />
                    </div>
                    <span className="font-bold text-slate-800">Log Sleep</span>
                  </div>
                  <Plus className="w-5 h-5 text-indigo-500 group-hover:rotate-90 transition-transform" />
                </button>

                <button className="w-full flex items-center justify-between p-4 rounded-2xl bg-slate-50 hover:bg-slate-100 transition-colors border border-slate-200 group">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                      <Bell className="w-5 h-5" />
                    </div>
                    <span className="font-bold text-slate-800">View Alerts</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>

          </div>

        </motion.div>
      ) : (
        <div className="flex items-center justify-center h-64 border-2 border-dashed border-slate-200 rounded-3xl bg-white/50">
          <p className="text-slate-400 text-lg font-medium">Work in progress: <span className="capitalize">{activeTab.replace('_', ' ')}</span> view</p>
        </div>
      )}
    </div>
  );
}