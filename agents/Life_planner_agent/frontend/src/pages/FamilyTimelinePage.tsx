import { motion } from 'framer-motion';
import { Users, Clock, MapPin } from 'lucide-react';

interface FamilyTimelinePageProps {
  timelineData: Array<{
    id: number;
    title: string;
    description: string | null;
    start: string;
    end: string;
    type: string;
    location: string | null;
    member: string;
    priority: string;
  }>;
  scheduleHealth: number;
}

export default function FamilyTimelinePage({ timelineData, scheduleHealth }: FamilyTimelinePageProps) {
  
  const getMemberStyle = (member: string) => {
    const norm = member.toLowerCase();
    if (norm.includes('father') || norm.includes('dad')) {
      return { bg: 'bg-blue-50 border-blue-200', text: 'text-blue-700 bg-blue-100', dot: 'bg-blue-600' };
    }
    if (norm.includes('mother') || norm.includes('mom')) {
      return { bg: 'bg-rose-50 border-rose-200', text: 'text-rose-700 bg-rose-100', dot: 'bg-rose-600' };
    }
    if (norm.includes('child') || norm.includes('student') || norm.includes('kid')) {
      return { bg: 'bg-amber-50 border-amber-200', text: 'text-amber-700 bg-amber-100', dot: 'bg-amber-600' };
    }
    if (norm.includes('elder') || norm.includes('grand')) {
      return { bg: 'bg-emerald-50 border-emerald-200', text: 'text-emerald-700 bg-emerald-100', dot: 'bg-emerald-600' };
    }
    // Default or Planner
    return { bg: 'bg-purple-50 border-purple-200', text: 'text-purple-700 bg-purple-100', dot: 'bg-purple-600' };
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
          <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Family Schedule</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Consolidated coordinate timeline across all house members</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200/60 shrink-0">
          <span className="text-[11px] font-bold text-slate-500">Schedule Health:</span>
          <span className="text-xs font-extrabold text-indigo-600">{scheduleHealth}%</span>
        </div>
      </div>

      {/* Timeline Layout */}
      <div className="white-card p-8">
        {timelineData.length === 0 ? (
          <div className="py-12 text-center">
            <Users className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-xs text-slate-400 italic">No schedules recorded on the consolidated timeline.</p>
          </div>
        ) : (
          <div className="relative border-l-2 border-slate-200 pl-8 ml-4 space-y-8">
            {timelineData.map((item, idx) => {
              const styles = getMemberStyle(item.member);
              return (
                <div key={idx} className="relative">
                  {/* Timeline Node Dot */}
                  <span className={`absolute -left-[39px] top-1.5 h-4.5 w-4.5 rounded-full border-4 border-white ${styles.dot}`}></span>

                  <div className={`p-5 rounded-xl border transition-all hover:scale-[1.01] ${styles.bg}`}>
                    <div className="flex justify-between items-start gap-4">
                      <div className="space-y-1">
                        <h4 className="text-sm font-extrabold text-slate-800">{item.title}</h4>
                        {item.description && (
                          <p className="text-xs text-slate-600 leading-relaxed font-medium">{item.description}</p>
                        )}
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase shrink-0 ${styles.text}`}>
                        {item.member}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-4 text-[10px] text-slate-400 font-bold uppercase tracking-wider pt-3 mt-3 border-t border-slate-200/50">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        Start: {new Date(item.start).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </span>
                      {item.location && (
                        <span className="flex items-center gap-0.5">
                          <MapPin className="h-3.5 w-3.5" />
                          Loc: {item.location}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}
