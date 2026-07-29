import React, { useState } from 'react';
import { useFamily } from '../context/FamilyContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Settings as SettingsIcon, Server, User, Wifi, RefreshCw, ShieldCheck } from 'lucide-react';

export const Settings = () => {
  const { familyId, setFamilyId, isBackendConnected, isCheckingBackend, checkConnection } = useFamily();
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_FATHER_AGENT_API_URL || 'http://localhost:8000');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-slate-400" />
            <span>Settings & Configuration</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            System configuration, active backend endpoint, and family tenant scope.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Family Tenant Scope */}
        <GlassCard className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Active Family Context</h3>
              <p className="text-xs text-slate-400">Select multi-tenant family ID</p>
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-xs font-semibold text-slate-400">Family ID Scope</label>
            <select
              value={familyId}
              onChange={(e) => setFamilyId(Number(e.target.value))}
              className="w-full px-3 py-2.5 rounded-xl glass-input text-sm bg-slate-900"
            >
              <option value={1}>Family ID 1 (Primary Family)</option>
              <option value={2}>Family ID 2 (Secondary Family)</option>
            </select>
          </div>
        </GlassCard>

        {/* Backend Connection */}
        <GlassCard className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Backend Microservice</h3>
              <p className="text-xs text-slate-400">Father Agent API Base URL</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">API Endpoint URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl glass-input text-sm font-mono"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2 text-xs font-semibold">
                <span className={`w-2 h-2 rounded-full ${isBackendConnected ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                <span className={isBackendConnected ? 'text-emerald-400' : 'text-rose-400'}>
                  {isBackendConnected ? 'Connected & Responsive' : 'Service Unreachable'}
                </span>
              </div>

              <button
                onClick={checkConnection}
                disabled={isCheckingBackend}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs flex items-center gap-2 transition-colors"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isCheckingBackend ? 'animate-spin' : ''}`} />
                <span>Test Connection</span>
              </button>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default Settings;
