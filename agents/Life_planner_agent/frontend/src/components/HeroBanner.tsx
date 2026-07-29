import { Sparkles, Calendar, CheckSquare, Flame } from 'lucide-react';

interface HeroBannerProps {
  userName: string;
  scheduleHealth: number;
  plannerScore: number;
  eventsCount: number;
  tasksCount: number;
  streakCount: number;
  aiBriefSummary: string;
  onOpenAiPlanner: () => void;
}

export default function HeroBanner({
  userName,
  scheduleHealth,
  plannerScore,
  eventsCount,
  tasksCount,
  streakCount,
  aiBriefSummary,
  onOpenAiPlanner
}: HeroBannerProps) {
  return (
    <div className="dark-panel p-8 relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shadow-xl">
      {/* Sparkle background elements */}
      <div className="absolute right-0 top-0 w-80 h-80 bg-[#1D4ED8]/10 rounded-full blur-3xl -z-0"></div>
      <div className="absolute left-1/3 bottom-0 w-48 h-48 bg-[#7C3AED]/10 rounded-full blur-3xl -z-0"></div>

      <div className="space-y-4 z-10 max-w-2xl">
        <div className="space-y-1">
          <h2 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            Good Morning 👋 <span className="bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">{userName}</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed font-medium">
            {aiBriefSummary}
          </p>
        </div>

        {/* Small badge summary metrics */}
        <div className="flex flex-wrap gap-3 pt-2">
          <div className="px-3.5 py-1.5 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2 text-xs font-semibold text-slate-200">
            <span className="h-2 w-2 rounded-full bg-[#10B981]"></span>
            Schedule Health: <strong className="text-[#10B981]">{scheduleHealth}%</strong>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2 text-xs font-semibold text-slate-200">
            <span className="h-2 w-2 rounded-full bg-[#7C3AED]"></span>
            Planner Score: <strong className="text-[#7C3AED]">{plannerScore}</strong>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2 text-xs text-slate-300">
            <Calendar className="h-3.5 w-3.5 text-indigo-400" />
            <span>{eventsCount} Events Today</span>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2 text-xs text-slate-300">
            <CheckSquare className="h-3.5 w-3.5 text-indigo-400" />
            <span>{tasksCount} Tasks Pending</span>
          </div>
        </div>
      </div>

      {/* Right side: Streak badge & action button */}
      <div className="flex flex-col items-end gap-3 z-10 shrink-0 self-stretch justify-between">
        {/* Planner Streak Badge */}
        <div className="px-4 py-2 rounded-2xl bg-gradient-to-r from-[#F59E0B]/20 to-[#EF4444]/10 border border-[#F59E0B]/30 flex items-center gap-2 shadow-inner self-end">
          <Flame className="h-5 w-5 text-[#F59E0B] fill-[#F59E0B] animate-pulse" />
          <div className="text-right">
            <p className="text-[10px] text-[#F59E0B] uppercase font-bold tracking-wider">Planner Streak</p>
            <p className="text-md font-extrabold text-white leading-none">{streakCount} Days</p>
          </div>
        </div>

        <button 
          onClick={onOpenAiPlanner}
          className="w-full md:w-auto px-5 py-3 rounded-xl bg-[#1D4ED8] hover:bg-[#1D4ED8]/90 text-white font-semibold text-sm flex items-center justify-center gap-2 transition active:scale-95 border border-white/10 shadow-lg shadow-[#1D4ED8]/25"
        >
          <Sparkles className="h-4 w-4" /> Open AI Planner
        </button>
      </div>
    </div>
  );
}
