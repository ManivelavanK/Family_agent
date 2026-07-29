import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar as CalendarIcon, Clock, Plus, Trash2, MapPin } from 'lucide-react';
import type { CalendarEvent } from '../services/api';

interface CalendarPageProps {
  events: CalendarEvent[];
  onAddEvent: () => void;
  onDeleteEvent: (id: number) => void;
}

type ViewMode = 'month' | 'week' | 'day' | 'agenda';

export default function CalendarPage({ events, onAddEvent, onDeleteEvent }: CalendarPageProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('month');
  const [selectedDay, setSelectedDay] = useState<number>(new Date().getDate());

  const daysInJuly = 31;
  const currentMonthName = 'July 2026';

  const getDayEvents = (dayNum: number) => {
    return events.filter(e => {
      const date = new Date(e.start_datetime);
      return date.getDate() === dayNum;
    });
  };

  const getHeatmapColor = (dayNum: number) => {
    const count = getDayEvents(dayNum).length;
    if (count === 0) return 'bg-white text-slate-700 hover:bg-slate-50 border-slate-200';
    if (count === 1) return 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100/50';
    if (count === 2) return 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100/50';
    return 'bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100/50';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      {/* Calendar Header with Toggles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
            <CalendarIcon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">{currentMonthName}</h3>
            <p className="text-[11px] text-slate-400 font-semibold">KinNest Interactive Scheduler</p>
          </div>
        </div>

        {/* View mode buttons */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="bg-slate-100 p-1 rounded-xl flex gap-1 text-xs font-bold text-slate-600 w-full sm:w-auto justify-between">
            {(['month', 'week', 'day', 'agenda'] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                  viewMode === mode ? 'bg-white text-slate-800 shadow-sm' : 'hover:text-slate-800'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          <button
            onClick={onAddEvent}
            className="px-3.5 py-2 bg-[#1D4ED8] hover:bg-[#1D4ED8]/95 text-white rounded-xl text-xs font-bold flex items-center gap-1 shrink-0 shadow-sm"
          >
            <Plus className="h-4 w-4" /> Add
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar details */}
        <div className="white-card p-5 space-y-4">
          <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider">
            Day Schedule (July {selectedDay})
          </h4>
          <div className="space-y-3">
            {getDayEvents(selectedDay).length === 0 ? (
              <p className="text-xs text-slate-400 italic py-6 text-center">No activities scheduled for this day.</p>
            ) : (
              getDayEvents(selectedDay).map((e) => (
                <div key={e.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/60 space-y-2 hover:border-[#1D4ED8]/30 transition group relative">
                  <div className="flex justify-between items-start gap-2">
                    <p className="text-xs font-bold text-slate-800">{e.title}</p>
                    <button
                      onClick={() => onDeleteEvent(e.id)}
                      className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-500 transition shrink-0"
                    >
                      <Trash2 className="h-4.5 w-4.5" />
                    </button>
                  </div>
                  {e.description && <p className="text-[11px] text-slate-500 leading-normal">{e.description}</p>}
                  <div className="flex items-center gap-2 text-[10px] text-slate-400 font-semibold pt-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>{new Date(e.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    {e.location && (
                      <span className="flex items-center gap-0.5 ml-2">
                        <MapPin className="h-3 w-3" /> {e.location}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Calendar Body */}
        <div className="lg:col-span-3 white-card p-6 space-y-6">
          {viewMode === 'month' && (
            <div>
              {/* Days of week */}
              <div className="grid grid-cols-7 gap-2 text-center text-[10px] uppercase tracking-wider font-extrabold text-slate-400 mb-3">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => <span key={d}>{d}</span>)}
              </div>

              {/* Days Grid */}
              <div className="grid grid-cols-7 gap-2.5">
                {Array.from({ length: daysInJuly }, (_, i) => {
                  const dayNum = i + 1;
                  const dayEvents = getDayEvents(dayNum);
                  const isSelected = selectedDay === dayNum;
                  return (
                    <button
                      key={dayNum}
                      onClick={() => setSelectedDay(dayNum)}
                      className={`h-20 p-2 border rounded-xl flex flex-col justify-between items-start transition-all ${getHeatmapColor(dayNum)} ${
                        isSelected ? 'ring-2 ring-[#1D4ED8] ring-offset-2 scale-[1.02] font-bold' : ''
                      }`}
                    >
                      <span className="text-xs font-bold">{dayNum}</span>
                      {dayEvents.length > 0 && (
                        <div className="w-full text-left truncate">
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-black/5 block truncate">
                            {dayEvents[0].title}
                          </span>
                          {dayEvents.length > 1 && (
                            <span className="text-[8px] text-slate-400 font-semibold block mt-0.5">
                              +{dayEvents.length - 1} more
                            </span>
                          )}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {viewMode !== 'month' && (
            <div className="py-12 text-center space-y-3">
              <CalendarIcon className="h-8 w-8 text-slate-300 mx-auto" />
              <p className="text-sm font-semibold text-slate-700">Detailed {viewMode} scheduler simulation</p>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">Toggle back to month view to explore full daily scheduling heatmaps and add tasks.</p>
              <button 
                onClick={() => setViewMode('month')} 
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Go to Month View
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
