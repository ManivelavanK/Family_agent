import React, { useState } from 'react';
import { Plus, Layers, Droplets, AlertCircle } from 'lucide-react';

const DIAPER_TYPES = ['Wet', 'Dirty', 'Both'] as const;
type DiaperType = typeof DIAPER_TYPES[number];

interface DiaperChange {
  id: string;
  time: string;
  type: DiaperType;
  notes?: string;
}

const mockChanges: DiaperChange[] = [
  { id: 'd_1', time: new Date(Date.now() - 1 * 3600000).toISOString(), type: 'Wet' },
  { id: 'd_2', time: new Date(Date.now() - 3 * 3600000).toISOString(), type: 'Dirty', notes: 'Soft, yellowish - normal' },
  { id: 'd_3', time: new Date(Date.now() - 5 * 3600000).toISOString(), type: 'Wet' },
  { id: 'd_4', time: new Date(Date.now() - 7 * 3600000).toISOString(), type: 'Wet' },
  { id: 'd_5', time: new Date(Date.now() - 10 * 3600000).toISOString(), type: 'Both' },
  { id: 'd_6', time: new Date(Date.now() - 14 * 3600000).toISOString(), type: 'Dirty' },
];

const TYPE_CONFIG: Record<DiaperType, { bg: string; text: string; icon: string }> = {
  Wet:   { bg: 'bg-blue-100',   text: 'text-blue-700',   icon: '💧' },
  Dirty: { bg: 'bg-amber-100',  text: 'text-amber-700',  icon: '💩' },
  Both:  { bg: 'bg-violet-100', text: 'text-violet-700', icon: '🔄' },
};

function timeAgo(iso: string) {
  const diff = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (diff < 60) return `${diff}m ago`;
  return `${Math.round(diff / 60)}h ago`;
}

export default function Diapers() {
  const [changes, setChanges] = useState<DiaperChange[]>(mockChanges);

  const todayCount = changes.length;
  const wetCount   = changes.filter((c) => c.type === 'Wet' || c.type === 'Both').length;
  const dirtyCount = changes.filter((c) => c.type === 'Dirty' || c.type === 'Both').length;

  const logChange = (type: DiaperType) => {
    const newChange: DiaperChange = { id: `d_${Date.now()}`, time: new Date().toISOString(), type };
    setChanges((prev) => [newChange, ...prev]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Diaper Tracker</h1>
        <p className="text-sm text-slate-500 mt-0.5">Monitor Aarav's diaper changes and hydration</p>
      </div>

      {/* Today's Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Today's Changes", value: todayCount, icon: Layers,     bg: 'bg-violet-50', color: 'text-violet-600' },
          { label: 'Wet',            value: wetCount,   icon: Droplets,   bg: 'bg-blue-50',   color: 'text-blue-600'   },
          { label: 'Dirty',          value: dirtyCount, icon: AlertCircle, bg: 'bg-amber-50',  color: 'text-amber-600'  },
        ].map(({ label, value, icon: Icon, bg, color }) => (
          <div key={label} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm text-center">
            <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl ${bg}`}>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="text-xs text-slate-400 font-medium">{label}</p>
            <p className="text-2xl font-bold text-slate-900 mt-0.5">{value}</p>
          </div>
        ))}
      </div>

      {/* AI Insight */}
      <div className="rounded-2xl border border-cyan-100 bg-gradient-to-r from-cyan-50 to-blue-50 p-4">
        <p className="text-sm font-semibold text-cyan-700 mb-1">💧 AI Hydration Insight</p>
        <p className="text-sm text-slate-600">
          Aarav has had {wetCount} wet diapers today — hydration appears <strong>normal</strong>.
          WHO recommends ≥6 wet diapers/day for this age. Continue current feeding schedule.
        </p>
      </div>

      {/* Quick Log Buttons */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-700 mb-3">Log a Change</h3>
        <div className="flex gap-3">
          {DIAPER_TYPES.map((type) => {
            const cfg = TYPE_CONFIG[type];
            return (
              <button
                key={type}
                onClick={() => logChange(type)}
                className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors hover:opacity-90 ${cfg.bg} ${cfg.text}`}
              >
                <span>{cfg.icon}</span>
                {type}
              </button>
            );
          })}
        </div>
      </div>

      {/* Timeline */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-700 mb-4">Today's Timeline</h3>
        {changes.length === 0 ? (
          <div className="flex flex-col items-center py-12 text-center">
            <Layers className="h-12 w-12 text-slate-200 mb-3" />
            <p className="text-sm font-medium text-slate-500">No diaper changes logged yet.</p>
            <button className="mt-4 flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 transition-colors">
              <Plus className="h-4 w-4" />
              Log Change
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {changes.slice(0, 10).map((c) => {
              const cfg = TYPE_CONFIG[c.type];
              return (
                <div key={c.id} className="flex items-center gap-4 rounded-xl p-3 hover:bg-slate-50 transition-colors">
                  <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-lg ${cfg.bg}`}>
                    {cfg.icon}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm font-semibold ${cfg.text}`}>{c.type}</p>
                    {c.notes && <p className="text-xs text-slate-400 mt-0.5">{c.notes}</p>}
                  </div>
                  <span className="text-xs text-slate-400">{timeAgo(c.time)}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
