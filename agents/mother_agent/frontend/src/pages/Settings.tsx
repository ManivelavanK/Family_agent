import React, { useState } from 'react';
import { db } from '../data/mockData';
import { Users, ShieldCheck, Save } from 'lucide-react';

export const Settings: React.FC = () => {
  const [familyBudget, setFamilyBudget] = useState(db.familyContext.weeklyBudget);
  const [dietPref, setDietPref] = useState(db.familyContext.dietPreference);
  const [notifications, setNotifications] = useState(true);
  const [mockMode, setMockMode] = useState(localStorage.getItem('kinnest_mock_mode') === 'true');
  const [saving, setSaving] = useState(false);

  const capabilities = [
    'Inventory Monitoring & Tracking',
    'AI Consumption Prediction',
    'Smart Shopping List Generation',
    'Weekly Meal Plan Recommendations',
    'Grocery Budget Awareness',
    'Food Waste Monitor & Reduction Tips',
    'Proactive Critical Alerts'
  ];

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      db.familyContext.weeklyBudget = familyBudget;
      db.familyContext.dietPreference = dietPref;
      setSaving(false);
      alert('Settings updated successfully!');
    }, 800);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Mother Agent Settings</h1>
        <p className="text-slate-500 font-medium text-xs mt-1">Configure family contexts, AI agent capabilities, and data settings.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Editable Parameters */}
        <div className="lg:col-span-2 space-y-6">
          {/* Family Context Form */}
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs">
            <div className="flex items-center gap-2 mb-4">
              <Users className="h-4.5 w-4.5 text-indigo-600" />
              <h3 className="font-bold text-slate-800 text-sm">Family & Dietary Context</h3>
            </div>

            <form onSubmit={handleSaveSettings} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-2">Household Name</label>
                  <input
                    type="text"
                    value={db.familyContext.name}
                    disabled
                    className="w-full rounded-xl border border-slate-150 p-3 text-xs font-semibold bg-slate-55/40 text-slate-500 cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-2">Diet Preference</label>
                  <select
                    value={dietPref}
                    onChange={(e) => setDietPref(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 p-3 text-xs font-semibold focus:border-indigo-500 focus:outline-none bg-white"
                  >
                    <option value="South Indian">South Indian</option>
                    <option value="North Indian">North Indian</option>
                    <option value="Mixed Indian Diet">Mixed Indian Diet</option>
                    <option value="Continental / Western">Continental / Western</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-2">Weekly Grocery Budget (₹)</label>
                <input
                  type="number"
                  value={familyBudget}
                  onChange={(e) => setFamilyBudget(Number(e.target.value))}
                  className="w-full rounded-xl border border-slate-200 p-3 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  min={100}
                  required
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-1.5 rounded-xl bg-indigo-650 hover:bg-indigo-755 text-white font-bold px-4.5 py-2.5 text-xs shadow-md shadow-indigo-100 transition-colors cursor-pointer"
                >
                  <Save className="h-4 w-4" />
                  {saving ? 'Saving...' : 'Save Settings'}
                </button>
              </div>
            </form>
          </div>

          {/* System Configs */}
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="h-4.5 w-4.5 text-indigo-600" />
              <h3 className="font-bold text-slate-800 text-sm">System & Demo Toggles</h3>
            </div>

            <div className="space-y-4 divide-y divide-slate-50">
              {/* Push notifications */}
              <div className="flex items-center justify-between pt-2">
                <div>
                  <span className="block font-bold text-slate-850 text-xs">Enable Proactive Alerts</span>
                  <span className="block text-[10px] text-slate-400 font-medium">Allow Mother Agent to push stock warnings instantly</span>
                </div>
                <input
                  type="checkbox"
                  checked={notifications}
                  onChange={(e) => setNotifications(e.target.checked)}
                  className="h-4 w-8 rounded-full bg-slate-200 text-indigo-600 border-none cursor-pointer focus:ring-0"
                />
              </div>

              {/* API Mode toggle */}
              <div className="flex items-center justify-between pt-4">
                <div>
                  <span className="block font-bold text-slate-850 text-xs">Simulate Demo Data (Mock Mode)</span>
                  <span className="block text-[10px] text-slate-400 font-medium">Use frontend local states instead of making backend calls</span>
                </div>
                <input
                  type="checkbox"
                  checked={mockMode}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setMockMode(checked);
                    localStorage.setItem('kinnest_mock_mode', String(checked));
                    window.location.reload();
                  }}
                  className="h-4 w-8 rounded-full bg-slate-200 text-indigo-600 border-none cursor-pointer focus:ring-0"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Profile & Capabilities */}
        <div className="space-y-6">
          {/* Agent Card */}
          <div className="rounded-2xl border border-indigo-100 bg-linear-to-b from-indigo-50/40 to-indigo-100/10 p-6 shadow-xs relative overflow-hidden">
            <div className="absolute -top-3 -right-3 text-indigo-500/10 font-bold text-7xl select-none pointer-events-none">
              ✨
            </div>

            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-100 font-bold text-lg">
                MA
              </div>
              <div>
                <h3 className="font-bold text-slate-800 text-sm">Mother Agent</h3>
                <span className="block text-[10px] font-bold text-indigo-600">Household Intelligence Specialist</span>
              </div>
            </div>

            <span className="block text-[10px] font-bold text-indigo-700 uppercase tracking-wider mb-2">Primary Core Capabilities</span>
            <div className="space-y-2 border-t border-indigo-50 pt-3">
              {capabilities.map((cap, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs font-semibold text-slate-655">
                  <ShieldCheck className="h-4.5 w-4.5 text-indigo-600 shrink-0" />
                  <span>{cap}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Household Context */}
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4">
            <div className="flex items-center gap-2">
              <Users className="h-4.5 w-4.5 text-indigo-650" />
              <h3 className="font-bold text-slate-800 text-sm">Household Members ({db.familyContext.members.length})</h3>
            </div>
            <div className="space-y-3">
              {db.familyContext.members.map((member, idx) => (
                <div key={idx} className="flex items-center justify-between rounded-xl bg-slate-50/50 p-3 border border-slate-100">
                  <span className="font-bold text-slate-700 text-xs">{member.name}</span>
                  <span className="text-[10px] bg-slate-100 text-slate-550 font-semibold px-2 py-0.5 rounded-md border border-slate-200/50">
                    {member.role}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Settings;
