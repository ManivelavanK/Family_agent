import React, { useEffect, useState } from 'react';
import { HeartPulse, Plus, Thermometer, Pill, AlertCircle, FileText } from 'lucide-react';
import { healthService } from '../services/healthService';
import { HealthLog } from '../types/health';
import { SkeletonCard } from '../components/common/SkeletonLoader';

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: true,
  });
}

export default function HealthLogs() {
  const [logs, setLogs] = useState<HealthLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    healthService.getHealthLogs().then((l) => { setLogs(l); setLoading(false); });
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
          <h1 className="text-xl font-bold text-slate-900">Health Logs</h1>
          <p className="text-sm text-slate-500 mt-0.5">Complete health history for Aarav</p>
        </div>
        <button className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-violet-700 transition-colors">
          <Plus className="h-4 w-4" />
          Add Record
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: Thermometer, label: 'Avg Temp', value: '36.9°C', sub: 'Last 7 days', bg: 'bg-rose-50', color: 'text-rose-600' },
          { icon: Pill,        label: 'Medicines', value: '2',     sub: 'Active',       bg: 'bg-violet-50', color: 'text-violet-600' },
          { icon: AlertCircle, label: 'Symptoms',  value: '1',     sub: 'This week',    bg: 'bg-amber-50',  color: 'text-amber-600' },
        ].map(({ icon: Icon, label, value, sub, bg, color }) => (
          <div key={label} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm text-center">
            <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl ${bg}`}>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="text-xs text-slate-400 font-medium">{label}</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{value}</p>
            <p className="text-xs text-slate-400 mt-0.5">{sub}</p>
          </div>
        ))}
      </div>

      {/* Log List */}
      {logs.length === 0 ? (
        <div className="flex flex-col items-center py-12 text-center rounded-2xl border border-slate-100 bg-white">
          <HeartPulse className="h-12 w-12 text-slate-200 mb-3" />
          <p className="text-sm font-medium text-slate-500">No health records yet.</p>
          <p className="text-xs text-slate-400 mt-1">Add records to build Aarav's health history.</p>
          <button className="mt-4 flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 transition-colors">
            <Plus className="h-4 w-4" />
            Add Record
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {logs.map((log) => (
            <div key={log.id} className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-rose-50">
                  <HeartPulse className="h-5 w-5 text-rose-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs text-slate-400 font-medium">{formatDateTime(log.timestamp)}</p>
                    {log.symptoms.some(s => s !== 'None') && (
                      <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700">Symptoms</span>
                    )}
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-3">
                    {log.temperature && (
                      <div>
                        <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">Temperature</p>
                        <p className={`text-sm font-bold ${log.temperature > 37.5 ? 'text-rose-600' : 'text-slate-800'}`}>
                          {log.temperature}°C
                          {log.temperature > 37.5 && ' ⚠'}
                        </p>
                      </div>
                    )}
                    {log.weight && (
                      <div>
                        <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">Weight</p>
                        <p className="text-sm font-bold text-slate-800">{log.weight} kg</p>
                      </div>
                    )}
                    {log.medicine && (
                      <div>
                        <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">Medicine</p>
                        <p className="text-sm font-bold text-violet-700">{log.medicine}</p>
                      </div>
                    )}
                    {log.symptoms.some((s) => s !== 'None') && (
                      <div className="col-span-2 sm:col-span-3">
                        <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wide mb-1">Symptoms</p>
                        <div className="flex flex-wrap gap-1.5">
                          {log.symptoms.map((s) => (
                            <span key={s} className="rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700 border border-amber-100">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  {log.doctorNotes && (
                    <div className="mt-3 flex items-start gap-2 rounded-xl bg-slate-50 p-3">
                      <FileText className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
                      <p className="text-xs text-slate-600 italic">{log.doctorNotes}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
