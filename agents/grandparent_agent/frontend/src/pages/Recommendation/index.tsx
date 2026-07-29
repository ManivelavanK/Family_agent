import React, { useEffect, useState } from 'react';
import { recommendationService } from '../../services/recommendationService';
import { Recommendation as RecType } from '../../types';
import { Sparkles, Heart, Apple, Droplet, Clock, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import StatusBadge from '../../components/common/StatusBadge';

export const Recommendation: React.FC = () => {
  const [recs, setRecs] = useState<RecType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecs();
  }, []);

  const loadRecs = async () => {
    try {
      const data = await recommendationService.getRecommendations();
      setRecs(data);
    } catch (e) {
      toast.error("Failed to load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (cat: string) => {
    switch (cat) {
      case 'Diet': return Apple;
      case 'Exercise': return Heart;
      case 'Hydration': return Droplet;
      case 'Sleep': return Clock;
      case 'Health Warning': return AlertTriangle;
      default: return Sparkles;
    }
  };

  const getColor = (prio: string) => {
    if (prio === 'High') return 'border-rose-200 bg-rose-50/20 text-rose-700';
    if (prio === 'Medium') return 'border-amber-200 bg-amber-50/20 text-amber-700';
    return 'border-sky-200 bg-sky-50/20 text-sky-700';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-sky-50 to-emerald-50 border border-sky-100 p-6 rounded-2xl flex items-start gap-4">
        <div className="p-3 bg-sky-500 text-white rounded-xl">
          <Sparkles className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-800">AI Health Recommendations</h3>
          <p className="text-sm font-semibold text-slate-500">Personalized daily guidance dynamically updated based on your vitals logs, activity, and dietary data.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {recs.map((r) => {
          const Icon = getIcon(r.category);
          return (
            <div key={r.id} className={`p-6 rounded-2xl border ${getColor(r.priority)} flex flex-col justify-between`}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 bg-white border rounded-full">
                    {r.category}
                  </span>
                  <StatusBadge status={r.priority} />
                </div>
                <h4 className="text-lg font-black text-slate-800 leading-tight">{r.title}</h4>
                <p className="text-base font-semibold text-slate-600 leading-relaxed">{r.content}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2 text-xs font-semibold text-slate-400">
                <Icon className="h-4 w-4" />
                <span>Reason: {r.reason}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default Recommendation;
