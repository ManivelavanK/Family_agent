import React, { useEffect, useState } from 'react';
import { Syringe, CheckCircle, Clock, AlertTriangle, MapPin, User } from 'lucide-react';
import { vaccinationService } from '../services/vaccinationService';
import { Vaccination } from '../types/vaccination';
import { SkeletonCard } from '../components/common/SkeletonLoader';

const STATUS_CONFIG = {
  Completed: { icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50', badge: 'bg-emerald-100 text-emerald-700', border: 'border-emerald-100' },
  Upcoming:  { icon: Clock,       color: 'text-amber-600',   bg: 'bg-amber-50',   badge: 'bg-amber-100 text-amber-700',   border: 'border-amber-100'   },
  Overdue:   { icon: AlertTriangle, color: 'text-rose-600', bg: 'bg-rose-50',    badge: 'bg-rose-100 text-rose-700',     border: 'border-rose-100'    },
};

function daysUntil(dateStr: string) {
  return Math.ceil((new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
}

export default function Vaccinations() {
  const [vaccinations, setVaccinations] = useState<Vaccination[]>([]);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState<string | null>(null);

  useEffect(() => {
    vaccinationService.getVaccinations().then((v) => { setVaccinations(v); setLoading(false); });
  }, []);

  const handleMark = async (id: string) => {
    setMarking(id);
    await vaccinationService.markCompleted(id);
    setVaccinations((prev) =>
      prev.map((v) => v.id === id ? { ...v, status: 'Completed', completedDate: new Date().toISOString() } : v)
    );
    setMarking(null);
  };

  const completed = vaccinations.filter((v) => v.status === 'Completed');
  const upcoming  = vaccinations.filter((v) => v.status === 'Upcoming');
  const overdue   = vaccinations.filter((v) => v.status === 'Overdue');

  if (loading) return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Vaccination Schedule</h1>
        <p className="text-sm text-slate-500 mt-0.5">Track completed and upcoming vaccines for Aarav</p>
      </div>

      {/* Summary Badges */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Completed', count: completed.length, color: 'text-emerald-700 bg-emerald-50 border-emerald-100' },
          { label: 'Upcoming',  count: upcoming.length,  color: 'text-amber-700 bg-amber-50 border-amber-100'      },
          { label: 'Overdue',   count: overdue.length,   color: 'text-rose-700 bg-rose-50 border-rose-100'         },
        ].map(({ label, count, color }) => (
          <div key={label} className={`flex flex-col items-center rounded-2xl border p-4 shadow-sm ${color}`}>
            <span className="text-2xl font-bold">{count}</span>
            <span className="text-xs font-medium mt-1">{label}</span>
          </div>
        ))}
      </div>

      {/* Upcoming Alert Banner */}
      {upcoming.length > 0 && (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4">
          <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">Upcoming Vaccination</p>
            <p className="text-xs text-amber-600 mt-0.5">
              <strong>{upcoming[0].name}</strong> is due in <strong>{daysUntil(upcoming[0].dueDate)} days</strong>.
              Schedule an appointment with {upcoming[0].doctor} at {upcoming[0].hospital}.
            </p>
          </div>
        </div>
      )}

      {/* Vaccination List */}
      {[
        { label: 'Upcoming', items: upcoming },
        { label: 'Overdue', items: overdue },
        { label: 'Completed', items: completed },
      ].map(({ label, items }) => items.length > 0 && (
        <div key={label}>
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-3">{label}</h3>
          <div className="space-y-3">
            {items.map((v) => {
              const cfg = STATUS_CONFIG[v.status];
              const StatusIcon = cfg.icon;
              return (
                <div key={v.id} className={`rounded-2xl border ${cfg.border} bg-white p-5 shadow-sm`}>
                  <div className="flex items-start gap-4">
                    <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${cfg.bg}`}>
                      <Syringe className={`h-5 w-5 ${cfg.color}`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="text-sm font-bold text-slate-800">{v.name}</h4>
                        <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${cfg.badge}`}>
                          {v.status}
                        </span>
                      </div>
                      <div className="mt-2 space-y-1">
                        {v.status !== 'Completed' ? (
                          <p className="flex items-center gap-1.5 text-xs text-slate-500">
                            <Clock className="h-3.5 w-3.5" />
                            Due: {new Date(v.dueDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                            {' '}({daysUntil(v.dueDate)} days)
                          </p>
                        ) : (
                          <p className="flex items-center gap-1.5 text-xs text-emerald-600">
                            <CheckCircle className="h-3.5 w-3.5" />
                            Completed: {v.completedDate && new Date(v.completedDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                          </p>
                        )}
                        <p className="flex items-center gap-1.5 text-xs text-slate-400">
                          <User className="h-3.5 w-3.5" />
                          {v.doctor}
                        </p>
                        <p className="flex items-center gap-1.5 text-xs text-slate-400">
                          <MapPin className="h-3.5 w-3.5" />
                          {v.hospital}
                        </p>
                        {v.notes && <p className="text-xs text-slate-400 italic mt-1">{v.notes}</p>}
                      </div>
                    </div>
                  </div>
                  {v.status !== 'Completed' && (
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => handleMark(v.id)}
                        disabled={marking === v.id}
                        className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors disabled:opacity-60"
                      >
                        <CheckCircle className="h-3.5 w-3.5" />
                        {marking === v.id ? 'Marking...' : 'Mark Completed'}
                      </button>
                      <button className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
                        Set Reminder
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
