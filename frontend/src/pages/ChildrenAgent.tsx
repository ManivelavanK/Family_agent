import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { motion } from 'framer-motion';
import { 
  Clock, FileText, CheckCircle, GraduationCap, 
  Sparkles, TrendingUp, ChevronRight, Play, BrainCircuit, Plus, Bot,
  RefreshCw
} from 'lucide-react';

import { childrenApi } from '../api/childrenApi';

export default function ChildrenAgent() {
  const { token } = useAuthStore();
  const { activeTabs } = useActiveTabStore();
  const activeTab = activeTabs['/children'] || 'dashboard';

  const [stats, setStats] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [dailyBrief, setDailyBrief] = useState<any>(null);
  
  const [loading, setLoading] = useState(true);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const dash = await childrenApi.getDashboard(1);
      if (dash) {
        setStats({
          total_study_hours: Math.round((dash.study_performance?.total_study_minutes || 0) / 60),
          streak: dash.study_performance?.total_sessions || 0,
          learner_goal: dash.todays_priorities?.[0] || 'Be Consistent'
        });
        setTasks(new Array(dash.homework_status?.pending_count || 0).fill({}));
        setGoals(dash.todays_priorities || []);
        setExams(dash.upcoming_deadlines || []);
        setDailyBrief({ summary: (dash.greeting || 'Hello!') + ' ' + (dash.todays_priorities?.join(' ') || '') });
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [token]);

  // Derived metrics
  const totalStudyHours = stats?.total_study_hours ?? 0;
  const pendingAssignmentsCount = Array.isArray(tasks) ? tasks.length : 0;
  const activeGoalsCount = Array.isArray(goals) ? goals.length : 0;
  const upcomingExamsCount = Array.isArray(exams) ? exams.length : 0;
  const streak = stats?.streak ?? 0;
  const learnerGoal = stats?.learner_goal ?? 'Undecided';

  return (
    <div className="min-h-full bg-[#070E16] text-slate-200 p-8">
      {/* Header Banner */}
      <div className="bg-[#0F1C2E] rounded-3xl p-8 mb-8 flex flex-col md:flex-row items-start md:items-center justify-between border border-blue-900/30 shadow-lg relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px] pointer-events-none" />
        
        <div className="relative z-10">
          <h1 className="text-3xl font-bold text-white mb-2">Good morning, Student 👋</h1>
          <p className="text-blue-300/80 font-medium flex items-center space-x-2">
            <span>· learner</span>
            <span>· Goal: {learnerGoal}</span>
          </p>
        </div>
        
        <div className="mt-4 md:mt-0 relative z-10 flex items-center space-x-4">
          <button onClick={fetchAllData} className="p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-xl transition-colors border border-blue-500/20">
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <div className="bg-amber-500/20 border border-amber-500/30 text-amber-400 px-4 py-2 rounded-full font-bold flex items-center shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <span className="mr-2">🔥</span> STUDY STREAK - {streak} sessions
          </div>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Left Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* KPI Cards Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-[#0F1C2E] p-5 rounded-2xl border border-slate-800/60 shadow-sm flex flex-col justify-between">
                <Clock className="w-6 h-6 text-blue-400 mb-3" />
                <div>
                  <p className="text-3xl font-bold text-white mb-1">{totalStudyHours}h</p>
                  <p className="text-xs text-slate-400 font-medium">Total Study Hours</p>
                </div>
              </div>
              <div className="bg-[#0F1C2E] p-5 rounded-2xl border border-slate-800/60 shadow-sm flex flex-col justify-between">
                <FileText className="w-6 h-6 text-emerald-400 mb-3" />
                <div>
                  <p className="text-3xl font-bold text-white mb-1">{pendingAssignmentsCount}</p>
                  <p className="text-xs text-slate-400 font-medium">Pending Assignments</p>
                </div>
              </div>
              <div className="bg-[#0F1C2E] p-5 rounded-2xl border border-slate-800/60 shadow-sm flex flex-col justify-between">
                <CheckCircle className="w-6 h-6 text-purple-400 mb-3" />
                <div>
                  <p className="text-3xl font-bold text-white mb-1">{activeGoalsCount}</p>
                  <p className="text-xs text-slate-400 font-medium">Active Goals</p>
                </div>
              </div>
              <div className="bg-[#0F1C2E] p-5 rounded-2xl border border-slate-800/60 shadow-sm flex flex-col justify-between">
                <GraduationCap className="w-6 h-6 text-amber-400 mb-3" />
                <div>
                  <p className="text-3xl font-bold text-white mb-1">{upcomingExamsCount}</p>
                  <p className="text-xs text-slate-400 font-medium">Upcoming Exams</p>
                </div>
              </div>
            </div>

            {/* AI Daily Brief Box */}
            <div className="bg-gradient-to-br from-[#0F1C2E] to-[#0A1220] rounded-2xl p-6 border border-blue-900/40 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-[50px] rounded-full pointer-events-none" />
              
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-white">AI DAILY BRIEF</h2>
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 ml-2">Powered by Groq / Llama 3.3 70b</span>
              </div>
              
              <div className="text-slate-300 leading-relaxed text-sm">
                {dailyBrief?.summary ? (
                  <p>{dailyBrief.summary}</p>
                ) : (
                  <p className="italic text-slate-500">Your AI brief will appear here once you have recorded study sessions, assignments, and goals.</p>
                )}
              </div>
            </div>

            {/* Study Consistency Chart */}
            <div className="bg-[#0F1C2E] rounded-2xl p-6 border border-slate-800/60">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-white flex items-center">
                  <TrendingUp className="w-5 h-5 text-emerald-400 mr-2" /> Study Consistency
                </h2>
                <button className="text-xs text-blue-400 hover:text-blue-300 flex items-center transition-colors">
                  Full Analytics <ChevronRight className="w-3 h-3 ml-1" />
                </button>
              </div>
              
              <div className="h-48 flex items-center justify-center border border-dashed border-slate-700/50 rounded-xl bg-[#0A1220]/50">
                <p className="text-sm text-slate-500 italic">No progress data yet. Complete a study session to populate this chart.</p>
              </div>
            </div>

          </div>

          {/* Right Column Panels */}
          <div className="space-y-6">
            
            {/* STUDY NOW Card */}
            <div className="bg-gradient-to-b from-blue-600 to-indigo-700 rounded-2xl p-6 relative overflow-hidden shadow-[0_10px_30px_rgba(37,99,235,0.2)] border border-blue-400/30">
              <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 blur-[40px] rounded-full pointer-events-none" />
              
              <div className="flex items-center justify-between mb-4 relative z-10">
                <h2 className="text-lg font-bold text-white flex items-center">
                  <Sparkles className="w-5 h-5 text-amber-300 mr-2" /> STUDY NOW
                </h2>
                <button className="text-xs text-blue-100 hover:text-white flex items-center transition-colors">
                  Open Planner <ChevronRight className="w-3 h-3 ml-1" />
                </button>
              </div>
              
              <p className="text-sm text-blue-100/90 mb-6 relative z-10">
                {dailyBrief?.recommendation || "You're all caught up! Consider reviewing your recent notes or exploring new topics to get ahead."}
              </p>
              
              <button className="w-full bg-white text-indigo-700 font-bold py-3 rounded-xl flex items-center justify-center hover:bg-slate-50 transition-colors shadow-lg relative z-10">
                <Play className="w-4 h-4 mr-2" fill="currentColor" /> Start AI Study Session
              </button>
            </div>

            {/* QUICK ACTIONS Card */}
            <div className="bg-[#0F1C2E] rounded-2xl p-6 border border-slate-800/60">
              <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Quick Actions</h2>
              
              <div className="space-y-3">
                <button className="w-full flex items-center p-3 rounded-xl bg-[#152338] hover:bg-[#1A2C45] transition-colors border border-slate-700/50 group">
                  <div className="w-8 h-8 rounded-lg bg-orange-500/20 text-orange-400 flex items-center justify-center mr-3 group-hover:bg-orange-500 group-hover:text-white transition-colors">
                    <Clock className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-200">Start Focus Timer</span>
                </button>
                
                <button className="w-full flex items-center p-3 rounded-xl bg-[#152338] hover:bg-[#1A2C45] transition-colors border border-slate-700/50 group">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mr-3 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                    <BrainCircuit className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-200">AI Tutor Session</span>
                </button>

                <button className="w-full flex items-center p-3 rounded-xl bg-[#152338] hover:bg-[#1A2C45] transition-colors border border-slate-700/50 group">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center mr-3 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                    <Plus className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-200">Add Assignment</span>
                </button>

                <button className="w-full flex items-center p-3 rounded-xl bg-[#152338] hover:bg-[#1A2C45] transition-colors border border-slate-700/50 group">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center mr-3 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                    <Bot className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-200">View AI Companion</span>
                </button>
              </div>
            </div>

          </div>
        </motion.div>
      ) : (
        <div className="flex items-center justify-center h-64 border border-dashed border-slate-800 rounded-2xl">
          <p className="text-slate-500 text-lg">Work in progress: {activeTab.replace('_', ' ')} view</p>
        </div>
      )}
    </div>
  );
}