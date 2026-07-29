import React, { useEffect, useState } from 'react';
import { TrendingUp, Sparkles, Scale, Ruler } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { growthService } from '../services/growthService';
import { GrowthDataPoint, GrowthSummary } from '../types/growth';
import { SkeletonCard } from '../components/common/SkeletonLoader';

export default function Growth() {
  const [data, setData] = useState<GrowthDataPoint[]>([]);
  const [summary, setSummary] = useState<GrowthSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([growthService.getGrowthData(), growthService.getGrowthSummary()]).then(
      ([d, s]) => { setData(d); setSummary(s); setLoading(false); }
    );
  }, []);

  if (loading) return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );

  const latest = data[data.length - 1];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Growth Monitoring</h1>
        <p className="text-sm text-slate-500 mt-0.5">Track Aarav's growth vs WHO percentile curves</p>
      </div>

      {/* Key Metrics */}
      {latest && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: 'Current Weight', value: `${latest.weightKg} kg`, sub: '+0.3 kg this month', icon: Scale, bg: 'bg-emerald-50', color: 'text-emerald-600' },
            { label: 'Current Height', value: `${latest.heightCm} cm`, sub: '+1.5 cm this month', icon: Ruler, bg: 'bg-blue-50', color: 'text-blue-600' },
            { label: 'Head Circumference', value: `${latest.headCircumferenceCm} cm`, sub: 'Normal range', icon: TrendingUp, bg: 'bg-violet-50', color: 'text-violet-600' },
            { label: 'WHO Percentile', value: `${latest.weightPercentile}th`, sub: 'Median (Healthy)', icon: Sparkles, bg: 'bg-amber-50', color: 'text-amber-600' },
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

      {/* Weight Chart */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-700">Weight Trend (kg)</h3>
          <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-600">5 – 10 months</span>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="ageMonths" tickFormatter={(v) => `${v}m`} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[5, 10]} />
            <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontSize: 12 }}
              formatter={(v: unknown, name: unknown) => [name === 'weightKg' ? `${v} kg` : `${v}%`, name === 'weightKg' ? 'Weight' : 'Percentile']} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <ReferenceLine y={8} stroke="#e2e8f0" strokeDasharray="4 4" label={{ value: 'WHO Median', fontSize: 10, fill: '#94a3b8' }} />
            <Line type="monotone" dataKey="weightKg" stroke="#10b981" strokeWidth={2.5} dot={{ fill: '#10b981', r: 4, strokeWidth: 0 }} activeDot={{ r: 6 }} name="weightKg" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Height + Head Circ Charts */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-700 mb-4">Height Trend (cm)</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="ageMonths" tickFormatter={(v) => `${v}m`} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[60, 80]} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontSize: 12 }}
                formatter={(v: unknown) => [`${v} cm`, 'Height']} />
              <Line type="monotone" dataKey="heightCm" stroke="#3b82f6" strokeWidth={2.5} dot={{ fill: '#3b82f6', r: 4, strokeWidth: 0 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-700 mb-4">Head Circumference (cm)</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="ageMonths" tickFormatter={(v) => `${v}m`} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[40, 48]} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontSize: 12 }}
                formatter={(v: unknown) => [`${v} cm`, 'Head Circumference']} />
              <Line type="monotone" dataKey="headCircumferenceCm" stroke="#7c3aed" strokeWidth={2.5} dot={{ fill: '#7c3aed', r: 4, strokeWidth: 0 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Growth Summary */}
      {summary && (
        <div className="rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50 to-teal-50 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="h-4 w-4 text-emerald-600" />
            <h3 className="text-sm font-bold text-emerald-700">AI Growth Summary</h3>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed">{summary.insight}</p>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { label: 'Weight', value: summary.currentWeight },
              { label: 'Monthly Gain', value: summary.monthlyGain },
              { label: 'WHO Standing', value: summary.whoPercentileText.split(' ')[0] },
              { label: 'Status', value: 'Healthy ✓' },
            ].map(({ label, value }) => (
              <div key={label} className="rounded-xl bg-white/70 p-3 text-center">
                <p className="text-[10px] text-slate-400 font-medium">{label}</p>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
