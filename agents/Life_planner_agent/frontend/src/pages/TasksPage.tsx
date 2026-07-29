import { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckSquare, Plus, Trash2, Sparkles, Filter, CheckCircle2 } from 'lucide-react';
import type { Task } from '../services/api';

interface TasksPageProps {
  tasks: Task[];
  onAddTask: () => void;
  onToggleStatus: (task: Task) => void;
  onDeleteTask: (id: number) => void;
}

export default function TasksPage({ tasks, onAddTask, onToggleStatus, onDeleteTask }: TasksPageProps) {
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  const filteredTasks = tasks.filter(t => {
    if (filter === 'pending') return t.status !== 'COMPLETED';
    if (filter === 'completed') return t.status === 'COMPLETED';
    return true;
  });

  const getPriorityStyle = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'MEDIUM':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const getCompletionRate = () => {
    if (tasks.length === 0) return 0;
    const completed = tasks.filter(t => t.status === 'COMPLETED').length;
    return Math.round((completed / tasks.length) * 100);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      {/* Top Stats and Filters Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
            <CheckSquare className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Workspace Tasks</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Track execution items and sub-schedules</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Progress meter */}
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200/60 shrink-0">
            <span className="text-[11px] font-bold text-slate-500">Progress:</span>
            <span className="text-xs font-extrabold text-blue-600">{getCompletionRate()}%</span>
            <div className="w-16 bg-slate-200 h-1.5 rounded-full overflow-hidden shrink-0">
              <div className="bg-blue-600 h-full rounded-full transition-all duration-300" style={{ width: `${getCompletionRate()}%` }}></div>
            </div>
          </div>

          <button
            onClick={onAddTask}
            className="px-4 py-2 bg-[#1D4ED8] hover:bg-[#1D4ED8]/95 text-white rounded-xl text-xs font-extrabold flex items-center gap-1 shrink-0 shadow-sm shadow-blue-500/10"
          >
            <Plus className="h-4.5 w-4.5" /> Create Task
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters and AI Tips Column */}
        <div className="space-y-6">
          <div className="white-card p-5 space-y-4">
            <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider flex items-center gap-1">
              <Filter className="h-3.5 w-3.5" /> Filters
            </h4>
            <div className="space-y-1">
              {['all', 'pending', 'completed'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as any)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs font-bold capitalize transition ${
                    filter === f ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {f} Tasks
                </button>
              ))}
            </div>
          </div>

          {/* AI Tasks Insight */}
          <div className="dark-panel p-5 space-y-4 border border-[#1D3A5F]">
            <h4 className="text-xs uppercase font-extrabold text-purple-300 tracking-wider flex items-center gap-1">
              <Sparkles className="h-3.5 w-3.5 text-purple-400" /> AI Task Insights
            </h4>
            <p className="text-[11px] text-slate-300 leading-relaxed font-medium">
              Based on today's events, <strong className="text-yellow-400">Shopping</strong> should be prioritized before 6 PM to avoid conflicting with the evening family schedule slots.
            </p>
          </div>
        </div>

        {/* Tasks List */}
        <div className="lg:col-span-3 white-card p-6">
          <div className="space-y-3">
            {filteredTasks.length === 0 ? (
              <div className="py-12 text-center space-y-2">
                <CheckCircle2 className="h-8 w-8 text-slate-300 mx-auto" />
                <p className="text-xs text-slate-400 italic">No tasks found matching this criteria.</p>
              </div>
            ) : (
              filteredTasks.map((t) => (
                <div 
                  key={t.id} 
                  className={`p-4 rounded-xl border flex items-center justify-between transition-all duration-200 ${
                    t.status === 'COMPLETED' ? 'bg-slate-50/50 border-slate-200' : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={t.status === 'COMPLETED'}
                      onChange={() => onToggleStatus(t)}
                      className="h-4.5 w-4.5 rounded border-slate-300 text-[#1D4ED8] focus:ring-0 cursor-pointer"
                    />
                    <div>
                      <p className={`text-xs font-bold ${t.status === 'COMPLETED' ? 'line-through text-slate-400' : 'text-slate-700'}`}>
                        {t.title}
                      </p>
                      {t.description && (
                        <p className="text-[10px] text-slate-400 leading-normal mt-0.5">{t.description}</p>
                      )}
                      <div className="flex items-center gap-3 text-[9px] text-slate-400 font-bold mt-1 uppercase tracking-wide">
                        <span className={`px-1.5 py-0.5 rounded border font-semibold ${getPriorityStyle(t.priority)}`}>
                          {t.priority}
                        </span>
                        {t.due_date && <span>Due: {t.due_date}</span>}
                      </div>
                    </div>
                  </div>

                  <button 
                    onClick={() => onDeleteTask(t.id)} 
                    className="text-slate-400 hover:text-rose-500 transition p-1.5"
                  >
                    <Trash2 className="h-4.5 w-4.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
