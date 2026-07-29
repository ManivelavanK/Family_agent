import React, { useState } from 'react';
import { Settings as SettingsIcon, Bell, Mic, Calendar, MessageSquare, Server, Download, Shield, Sun, Globe } from 'lucide-react';
import toast from 'react-hot-toast';

export const Settings: React.FC = () => {
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [schedulerEnabled, setSchedulerEnabled] = useState(true);
  const [whatsappEnabled, setWhatsappEnabled] = useState(true);
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:8000');
  const [whatsappPhone, setWhatsappPhone] = useState('+91 98765 43210');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    // Persist settings to localStorage
    localStorage.setItem('gp_settings', JSON.stringify({
      voiceEnabled,
      notificationsEnabled,
      schedulerEnabled,
      whatsappEnabled,
      apiUrl,
      whatsappPhone,
    }));
    setTimeout(() => {
      setSaving(false);
      toast.success('Settings saved successfully!');
    }, 800);
  };

  const handleExport = () => {
    const allData = {
      profile: localStorage.getItem('grandparent_profile'),
      vitals: localStorage.getItem('grandparent_vitals'),
      medicines: localStorage.getItem('grandparent_medicines'),
      activities: localStorage.getItem('grandparent_activities'),
      nutrition: localStorage.getItem('grandparent_nutrition'),
      appointments: localStorage.getItem('grandparent_appointments'),
      insurance: localStorage.getItem('grandparent_insurance'),
      journals: localStorage.getItem('grandparent_journals'),
    };
    const blob = new Blob([JSON.stringify(allData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `kinnest_grandparent_backup_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Health data exported successfully!');
  };

  const handleClearData = () => {
    if (!window.confirm('Are you sure you want to clear all locally stored health data? This will reset all cached data to mock defaults.')) return;
    const keys = ['grandparent_profile', 'grandparent_vitals', 'grandparent_medicines', 'grandparent_activities', 'grandparent_nutrition', 'grandparent_appointments', 'grandparent_insurance', 'grandparent_journals', 'grandparent_quizzes', 'grandparent_reminders', 'grandparent_notifications', 'grandparent_sos'];
    keys.forEach(k => localStorage.removeItem(k));
    toast.success('Local cache cleared. Data will reload from mock defaults.');
  };

  const ToggleSwitch: React.FC<{ enabled: boolean; onToggle: () => void; label: string; description: string; icon: React.ElementType; }> = ({ enabled, onToggle, label, description, icon: Icon }) => (
    <div className="flex items-center justify-between p-5 bg-white border border-sky-100 rounded-2xl hover:border-sky-200 transition-colors">
      <div className="flex items-center gap-4">
        <span className={`p-3 rounded-xl border ${enabled ? 'bg-sky-50 text-sky-600 border-sky-100' : 'bg-slate-50 text-slate-400 border-slate-100'}`}>
          <Icon className="h-5 w-5" />
        </span>
        <div>
          <span className="block text-base font-bold text-slate-800">{label}</span>
          <span className="block text-xs font-semibold text-slate-400">{description}</span>
        </div>
      </div>
      <button
        onClick={onToggle}
        className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors cursor-pointer ${enabled ? 'bg-sky-500' : 'bg-slate-200'}`}
      >
        <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-md transition-transform duration-200 ${enabled ? 'translate-x-8' : 'translate-x-1'}`} />
      </button>
    </div>
  );

  return (
    <div className="max-w-2xl space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4 bg-gradient-to-r from-slate-50 to-sky-50 border border-slate-100 rounded-2xl p-6">
        <div className="p-3 bg-slate-600 text-white rounded-xl">
          <SettingsIcon className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-800">System Settings</h3>
          <p className="text-sm font-semibold text-slate-400">Configure features, API connection, and data management preferences.</p>
        </div>
      </div>

      {/* Feature Toggles */}
      <div className="space-y-4">
        <h4 className="text-base font-bold text-slate-500 uppercase tracking-wider">Feature Controls</h4>
        <ToggleSwitch
          enabled={voiceEnabled}
          onToggle={() => setVoiceEnabled(!voiceEnabled)}
          label="Voice Assistant"
          description="Enable speech-to-text and AI voice interaction"
          icon={Mic}
        />
        <ToggleSwitch
          enabled={notificationsEnabled}
          onToggle={() => setNotificationsEnabled(!notificationsEnabled)}
          label="Health Notifications"
          description="Enable real-time medicine and appointment alerts"
          icon={Bell}
        />
        <ToggleSwitch
          enabled={schedulerEnabled}
          onToggle={() => setSchedulerEnabled(!schedulerEnabled)}
          label="Daily Scheduler"
          description="Automated daily check-ins and health monitoring"
          icon={Calendar}
        />
        <ToggleSwitch
          enabled={whatsappEnabled}
          onToggle={() => setWhatsappEnabled(!whatsappEnabled)}
          label="WhatsApp Alerts"
          description="Send family updates and reminders via WhatsApp"
          icon={MessageSquare}
        />
      </div>

      {/* API Configuration */}
      <div className="space-y-4">
        <h4 className="text-base font-bold text-slate-500 uppercase tracking-wider">Backend Connection</h4>
        <div className="bg-white border border-sky-100 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <span className="p-2.5 bg-slate-50 text-slate-600 rounded-xl border border-slate-100">
              <Server className="h-5 w-5" />
            </span>
            <div>
              <span className="block text-sm font-bold text-slate-700">FastAPI Backend URL</span>
              <span className="block text-xs font-semibold text-slate-400">The KinNest Grandparent Agent backend endpoint</span>
            </div>
          </div>
          <input
            type="text"
            value={apiUrl}
            onChange={e => setApiUrl(e.target.value)}
            className="w-full text-base p-3 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-400 font-mono"
            placeholder="http://localhost:8000"
          />

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">WhatsApp Primary Recipient</label>
            <input
              type="text"
              value={whatsappPhone}
              onChange={e => setWhatsappPhone(e.target.value)}
              className="w-full text-base p-3 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-400"
              placeholder="+91 98765 43210"
            />
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="space-y-4">
        <h4 className="text-base font-bold text-slate-500 uppercase tracking-wider">Data Management</h4>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={handleExport}
            className="flex items-center justify-center gap-2 px-5 py-3.5 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-emerald-700 font-bold rounded-xl transition-colors cursor-pointer"
          >
            <Download className="h-5 w-5" />
            <span>Export All Data</span>
          </button>
          <button
            onClick={handleClearData}
            className="flex items-center justify-center gap-2 px-5 py-3.5 bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-bold rounded-xl transition-colors cursor-pointer"
          >
            <Shield className="h-5 w-5" />
            <span>Clear Cache</span>
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-8 py-3.5 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold text-base rounded-2xl shadow-md transition-all cursor-pointer"
        >
          <SettingsIcon className="h-5 w-5" />
          <span>{saving ? 'Saving...' : 'Save Settings'}</span>
        </button>
      </div>
    </div>
  );
};
export default Settings;
