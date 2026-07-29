import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Sparkles, Clock, FileText, Target, Award,
  Flame, ChevronRight, AlertCircle, BookOpen, TrendingUp,
  Code, Folder, Trophy, FileCheck, Briefcase, UserCheck, Shield
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard, SkeletonText, SkeletonChart } from '../components/Skeleton';

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};
const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show:   { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 260, damping: 22 } },
};

function StatCard({ icon: Icon, label, value, color, to }) {
  const card = (
    <motion.div
      variants={fadeUp}
      whileHover={{ y: -3, boxShadow: '0 12px 32px rgba(99,102,241,0.14)' }}
      className="glass rounded-2xl p-5 flex items-center gap-4 cursor-pointer transition-all"
    >
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={20} />
      </div>
      <div className="min-w-0">
        <div className="text-xs font-semibold text-gray-400 truncate">{label}</div>
        <div className="text-xl font-extrabold text-navy-dark leading-tight">{value ?? '—'}</div>
      </div>
    </motion.div>
  );
  return to ? <Link to={to} className="block">{card}</Link> : card;
}

function AIDailyBrief({ brief, loading }) {
  return (
    <div className="glass-dark rounded-3xl p-6 text-white relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute -top-16 -right-16 w-48 h-48 rounded-full bg-indigo-600/20 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-16 -left-16 w-48 h-48 rounded-full bg-purple-700/15 blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-400/20">
            <Sparkles size={16} className="text-indigo-300" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-widest text-indigo-400">AI Daily Brief</div>
            <div className="text-[11px] text-slate-500">Powered by Groq · llama-3.3-70b</div>
          </div>
        </div>

        {loading ? (
          <SkeletonText lines={4} />
        ) : (
          <p className="text-sm leading-relaxed text-slate-200 font-medium">
            {brief || 'Your AI brief will appear here once you have recorded study sessions, assignments, and goals.'}
          </p>
        )}
      </div>
    </div>
  );
}

function StudyNowCard({ rec, loading }) {
  return (
    <motion.div
      variants={fadeUp}
      className="glass rounded-3xl p-5 border-l-4 border-brand-indigo overflow-hidden"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-indigo-500">✨ Study Now</span>
        <Link to="/ai-planner" className="text-xs text-indigo-400 hover:text-indigo-600 flex items-center gap-1 font-semibold">
          Open Planner <ChevronRight size={12} />
        </Link>
      </div>

      {loading ? (
        <SkeletonText lines={3} />
      ) : rec ? (
        <>
          <div className="text-xl font-extrabold text-navy-dark">{rec.subject}</div>
          <div className="text-sm text-gray-500 font-medium mt-0.5">{rec.topic}</div>
          <div className="mt-3 flex items-center gap-3">
            <span className="pill-indigo">{rec.duration_minutes} min</span>
          </div>
          <p className="mt-3 text-xs text-gray-400 leading-relaxed italic">"{rec.reason}"</p>
        </>
      ) : (
        <div className="text-sm text-gray-400">
          No current recommendation. Add subjects and assignments to get started.
        </div>
      )}
    </motion.div>
  );
}

