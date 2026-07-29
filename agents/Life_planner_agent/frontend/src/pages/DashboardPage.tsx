import { motion } from 'framer-motion';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip
} from 'recharts';
import { Calendar, CheckSquare, Target, Activity, Users, TrendingUp } from 'lucide-react';
import type { Goal, Habit, DigitalTwin, CalendarEvent, Task } from '../services/api';
import HeroBanner from '../components/HeroBanner';
import AIDailyBrief from '../components/AIDailyBrief';
import TodayPlanCard from '../components/TodayPlanCard';
import QuickActions from '../components/QuickActions';

interface DashboardPageProps {
  goals: Goal[];
  habits: Habit[];
  digitalTwin: DigitalTwin | null;
  events: CalendarEvent[];
  tasks: Task[];
  scheduleHealth: number;
  onNavigate: (tab: string) => void;
  onAddTask: () => void;
  onAddEvent: () => void;
}

export default function DashboardPage({
  goals,
  habits,
  digitalTwin,
  events,
  tasks,
  scheduleHealth,
  onNavigate,
  onAddTask,
  onAddEvent
}: DashboardPageProps) {
  
  // Calculate metric values
  const activeTasks = tasks.filter(t => t.status !== 'COMPLETED').length;
  const plannerScore = digitalTwin?.planning_score || 85;

  const mockChartData = [
    { name: 'Mon', completion: 65, stress: 30 },
    { name: 'Tue', completion: 75, stress: 25 },
    { name: 'Wed', completion: 85, stress: 35 },
    { name: 'Thu', completion: 80, stress: 40 },
    { name: 'Fri', completion: 90, stress: 20 },
    { name: 'Sat', completion: 95, stress: 15 },
    { name: 'Sun', completion: 90, stress: 10 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      {/* Hero Header Banner */}
      <HeroBanner
        userName="Lakshmanan"
        scheduleHealth={scheduleHealth}
        plannerScore={plannerScore}
        eventsCount={events.length}
        tasksCount={activeTasks}
        streakCount={12}
        aiBriefSummary={`Your schedule health is at ${scheduleHealth}%. You have ${events.length} activities scheduled for today. Make sure to complete shopping before 6 PM.`}
        onOpenAiPlanner={() => onNavigate('ai-planner')}
      />

      {/* Key Metrics cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
        {[
          { title: "Today's Tasks", val: activeTasks, icon: CheckSquare, color: 'text-blue-600 bg-blue-50/80 border-blue-100' },
          { title: "Upcoming Events", val: events.length, icon: Calendar, color: 'text-indigo-600 bg-indigo-50/80 border-indigo-100' },
          { title: "Goal Progress", val: `${Math.round(goals.length ? goals.reduce((acc, g) => acc + g.progress, 0) / goals.length : 0)}%`, icon: Target, color: 'text-purple-600 bg-purple-50/80 border-purple-100' },
          { title: "Habit Streak", val: `${habits.length ? Math.max(...habits.map(h => h.streak), 0) : 0}d`, icon: Activity, color: 'text-emerald-600 bg-emerald-50/80 border-emerald-100' },
          { title: "Planner Score", val: `${plannerScore}`, icon: TrendingUp, color: 'text-amber-600 bg-amber-50/80 border-amber-100' },
          { title: "Family Health", val: `${scheduleHealth}%`, icon: Users, color: 'text-rose-600 bg-rose-50/80 border-rose-100' }
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="white-card p-5 flex items-center gap-4 hover:scale-[1.03] cursor-pointer">
              <div className={`p-3 rounded-xl border ${item.color} shrink-0`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="overflow-hidden">
                <p className="text-[10px] uppercase font-extrabold text-slate-450 tracking-wider mb-1 truncate">{item.title}</p>
                <p className="text-xl font-extrabold text-slate-800 leading-none">{item.val}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column - col-span-2: AI Daily Brief & Charts */}
        <div className="lg:col-span-2 space-y-6">
          
          <AIDailyBrief 
            bullets={[
              "You have three high-priority tasks today.",
              "Shopping should be completed before 6 PM.",
              "Your child has an exam tomorrow.",
              "Electricity bill is due in two days."
            ]}
            onOpenAiPlanner={() => onNavigate('ai-planner')}
          />

          <div className="white-card p-6 flex flex-col justify-between">
            <div>
              <h4 className="font-extrabold text-slate-800 text-sm uppercase tracking-tight mb-4 flex items-center gap-1.5">
                <TrendingUp className="h-4.5 w-4.5 text-[#1D4ED8]" /> Weekly Consistency
              </h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockChartData}>
                    <defs>
                      <linearGradient id="colorGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1D4ED8" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#1D4ED8" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} axisLine={false} tickLine={false} />
                    <YAxis stroke="#94A3B8" fontSize={11} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#FFF', borderRadius: '12px', border: '1px solid #E2E8F0' }} />
                    <Area type="monotone" dataKey="completion" stroke="#1D4ED8" strokeWidth={2.5} fillOpacity={1} fill="url(#colorGrad)" name="Task Completion %" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column - col-span-1: Today's Plan & Quick Actions */}
        <div className="space-y-6">
          
          <TodayPlanCard 
            events={events}
            onViewTimeline={() => onNavigate('family-schedule')}
          />

          <QuickActions 
            onCreateTask={onAddTask}
            onScheduleMeeting={onAddEvent}
            onAiPlanDay={() => onNavigate('ai-planner')}
            onGenerateWeeklyPlan={() => onNavigate('ai-planner')}
            onViewCalendar={() => onNavigate('calendar')}
            onAddReminder={onAddEvent}
          />

        </div>

      </div>
    </motion.div>
  );
}
