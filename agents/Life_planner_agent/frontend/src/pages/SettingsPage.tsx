import { motion } from 'framer-motion';
import { Settings, Database, Sliders } from 'lucide-react';

export default function SettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-slate-100 text-slate-650">
            <Settings className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Settings</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Customize developer configurations and database controls</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 white-card p-6 space-y-6">
          <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider flex items-center gap-1.5">
            <Sliders className="h-4.5 w-4.5" /> General Configuration
          </h4>

          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500">Agent Autopilot Mode</label>
              <select className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold focus:outline-none">
                <option>Active (Auto rearrangement & conflict resolve)</option>
                <option>Manual (Requires prompt actions)</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500">Mock Data Fallbacks</label>
              <select className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold focus:outline-none">
                <option>Enabled (Development Sandbox)</option>
                <option>Disabled (Production APIs Only)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="white-card p-6 space-y-4">
          <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider flex items-center gap-1.5">
            <Database className="h-4.5 w-4.5" /> Infrastructure
          </h4>
          
          <div className="space-y-3.5 text-xs text-slate-600 font-semibold leading-relaxed">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <p className="text-slate-800">Database Engine</p>
              <p className="text-[10px] text-slate-450">PostgreSQL + SQLAlchemy v2</p>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <p className="text-slate-800">CORS Origins</p>
              <p className="text-[10px] text-slate-450">Allowed: *</p>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <p className="text-slate-800">API Endpoint</p>
              <p className="text-[10px] text-slate-450">http://localhost:8000/api/v1</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
