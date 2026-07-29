import { 
  CheckSquare, 
  Users, 
  Sparkles, 
  CalendarDays, 
  Calendar, 
  BellRing,
  ChevronRight
} from 'lucide-react';

interface QuickActionsProps {
  onCreateTask: () => void;
  onScheduleMeeting: () => void;
  onAiPlanDay: () => void;
  onGenerateWeeklyPlan: () => void;
  onViewCalendar: () => void;
  onAddReminder: () => void;
}

export default function QuickActions({
  onCreateTask,
  onScheduleMeeting,
  onAiPlanDay,
  onGenerateWeeklyPlan,
  onViewCalendar,
  onAddReminder
}: QuickActionsProps) {
  const actions = [
    { label: 'Create Task', onClick: onCreateTask, icon: CheckSquare, color: 'text-[#1D4ED8] bg-[#1D4ED8]/5' },
    { label: 'Schedule Meeting', onClick: onScheduleMeeting, icon: Users, color: 'text-[#7C3AED] bg-[#7C3AED]/5' },
    { label: 'AI Plan My Day', onClick: onAiPlanDay, icon: Sparkles, color: 'text-[#F59E0B] bg-[#F59E0B]/5' },
    { label: 'Generate Weekly Plan', onClick: onGenerateWeeklyPlan, icon: CalendarDays, color: 'text-[#10B981] bg-[#10B981]/5' },
    { label: 'View Calendar', onClick: onViewCalendar, icon: Calendar, color: 'text-sky-500 bg-sky-500/5' },
    { label: 'Add Reminder', onClick: onAddReminder, icon: BellRing, color: 'text-[#EF4444] bg-[#EF4444]/5' },
  ];

  return (
    <div className="white-card p-6 flex flex-col justify-between h-full border border-slate-200">
      <div className="space-y-4">
        <h4 className="text-xs uppercase font-extrabold tracking-wider text-slate-400">Quick Actions</h4>
        <div className="space-y-2">
          {actions.map((act, idx) => {
            const Icon = act.icon;
            return (
              <button
                key={idx}
                onClick={act.onClick}
                className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-100 transition-all duration-200 group text-left"
              >
                <div className="flex items-center gap-3">
                  <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${act.color}`}>
                    <Icon className="h-4.5 w-4.5" />
                  </div>
                  <span className="text-xs font-bold text-slate-700 group-hover:text-[#1D4ED8] transition-colors">{act.label}</span>
                </div>
                <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-[#1D4ED8] group-hover:translate-x-0.5 transition-all" />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
