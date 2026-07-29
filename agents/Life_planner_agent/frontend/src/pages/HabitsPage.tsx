import { motion } from 'framer-motion';
import { Activity, Plus, Trash2, Flame, Award } from 'lucide-react';
import type { Habit } from '../services/api';

interface HabitsPageProps {
  habits: Habit[];
  onAddHabit: () => void;
  onLogHabit: (habitId: number, completed: boolean) => void;
  onDeleteHabit: (habitId: number) => void;
}

export default function HabitsPage({ habits, onAddHabit, onLogHabit, onDeleteHabit }: HabitsPageProps) {
  
  // Renders a GitHub-like consistency grid representing the last 21 days
  const renderConsistencyGrid = (habit: Habit) => {
    const today = new Date();
    const dots = [];
    
    for (let i = 20; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const logged = habit.logs?.some(l => l.date === dateStr && l.completed);
      
      dots.push(
        <div
          key={i}
          title={`${dateStr}: ${logged ? 'Completed' : 'Not completed'}`}
          className={`h-3 w-3 rounded-sm border ${
            logged 
              ? 'bg-emerald-500 border-emerald-600 shadow-[0_0_4px_rgba(16,185,129,0.3)]' 
              : 'bg-slate-100 border-slate-200'
          }`}
        />
      );
    }
    
    return (
      <div className="space-y-1.5">
        <p className="text-[9px] uppercase font-extrabold text-slate-400 tracking-wider">Consistency (Last 21 Days)</p>
        <div className="flex flex-wrap gap-1">
          {dots}
        </div>
      </div>
    );
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
          <div className="p-2 rounded-xl bg-rose-50 text-rose-600">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Habits Consistency</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Build daily routines and track completion streaks</p>
          </div>
        </div>

        <button
          onClick={onAddHabit}
          className="px-4 py-2 bg-[#1D4ED8] hover:bg-[#1D4ED8]/95 text-white rounded-xl text-xs font-extrabold flex items-center gap-1 shrink-0 shadow-sm"
        >
          <Plus className="h-4.5 w-4.5" /> New Habit
        </button>
      </div>

      {/* Habits Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {habits.length === 0 ? (
          <p className="text-xs text-slate-400 italic py-12 text-center col-span-full">No habits tracked yet.</p>
        ) : (
          habits.map((h) => {
            const todayStr = new Date().toISOString().split('T')[0];
            const isCompletedToday = h.logs?.some(l => l.date === todayStr && l.completed);

            return (
              <div 
                key={h.id} 
                className="white-card p-6 flex flex-col justify-between space-y-4 hover:shadow-lg transition-all duration-300"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2">
                    <span className="px-2 py-0.5 rounded border bg-slate-50 text-slate-600 border-slate-200 text-[9px] font-extrabold uppercase tracking-wide">
                      {h.category}
                    </span>
                    <button 
                      onClick={() => onDeleteHabit(h.id)} 
                      className="text-slate-400 hover:text-rose-500 transition p-0.5"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <h4 className="font-extrabold text-slate-800 text-sm leading-snug">{h.title}</h4>

                  {/* Streak displays */}
                  <div className="flex items-center gap-4 text-xs font-bold text-slate-500 pt-1">
                    <div className="flex items-center gap-1 text-[#F59E0B]">
                      <Flame className="h-4.5 w-4.5 fill-[#F59E0B]" />
                      <span>{h.streak} Streak</span>
                    </div>
                    <div className="flex items-center gap-1 text-slate-400">
                      <Award className="h-4.5 w-4.5" />
                      <span>Max {h.max_streak}</span>
                    </div>
                  </div>
                </div>

                {/* Consistency Grid */}
                {renderConsistencyGrid(h)}

                {/* Today Log Action */}
                <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200/60 mt-2">
                  <span className="text-xs font-bold text-slate-600">Completed Today</span>
                  <input
                    type="checkbox"
                    checked={isCompletedToday}
                    onChange={(e) => onLogHabit(h.id, e.target.checked)}
                    className="h-5 w-5 rounded border-slate-300 text-[#1D4ED8] focus:ring-0 cursor-pointer"
                  />
                </div>
              </div>
            );
          })
        )}
      </div>
    </motion.div>
  );
}
