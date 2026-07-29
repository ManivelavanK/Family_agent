import { motion } from 'framer-motion';
import { Target, Plus, Trash2, Zap, Calendar } from 'lucide-react';
import type { Goal } from '../services/api';

interface GoalsPageProps {
  goals: Goal[];
  onAddGoal: () => void;
  onUpdateGoal: (id: number, currentProgress: number) => void;
  onDeleteGoal: (id: number) => void;
}

export default function GoalsPage({ goals, onAddGoal, onUpdateGoal, onDeleteGoal }: GoalsPageProps) {
  
  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'ACADEMIC':
        return 'bg-blue-50 text-blue-700 border-blue-100';
      case 'FINANCIAL':
        return 'bg-emerald-50 text-emerald-700 border-emerald-100';
      case 'HEALTH':
        return 'bg-rose-50 text-rose-700 border-rose-100';
      case 'HOUSEHOLD':
        return 'bg-amber-50 text-amber-700 border-amber-100';
      default:
        return 'bg-purple-50 text-purple-700 border-purple-100';
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
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
            <Target className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Goal Predictions</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Align accomplishments and forecast completion times</p>
          </div>
        </div>

        <button
          onClick={onAddGoal}
          className="px-4 py-2 bg-[#1D4ED8] hover:bg-[#1D4ED8]/95 text-white rounded-xl text-xs font-extrabold flex items-center gap-1 shrink-0 shadow-sm"
        >
          <Plus className="h-4.5 w-4.5" /> Add Goal
        </button>
      </div>

      {/* Goal Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.length === 0 ? (
          <p className="text-xs text-slate-400 italic py-12 text-center col-span-full">No goals have been added yet.</p>
        ) : (
          goals.map((g) => {
            const daysLeft = g.progress < 100 ? Math.ceil((100 - g.progress) / 2.5) : 0;
            return (
              <div 
                key={g.id} 
                className="white-card p-6 flex flex-col justify-between space-y-4 hover:shadow-lg transition-all duration-300"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2">
                    <span className={`px-2 py-0.5 rounded border text-[9px] font-extrabold uppercase tracking-wide ${getCategoryColor(g.category)}`}>
                      {g.category}
                    </span>
                    <button 
                      onClick={() => onDeleteGoal(g.id)} 
                      className="text-slate-400 hover:text-rose-500 transition p-0.5"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  
                  <h4 className="font-extrabold text-slate-800 text-sm leading-snug">{g.title}</h4>
                  {g.description && (
                    <p className="text-xs text-slate-500 leading-relaxed font-medium">{g.description}</p>
                  )}
                </div>

                {/* Progress bar and AI Predict Info */}
                <div className="space-y-3.5 pt-2">
                  {g.progress < 100 && (
                    <div className="p-2.5 rounded-xl bg-purple-50/50 border border-purple-100 text-[10px] text-purple-700 flex items-center gap-1.5 font-bold">
                      <Zap className="h-3.5 w-3.5 text-amber-500 animate-pulse" />
                      <span>AI prediction: Target achievement in ~<strong>{daysLeft} days</strong></span>
                    </div>
                  )}

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs font-bold">
                      <span className="text-slate-500">Progress</span>
                      <span className="text-blue-600">{Math.round(g.progress)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <motion.div 
                        className="bg-gradient-to-r from-blue-600 to-indigo-500 h-full rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${g.progress}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                      />
                    </div>
                  </div>

                  {g.ai_recommendation && (
                    <div className="p-2.5 rounded-xl bg-blue-50/40 border border-blue-100 text-[10px] text-blue-700 font-medium">
                      <strong className="text-blue-800 font-bold">AI Tip:</strong> {g.ai_recommendation}
                    </div>
                  )}

                  {g.deadline && (
                    <div className="flex items-center gap-1 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>Target: {new Date(g.deadline).toLocaleDateString()}</span>
                    </div>
                  )}

                  {g.progress < 100 && (
                    <button
                      onClick={() => onUpdateGoal(g.id, g.progress)}
                      className="w-full py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-colors"
                    >
                      Bump Progress (+15%)
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </motion.div>
  );
}
