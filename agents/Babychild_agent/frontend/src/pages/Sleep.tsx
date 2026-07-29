import React, { useEffect, useState } from 'react';
import { Moon, Sparkles, Plus, Sun, Clock } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { sleepService } from '../services/sleepService';
import { SleepLog, SleepSummary } from '../types/sleep';
import { SkeletonCard } from '../components/common/SkeletonLoader';

const QUALITY_COLOR: Record<string, string> = {
  Excellent: 'bg-emerald-100 text-emerald-700',
  Good:      'bg-blue-100 text-blue-700',
  Fair:      'bg-amber-100 text-amber-700',
  Poor:      'bg-rose-100 text-rose-700',
};

// Mock weekly chart data
const weeklyData = [
  { day: 'Mon', sleep: 11.5 },
  { day: 'Tue', sleep: 12.0 },
  { day: 'Wed', sleep: 10.5 },
  { day: 'Thu', sleep: 13.0 },
  { day: 'Fri', sleep: 11.0 },
  { day: 'Sat', sleep: 13.25 },
  { day: 'Sun', sleep: 11.25 },
];

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
}
function formatDate(iso: string) {
  const d = new Date(iso);
  const today = new Date();
  const diff = Math.floor((today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Yesterday';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

export default function Sleep() {
  const [logs, setLogs] = useState<SleepLog[]>([]);
  const [summary, setSummary] = useState<SleepSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([sleepService.getSleepLogs(), sleepService.getSleepSummary()]).then(
      ([l, s]) => { setLogs(l); setSummary(s); setLoading(false); }
    );
  }, []);

  if (loading) return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Sleep Tracker</h1>
          <p className="text-sm text-slate-500 mt-0.5">Monitor Aarav's sleep patterns and quality</p>
        </div>
        <button className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-violet-700 transition-colors">
          <Plus className="h-4 w-4" />
          Log Sleep
        </button>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: "Today's Sleep", value: `${summary.todayTotal}h`, sub: 'Total', icon: Moon, bg: 'bg-indigo-50', color: 'text-indigo-600' },
            { label: 'Weekly Avg', value: `${summary.weeklyAverage}h`, sub: 'Per Day', icon: Clock, bg: 'bg-violet-50', color: 'text-violet-600' },
            { label: 'Quality', value: summary.qualityStatus, sub: 'Last Night', icon: Sparkles, bg: 'bg-emerald-50', color: 'text-emerald-600' },
            { label: 'Last Sleep', value: '8.5h', sub: 'Night Sleep', icon: Sun, bg: 'bg-amber-50', color: 'text-amber-600' },
          ].map(({ label, value, sub, icon: Icon, bg, color }) => (
            <div key={label} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
              <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${bg} mb-3`}>
                <Icon className={`h-4 w-4 ${color}`} />
              </div>
              <p className="text-xs text-slate-400 font-medium">{label}</p>
              <p className="text-xl font-bold text-slate-900 mt-0.5 leading-none">{value}</p>
              <p className="text-xs text-slate-400 mt-1">{sub}</p>
            </div>
          ))}
        </div>
      )}

      {/* Weekly Trend Chart */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-700">Weekly Sleep Trend</h3>
          <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-600">This Week</span>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={weeklyData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <defs>
              <linearGradient id="sleepGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[0, 15]} />
            <Tooltip
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontSize: 12 }}
              formatter={(v: unknown) => [`${v}h`, 'Sleep']}
            />
            <Area type="monotone" dataKey="sleep" stroke="#7c3aed" strokeWidth={2.5} fill="url(#sleepGrad)" dot={{ fill: '#7c3aed', r: 4, strokeWidth: 0 }} activeDot={{ r: 6 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* AI Summary */}
      {summary && (
        <div className="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50 to-violet-50 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="h-4 w-4 text-violet-600" />
            <h3 className="text-sm font-bold text-violet-700">AI Sleep Summary</h3>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed">{summary.insight}</p>
          <div className="mt-3 flex items-center gap-2">
            <Moon className="h-4 w-4 text-indigo-500" />
            <span className="text-xs text-slate-500 font-medium">Recommended total sleep for 10-month-old: 12–16 hours/day (WHO)</span>
          </div>
        </div>
      )}

      {/* Sleep Log Timeline */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-700 mb-4">Sleep Timeline</h3>
        {logs.length === 0 ? (
          <div className="flex flex-col items-center py-12 text-center">
            <Moon className="h-12 w-12 text-slate-200 mb-3" />
            <p className="text-sm font-medium text-slate-500">No sleep records yet.</p>
            <p className="text-xs text-slate-400 mt-1">Start logging sleep to track patterns.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start gap-4 rounded-xl border border-slate-50 p-4 hover:bg-slate-50 transition-colors">
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${log.type === 'Night Sleep' ? 'bg-indigo-100' : 'bg-amber-100'}`}>
                  {log.type === 'Night Sleep' ? <Moon className="h-5 w-5 text-indigo-600" /> : <Sun className="h-5 w-5 text-amber-600" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-slate-800">{log.type}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${QUALITY_COLOR[log.quality]}`}>
                      {log.quality}
                    </span>
                    <span className="text-xs text-slate-400 ml-auto">{formatDate(log.startTime)}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {formatTime(log.startTime)} – {formatTime(log.endTime)} · {log.duration}h
                  </p>
                  {log.notes && <p className="text-xs text-slate-400 mt-1 italic">{log.notes}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