export default function Dashboard() {
  const { refreshToken, studentId } = useApp();

  const [student,    setStudent]    = useState(null);
  const [brief,      setBrief]      = useState('');
  const [rec,        setRec]        = useState(null);
  const [twin,       setTwin]       = useState(null);
  const [chartData,  setChartData]  = useState([]);
  const [stats,      setStats]      = useState({});
  const [loading,    setLoading]    = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [stu, assigns, goals, exams, progress, sessions, twinData] = await Promise.all([
          api.getStudent(studentId),
          api.getAssignments(studentId),
          api.getGoals(studentId),
          api.getExams(studentId),
          api.getProgress(studentId),
          api.getStudySessions(studentId),
          api.getStudentDigitalTwin(studentId).catch(() => null)
        ]);
        if (cancelled) return;

        setStudent(stu);
        setTwin(twinData);
        setStats({
          pendingAssignments: assigns.filter(a => a.status === 'Pending').length,
          activeGoals:        goals.filter(g => g.status === 'In Progress').length,
          upcomingExams:      exams.length,
          totalHours:         progress.reduce((s, p) => s + p.study_hours, 0).toFixed(1),
          streak:             sessions.length,
        });

        const cd = progress.slice(-7).map(p => ({
          date: p.date?.slice(5) ?? '',
          hours: parseFloat(p.study_hours.toFixed(1)),
        }));
        setChartData(cd);

        // AI Brief (non-blocking)
        api.getDailyBrief(studentId).then(b => { if (!cancelled) setBrief(b.brief); }).catch(() => {});
        api.getStudyNow(studentId).then(r => { if (!cancelled) setRec(r); }).catch(() => {});
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-6">

      {/* ── Hero Banner ─────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        className="relative overflow-hidden rounded-3xl gradient-navy text-white p-6 md:p-8"
        style={{ boxShadow: '0 4px 32px rgba(11,31,51,0.35)' }}
      >
        <div className="relative z-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              {loading ? (
                <>
                  <div className="skeleton w-56 h-7 rounded-lg mb-2" />
                  <div className="skeleton w-72 h-4 rounded-lg" />
                </>
              ) : (
                <>
                  <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
                    {greeting}, {student?.name ?? 'Student'} 👋
                  </h1>
                  <p className="text-slate-400 text-sm mt-1.5 font-medium">
                    {student?.grade} · <span className="text-indigo-400">{student?.learning_style}</span> learner ·{' '}
                    Goal: <span className="text-amber-400">{student?.career_interest ?? 'Undecided'}</span>
                  </p>
                </>
              )}
            </div>

            <div className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 w-fit">
              <Flame className="text-amber-400" size={18} />
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-amber-500">Study Streak</div>
                <div className="text-lg font-extrabold text-amber-400 leading-none">
                  {loading ? '…' : `${stats.streak ?? 0} sessions`}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative orbs */}
        <div className="absolute -right-20 -top-20 w-72 h-72 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />
        <div className="absolute -left-10 -bottom-20 w-56 h-56 rounded-full bg-purple-700/10 blur-3xl pointer-events-none" />
      </motion.div>

      {/* ── Stats Row ───────────────────────────────── */}
      <motion.div variants={stagger} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard icon={Clock}    label="Total Study Hours"  value={`${stats.totalHours}h`}           color="bg-indigo-50 text-indigo-600"  to="/study-hub"   />
            <StatCard icon={FileText} label={student?.education_level === 'COLLEGE' ? "Projects & Tasks" : "Pending Assignments"} value={stats.pendingAssignments}          color="bg-rose-50 text-rose-500"     to="/assignments" />
            <StatCard icon={Target}   label={student?.education_level === 'COLLEGE' ? "Active Milestones" : "Active Goals"}        value={stats.activeGoals}                 color="bg-emerald-50 text-emerald-600" to="/goals"     />
            <StatCard icon={Award}    label={student?.education_level === 'COLLEGE' ? "Assessments" : "Upcoming Exams"}      value={stats.upcomingExams}               color="bg-amber-50 text-amber-600"   to="/exams"       />
          </>
        )}
      </motion.div>

      {/* ── Stage-Aware Academic Digital Twin ─────────────────────────────── */}
      {!loading && twin && (
        <motion.div
          variants={fadeUp}
          className="glass rounded-3xl p-6 relative overflow-hidden border border-indigo-100"
        >
          <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full bg-indigo-50/50 blur-2xl pointer-events-none" />
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="text-indigo-500 animate-pulse" size={20} />
              <div>
                <h3 className="font-extrabold text-navy-dark text-base">Academic Digital Twin</h3>
                <p className="text-[11px] text-gray-400">Dynamic AI analysis of your current learning profile</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs font-bold text-gray-500">
              <div>Learning Score: <span className="text-indigo-600">{(twin.learning_score * 100).toFixed(0)}%</span></div>
              <div>Confidence: <span className="text-emerald-600">{(twin.confidence * 100).toFixed(0)}%</span></div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
            {student?.education_level === 'COLLEGE' ? (
              <>
                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
                    <Code size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Coding Platform Score</div>
                    <div className="text-sm font-black text-navy-dark mt-0.5">{(twin.twin_metrics?.coding_platforms_score * 100 || 0).toFixed(0)}%</div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                    <Folder size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Projects Tracked</div>
                    <div className="text-sm font-black text-navy-dark mt-0.5">{twin.twin_metrics?.projects_completed_count || 0} active</div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                    <Trophy size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Hackathons & Certs</div>
                    <div className="text-sm font-black text-navy-dark mt-0.5 truncate">
                      {twin.twin_metrics?.hackathons_count || 0} Hack · {twin.twin_metrics?.certifications_count || 0} Certs
                    </div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                    <Briefcase size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Internship Tracker</div>
                    <div className="text-xs font-semibold text-navy-dark mt-0.5 truncate" title={twin.twin_metrics?.internship_status}>
                      {twin.twin_metrics?.internship_status || '—'}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                    <FileCheck size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Homework Rate</div>
                    <div className="text-sm font-black text-navy-dark mt-0.5">{(twin.twin_metrics?.homework_completion_rate * 100 || 0).toFixed(0)}%</div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                    <UserCheck size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Attendance Rate</div>
                    <div className="text-sm font-black text-navy-dark mt-0.5">{(twin.twin_metrics?.attendance_rate * 100 || 95).toFixed(0)}%</div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
                    <BookOpen size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Reading Progress</div>
                    <div className="text-xs font-semibold text-navy-dark mt-0.5 truncate" title={twin.twin_metrics?.reading_progress}>
                      {twin.twin_metrics?.reading_progress || '—'}
                    </div>
                  </div>
                </div>

                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                    <Shield size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Study Habits</div>
                    <div className="text-xs font-semibold text-navy-dark mt-0.5 truncate" title={twin.twin_metrics?.study_habits}>
                      {twin.twin_metrics?.study_habits || '—'}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </motion.div>
      )}

      {/* ── Main 2-col ──────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left: AI Brief + Chart */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div variants={fadeUp}>
            <AIDailyBrief brief={brief} loading={loading} />
          </motion.div>

          {/* Progress chart */}
          <motion.div variants={fadeUp} className="glass rounded-3xl p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <TrendingUp className="text-indigo-500" size={18} />
                <h3 className="font-bold text-navy-dark">Study Consistency</h3>
              </div>
              <Link to="/progress" className="text-xs text-indigo-500 hover:text-indigo-700 font-semibold flex items-center gap-1">
                Full Analytics <ChevronRight size={12} />
              </Link>
            </div>

            {loading ? (
              <SkeletonChart />
            ) : chartData.length === 0 ? (
              <div className="h-48 flex items-center justify-center text-sm text-gray-400">
                No progress data yet. Complete a study session to populate this chart.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%"   stopColor="#6366F1" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#6366F1" stopOpacity={0}    />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} unit="h" />
                  <Tooltip
                    contentStyle={{ background: '#0B1F33', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 12, color: '#fff', fontSize: 12 }}
                    formatter={(v) => [`${v}h`, 'Study']}
                  />
                  <Area type="monotone" dataKey="hours" stroke="#6366F1" strokeWidth={2.5} fill="url(#cg)" dot={{ fill: '#6366F1', r: 3 }} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </motion.div>
        </div>

        {/* Right: Study Now + Quick Links */}
        <div className="space-y-5">
          <StudyNowCard rec={rec} loading={loading} />

          {/* Quick Actions */}
          <motion.div variants={fadeUp} className="glass rounded-3xl p-5 space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Quick Actions</div>
            {[
              { icon: BookOpen,   label: 'Start Focus Timer',  to: '/focus-habits', color: 'text-indigo-500 bg-indigo-50' },
              { icon: Sparkles,   label: 'AI Tutor Session',   to: '/ai-tutor',     color: 'text-purple-500 bg-purple-50' },
              { icon: FileText,   label: 'Add Assignment',     to: '/assignments',  color: 'text-rose-500 bg-rose-50'    },
              { icon: AlertCircle,label: 'View AI Companion',  to: '/ai-companion', color: 'text-amber-500 bg-amber-50'  },
            ].map(({ icon: Icon, label, to, color }) => (
              <Link
                key={to}
                to={to}
                className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 transition-all group"
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${color}`}>
                  <Icon size={16} />
                </div>
                <span className="text-sm font-semibold text-navy-dark group-hover:text-indigo-600 transition-colors">{label}</span>
                <ChevronRight size={14} className="ml-auto text-gray-300 group-hover:text-indigo-400 transition-colors" />
              </Link>
            ))}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
