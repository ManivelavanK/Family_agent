import { Clock, Sun, Moon, Sunrise, Sunset, ArrowRight } from 'lucide-react';
import type { CalendarEvent } from '../services/api';

interface TodayPlanCardProps {
  events: CalendarEvent[];
  onViewTimeline: () => void;
}

export default function TodayPlanCard({ events, onViewTimeline }: TodayPlanCardProps) {
  // Group events by time of day
  const categorizeEvent = (event: CalendarEvent) => {
    const hour = new Date(event.start_datetime).getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  };

  const morningEvents = events.filter(e => categorizeEvent(e) === 'morning');
  const afternoonEvents = events.filter(e => categorizeEvent(e) === 'afternoon');
  const eveningEvents = events.filter(e => categorizeEvent(e) === 'evening');
  const nightEvents = events.filter(e => categorizeEvent(e) === 'night');

  const renderTimelineSlot = (
    title: string,
    slotEvents: CalendarEvent[],
    icon: React.ReactNode,
    colorClass: string
  ) => {
    return (
      <div className="flex gap-3 border-l-2 border-slate-100 pl-4 py-1 relative">
        <span className={`absolute -left-[9px] top-1.5 h-4 w-4 rounded-full flex items-center justify-center border-2 border-white text-white ${colorClass}`}>
          {icon}
        </span>
        <div className="space-y-1 w-full">
          <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
            {title}
          </p>
          <div className="space-y-1">
            {slotEvents.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No events scheduled</p>
            ) : (
              slotEvents.map(e => (
                <div key={e.id} className="text-xs font-semibold text-slate-700 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200/50 flex justify-between items-center">
                  <span className="truncate max-w-[150px]">{e.title}</span>
                  <span className="text-[10px] text-slate-400 font-medium shrink-0">
                    {new Date(e.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="white-card p-6 flex flex-col justify-between h-full border border-slate-200">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-extrabold text-slate-800 tracking-tight uppercase flex items-center gap-1.5">
            <Clock className="h-4.5 w-4.5 text-[#1D4ED8]" /> Today's Plan
          </h4>
          <button 
            onClick={onViewTimeline}
            className="text-xs text-[#1D4ED8] font-bold hover:underline flex items-center gap-0.5"
          >
            Full Timeline <ArrowRight className="h-3 w-3" />
          </button>
        </div>

        {/* Timeline segments */}
        <div className="space-y-4 pt-1">
          {renderTimelineSlot(
            "Morning", 
            morningEvents, 
            <Sunrise className="h-2 w-2" />, 
            "bg-[#F59E0B]"
          )}
          {renderTimelineSlot(
            "Afternoon", 
            afternoonEvents, 
            <Sun className="h-2 w-2" />, 
            "bg-[#1D4ED8]"
          )}
          {renderTimelineSlot(
            "Evening", 
            eveningEvents, 
            <Sunset className="h-2 w-2" />, 
            "bg-[#7C3AED]"
          )}
          {renderTimelineSlot(
            "Night", 
            nightEvents, 
            <Moon className="h-2 w-2" />, 
            "bg-[#0B1F33]"
          )}
        </div>
      </div>
    </div>
  );
}
