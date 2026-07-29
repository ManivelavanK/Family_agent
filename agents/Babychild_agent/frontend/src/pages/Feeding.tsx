import React, { useEffect, useState } from 'react';
import { Milk, Plus, Sparkles, Clock, Droplets, Info } from 'lucide-react';
import { feedingService } from '../services/feedingService';
import { FeedingRecord, FeedingAnalysis, FeedingType } from '../types/feeding';
import { SkeletonCard } from '../components/common/SkeletonLoader';

const TYPE_CONFIG: Record<FeedingType, { color: string; bg: string; icon: string }> = {
  'Bottle':        { color: 'text-blue-700',   bg: 'bg-blue-100',   icon: '🍼' },
  'Breastfeeding': { color: 'text-pink-700',   bg: 'bg-pink-100',   icon: '🤱' },
  'Solid Food':    { color: 'text-amber-700',  bg: 'bg-amber-100',  icon: '🥣' },
  'Water':         { color: 'text-cyan-700',   bg: 'bg-cyan-100',   icon: '💧' },
  'Formula':       { color: 'text-violet-700', bg: 'bg-violet-100', icon: '🧪' },
};

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

export default function Feeding() {
  const [history, setHistory] = useState<FeedingRecord[]>([]);
  const [analysis, setAnalysis] = useState<FeedingAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([feedingService.getFeedingHistory(), feedingService.getFeedingAnalysis()]).then(
      ([hist, anal]) => {
        setHistory(hist);
        setAnalysis(anal);
        setLoading(false);
      }
    );
  }, []);

  // Group by date label
  const grouped = history.reduce<Record<string, FeedingRecord[]>>((acc, r) => {
    const key = formatDate(r.time);
    (acc[key] = acc[key] || []).push(r);
    return acc;
  }, {});

  if (loading) return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Feeding Tracker</h1>
          <p className="text-sm text-slate-500 mt-0.5">Log and monitor Aarav's feeding schedule</p>
        </div>
        <button className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-violet-700 transition-colors">
          <Plus className="h-4 w-4" />
          Log Feeding
        </button>
      </div>

      {/* AI Prediction Card */}
      {analysis && (
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 p-5 text-white shadow-lg">
          <div className="pointer-events-none absolute -top-6 -right-6 h-32 w-32 rounded-full bg-white/10 blur-xl" />
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-bold text-white/80 uppercase tracking-wide mb-2">AI Feeding Analysis</h3>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { label: 'Avg Interval', value: analysis.averageFeedingInterval },
                  { label: 'Next Predicted Feed', value: analysis.predictedNextFeed },
                  { label: 'Hydration Status', value: analysis.hydrationStatus },
                  { label: 'AI Confidence', value: analysis.confidence },
                ].map(({ label, value }) => (
                  <div key={label} className="rounded-xl bg-white/15 p-3">
                    <p className="text-[10px] font-medium text-white/70 mb-1">{label}</p>
                    <p className="text-base font-bold text-white leading-none">{value}</p>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2">
                <Info className="h-4 w-4 text-white/70 shrink-0" />
                <p className="text-xs text-white/80">{analysis.recommendation}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: Milk, label: "Today's Feedings", value: '8', sub: 'On Track', bg: 'bg-blue-50', color: 'text-blue-600' },
          { icon: Clock, label: 'Next Feed In', value: '~2h', sub: 'Predicted', bg: 'bg-violet-50', color: 'text-violet-600' },
          { icon: Droplets, label: 'Hydration', value: 'Normal', sub: analysis?.hydrationStatus, bg: 'bg-cyan-50', color: 'text-cyan-600' },
        ].map(({ icon: Icon, label, value, sub, bg, color }) => (
          <div key={label} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm text-center">
            <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl ${bg}`}>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="text-xs text-slate-400">{label}</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{value}</p>
            {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
          </div>
        ))}
      </div>

      {/* Feeding History */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-700 mb-4">Feeding History</h3>

        {Object.keys(grouped).length === 0 ? (
          <div className="flex flex-col items-center py-12 text-center">
            <Milk className="h-12 w-12 text-slate-200 mb-3" />
            <p className="text-sm font-medium text-slate-500">No feeding records yet.</p>
            <p className="text-xs text-slate-400 mt-1">Start logging feedings to allow Baby Agent to predict feeding schedules.</p>
            <button className="mt-4 flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 transition-colors">
              <Plus className="h-4 w-4" />
              Add Feeding
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(grouped).map(([date, records]) => (
              <div key={date}>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">{date}</p>
                <div className="space-y-2">
                  {records.map((r) => {
                    const cfg = TYPE_CONFIG[r.type];
                    return (
                      <div key={r.id} className="flex items-center gap-4 rounded-xl border border-slate-50 p-4 hover:bg-slate-50 transition-colors">
                        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg ${cfg.bg}`}>
                          {cfg.icon}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-semibold ${cfg.color}`}>{r.type}</span>
                            {r.notes && <span className="text-xs text-slate-400">· {r.notes}</span>}
                          </div>
                          <p className="text-xs text-slate-400 mt-0.5">
                            {formatTime(r.time)} · {r.quantity}
                            {r.duration ? ` · ${r.duration}` : ''}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
