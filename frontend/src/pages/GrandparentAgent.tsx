import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { 
  Heart, Pill, Activity, Bell, 
  Droplet, Footprints, ArrowLeft, Stethoscope, CheckCircle2, AlertTriangle
} from 'lucide-react';
import clsx from 'clsx';

import { grandparentApi } from '../api/grandparentApi';

export default function GrandparentAgent() {
  const navigate = useNavigate();
  const { activeTabs } = useActiveTabStore();
  const activeTab = activeTabs['/grandparent'] || 'dashboard';

  // API States
  const [vitals, setVitals] = useState<any>(null);
  const [medications, setMedications] = useState<any>(null);
  const [visits, setVisits] = useState<any>(null);
  const [activity, setActivity] = useState<any>(null);

  // Local UI States
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [sosLoading, setSosLoading] = useState(false);
  const [sosModalOpen, setSosModalOpen] = useState(false);
  const [sosMessage, setSosMessage] = useState('');

  const fetchDashboardData = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      setErrorMsg('');
      const [resVitals, resMeds, resVisits, resActivity] = await Promise.all([
        grandparentApi.getVitals(),
        grandparentApi.getMedications(),
        grandparentApi.getVisits(),
        grandparentApi.getActivity()
      ].map(p => p.catch(err => {
        console.error("Fetch failed:", err);
        return null;
      })));

      if (resVitals) setVitals(resVitals);
      if (resMeds) setMedications(resMeds);
      if (resVisits) setVisits(resVisits);
      if (resActivity) setActivity(resActivity);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to connect to Grandparent microservice on Port 8004.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Auto-sync when window gains focus
    const handleFocus = () => fetchDashboardData(true);
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [activeTab]); // also refetch when switching tabs

  const triggerSOS = async () => {
    setSosLoading(true);
    try {
      const data = await grandparentApi.triggerEmergency();
      if (data) {
        setSosMessage(data.message || 'Emergency contacts notified!');
        setSosModalOpen(true);
      } else {
        alert('Failed to trigger SOS');
      }
    } catch (err) {
      console.error(err);
      alert('Error triggering SOS');
    } finally {
      setSosLoading(false);
    }
  };

  const getBadgeStyle = (status?: string, fallbackLabel?: string) => {
    const text = (status || fallbackLabel || '').toLowerCase();
    if (text.includes('warning')) return 'bg-amber-100 text-amber-700 border-amber-200';
    if (text.includes('normal') || text.includes('taken')) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    return 'bg-blue-100 text-blue-700 border-blue-200'; // default
  };

  if (loading && !vitals) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 font-semibold animate-pulse">
        Loading health dashboard...
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full space-y-4 font-sans antialiased text-slate-800">
      
      {/* Top Header & Greeting Banner */}
      <div className="flex flex-col md:flex-row md:items-stretch gap-4">
        
        {/* Left: Reassurance Banner */}
        <div className="flex-1 bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-3xl p-6 md:p-8 flex items-center justify-between shadow-sm">
          <div className="flex items-start space-x-4 text-white">
            <button onClick={() => navigate('/roles')} className="mt-1 p-1.5 hover:bg-white/20 rounded-xl transition-colors">
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-2">Namaste, Gopalaswamy!</h1>
              <p className="text-sm md:text-base font-medium opacity-90 leading-relaxed max-w-xl">
                Everything is looking stable today. Your morning medicines are checked, and your vitals are within target ranges.
              </p>
            </div>
          </div>
        </div>

        {/* Right: Emergency Controls */}
        <div className="flex flex-col justify-center items-center md:items-end space-y-3 bg-white border border-slate-200 rounded-3xl px-6 py-4 shadow-sm min-w-[250px]">
          <div className="flex items-center space-x-3 w-full justify-end">
            <button className="p-3 bg-slate-50 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-all border border-slate-200">
              <Bell className="w-6 h-6" />
            </button>
            <button 
              onClick={triggerSOS}
              disabled={sosLoading}
              className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 active:bg-red-700 text-white px-5 py-3 rounded-full font-bold shadow-lg shadow-red-500/30 transition-all disabled:opacity-50"
            >
              <AlertTriangle className="w-5 h-5" />
              <span>🚨 EMERGENCY SOS</span>
            </button>
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700 font-medium">
          {errorMsg}
        </div>
      )}

      {/* Main Layout */}
      <div className="w-full space-y-6">
        
        {activeTab === 'dashboard' ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              
              {/* Top Row: Live Vitals */}
              <div>
                <h2 className="text-lg font-extrabold text-slate-800 mb-4 px-1">Live Health Vitals</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                  {[
                    { label: 'Blood Pressure', data: vitals?.blood_pressure, icon: Heart, iconColor: 'text-rose-500' },
                    { label: 'Blood Sugar', data: vitals?.blood_sugar, icon: Activity, iconColor: 'text-blue-500' },
                    { label: 'Heart Rate', data: vitals?.heart_rate, icon: Activity, iconColor: 'text-rose-400' },
                    { label: 'Body Temp', data: vitals?.body_temp, icon: Droplet, iconColor: 'text-amber-500' }
                  ].map((card, i) => (
                    <div key={i} className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center space-x-2 text-sm font-bold text-slate-500 uppercase tracking-wide">
                          <card.icon className={clsx("w-4 h-4", card.iconColor)} />
                          <span>{card.label}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-2xl font-black text-slate-900 mb-1">{card.data?.value || '--'}</p>
                        <p className="text-sm font-medium text-slate-500 mb-3">{card.data?.subtitle || '--'}</p>
                        <span className={clsx("text-xs font-bold px-2.5 py-1 rounded-lg border", getBadgeStyle(card.data?.status, card.data?.badge))}>
                          {card.data?.badge || 'Unknown'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bottom Row: Routines */}
              <div>
                <h2 className="text-lg font-extrabold text-slate-800 mb-4 px-1">Health & Daily Routines</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                  {[
                    { label: 'Medicines Today', data: medications, icon: Pill, iconColor: 'text-emerald-500' },
                    { label: 'Next Appointment', data: visits, icon: Stethoscope, iconColor: 'text-indigo-500' },
                    { label: 'Water Intake', data: vitals?.water_intake, icon: Droplet, iconColor: 'text-cyan-500' },
                    { label: 'Today\'s Steps', data: activity, icon: Footprints, iconColor: 'text-orange-500' }
                  ].map((card, i) => (
                    <div key={i} className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center space-x-2 text-sm font-bold text-slate-500 uppercase tracking-wide">
                          <card.icon className={clsx("w-4 h-4", card.iconColor)} />
                          <span>{card.label}</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xl font-black text-slate-900 mb-1 truncate" title={card.data?.value}>{card.data?.value || '--'}</p>
                        <p className="text-sm font-medium text-slate-500 mb-3 truncate" title={card.data?.subtitle}>{card.data?.subtitle || '--'}</p>
                        <span className={clsx("text-xs font-bold px-2.5 py-1 rounded-lg border", getBadgeStyle(card.data?.status, card.data?.badge))}>
                          {card.data?.badge || 'Unknown'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </motion.div>
          ) : (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-3xl border border-slate-200 p-12 text-center shadow-sm">
              <h2 className="text-2xl font-bold text-slate-800 mb-2 capitalize">{activeTab.replace('-', ' ')}</h2>
              <p className="text-slate-500">This section is currently under development.</p>
            </motion.div>
          )}
        </div>
      
      {/* SOS Modal Overlay */}
      <AnimatePresence>
        {sosModalOpen && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
          >
            <motion.div 
              initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}
              className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-slate-100 text-center space-y-6"
            >
              <div className="mx-auto w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-2">
                <CheckCircle2 className="w-10 h-10 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-2xl font-black text-slate-900 mb-2">SOS Alert Sent!</h3>
                <p className="text-slate-600 font-medium leading-relaxed">{sosMessage}</p>
              </div>
              <button 
                onClick={() => setSosModalOpen(false)}
                className="w-full py-4 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-2xl transition-colors"
              >
                Dismiss
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
      `}</style>
    </div>
  );
}