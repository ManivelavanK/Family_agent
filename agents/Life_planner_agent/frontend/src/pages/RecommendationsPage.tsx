import { motion } from 'framer-motion';
import { Sparkles, Check } from 'lucide-react';
import type { Recommendation } from '../services/api';

interface RecommendationsPageProps {
  recommendations: Recommendation[];
}

export default function RecommendationsPage({ recommendations }: RecommendationsPageProps) {
  
  const getRecTagStyle = (type: string) => {
    switch (type) {
      case 'CONFLICT':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'GOAL_DEADLINE':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-50 text-amber-600">
            <Sparkles className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Conflict Resolver</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Proactive schedule rearrangements and timing recommendations</p>
          </div>
        </div>
      </div>

      {/* List of recommendations */}
      <div className="white-card p-6 space-y-4">
        {recommendations.length === 0 ? (
          <div className="py-12 text-center space-y-2">
            <Check className="h-8 w-8 text-emerald-500 mx-auto" />
            <p className="text-sm font-semibold text-slate-700">All schedules clear!</p>
            <p className="text-xs text-slate-400">No conflicts or optimizations detected at this time.</p>
          </div>
        ) : (
          recommendations.map((r, idx) => (
            <div 
              key={idx} 
              className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition duration-200"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded border text-[9px] font-extrabold tracking-wide uppercase ${getRecTagStyle(r.type)}`}>
                    {r.type}
                  </span>
                </div>
                <h4 className="text-xs font-extrabold text-slate-800">{r.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed font-medium">{r.suggestion}</p>
              </div>

              <button
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-extrabold transition shadow-sm shrink-0"
                onClick={() => alert('Conflict resolved successfully')}
              >
                Apply Change
              </button>
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
}
