import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, Plus, Clock, Bookmark, BookOpen, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard } from '../components/Skeleton';

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };
const fadeUp  = { hidden: { opacity:0, y:16 }, show: { opacity:1, y:0, transition:{ type:'spring', stiffness:260, damping:22 } } };

// ── Focus Timer Component ────────────────────────────────────────────────────
function FocusTimer({ subjects, onSessionEnd }) {
  const [running, setRunning] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [topic, setTopic]   = useState('');
  const { studentId } = useApp();

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setSeconds(s => s + 1), 1000);
    return () => clearInterval(id);
  }, [running]);

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`;

  const handleStart = () => {
    if (!selectedSubject) return;
    setRunning(true);
  };

  const handleStop = async () => {
    setRunning(false);
    const mins = Math.floor(seconds / 60);
    if (mins < 1) { setSeconds(0); return; }
    try {
      const sub = subjects.find(s => String(s.id) === selectedSubject);
      await api.recordStudySession({
        student_id: studentId,
        subject_id: parseInt(selectedSubject),
        topic: topic || `${sub?.name ?? 'General'} Study`,
        duration_minutes: mins,
      });
      onSessionEnd?.();
    } catch (e) { console.error(e); }
    setSeconds(0);
  };

  const progress = Math.min((seconds / (25 * 60)) * 100, 100); // Pomodoro 25min

  return (
    <div className="glass-dark rounded-3xl p-7 text-white relative overflow-hidden">
      <div className="absolute -top-12 -right-12 w-40 h-40 rounded-full bg-indigo-600/15 blur-3xl" />
      <div className="flex items-center gap-2.5 mb-6">
        <Clock className="text-indigo-400" size={18} />
        <span className="font-bold text-white">Focus Timer</span>
        <span className="pill-indigo ml-auto">Pomodoro Mode</span>
      </div>

      {/* Clock display */}
      <div className="flex justify-center mb-6">
        <div className="relative w-44 h-44">
          <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(99,102,241,0.15)" strokeWidth="6" />
            <circle
              cx="50" cy="50" r="45" fill="none"
              stroke="url(#timerGrad)" strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 45}`}
              strokeDashoffset={`${2 * Math.PI * 45 * (1 - progress / 100)}`}
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
            <defs>
              <linearGradient id="timerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#6366F1" />
                <stop offset="100%" stopColor="#7C3AED" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-black tracking-tight text-white">{fmt(seconds)}</span>
            <span className="text-xs text-slate-400 mt-1 font-medium">
              {running ? 'Focusing…' : 'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="space-y-3 mb-5">
        <select
          value={selectedSubject}
          onChange={e => setSelectedSubject(e.target.value)}
          className="w-full bg-white/8 border border-white/12 rounded-xl px-4 py-2.5 text-sm text-white outline-none focus:border-indigo-400"
        >
          <option value="">Select Subject…</option>
          {subjects.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        <input
          value={topic}
          onChange={e => setTopic(e.target.value)}
          placeholder="Topic (optional)"
          className="w-full bg-white/8 border border-white/12 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:border-indigo-400"
        />
      </div>

      <button
        onClick={running ? handleStop : handleStart}
        disabled={!selectedSubject && !running}
        className={`w-full flex items-center justify-center gap-2.5 py-3 rounded-2xl font-bold text-sm transition-all ${
          running
            ? 'bg-rose-500/80 hover:bg-rose-500 border border-rose-400/30 text-white'
            : 'bg-gradient-to-r from-indigo-500 to-violet-600 text-white shadow-glow hover:shadow-glow-lg disabled:opacity-40'
        }`}
      >
        {running ? <><Square size={15} /> Stop & Save Session</> : <><Play size={15} /> Start Focus Timer</>}
      </button>
    </div>
  );
}

// ── Session History Card ─────────────────────────────────────────────────────
function SessionCard({ session }) {
  return (
    <motion.div
      variants={fadeUp}
      className="glass rounded-2xl p-4 flex items-center gap-4 card-hover"
    >
      <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center shrink-0">
        <CheckCircle2 size={18} className="text-indigo-500" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-navy-dark text-sm truncate">{session.topic || 'Study Session'}</div>
        <div className="text-xs text-gray-400 mt-0.5">{session.duration_minutes} min</div>
      </div>
      <span className="pill-indigo shrink-0">{session.focus_score ?? '—'}/100</span>
    </motion.div>
  );
}

// ── Subject Chip ─────────────────────────────────────────────────────────────
function SubjectChip({ subject }) {
  const style = subject.color
    ? { background: `${subject.color}18`, borderColor: `${subject.color}44`, color: subject.color }
    : {};
  return (
    <motion.div
      variants={fadeUp}
      style={style}
      className="rounded-2xl border px-4 py-3 flex items-center gap-3 card-hover cursor-pointer"
    >
      <BookOpen size={16} style={{ color: subject.color || '#6366F1' }} />
      <div className="flex-1 min-w-0">
        <div className="font-bold text-navy-dark text-sm truncate">{subject.name}</div>
        <div className="text-xs text-gray-400">{subject.current_grade || 'No grade'}</div>
      </div>
      <div className="text-right shrink-0">
        <div className="text-xs font-bold" style={{ color: subject.color || '#6366F1' }}>
          {subject.target_hours_per_week}h/wk
        </div>
      </div>
    </motion.div>
  );
}

// ── Add Session Modal ────────────────────────────────────────────────────────
function AddSessionModal({ subjects, onClose, onSave }) {
  const { studentId } = useApp();
  const [form, setForm] = useState({ subject_id:'', topic:'', duration_minutes:30 });
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!form.subject_id) return;
    setSaving(true);
    try {
      await api.recordStudySession({ student_id: studentId, ...form, subject_id: parseInt(form.subject_id) });
      onSave?.();
      onClose();
    } catch (e) { console.error(e); } finally { setSaving(false); }
  };

  return (
    <motion.div
      initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale:0.94, opacity:0 }} animate={{ scale:1, opacity:1 }} exit={{ scale:0.94, opacity:0 }}
        className="glass rounded-3xl p-6 w-full max-w-md shadow-card-hover"
      >
        <h3 className="font-extrabold text-navy-dark text-lg mb-5">Log Study Session</h3>
        <div className="space-y-3">
          <select value={form.subject_id} onChange={e => setForm(f=>({...f, subject_id:e.target.value}))} className="input-base">
            <option value="">Select Subject</option>
            {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input value={form.topic} onChange={e => setForm(f=>({...f, topic:e.target.value}))} placeholder="Topic" className="input-base" />
          <div className="flex items-center gap-3">
            <input type="number" value={form.duration_minutes} onChange={e => setForm(f=>({...f, duration_minutes:+e.target.value}))} min={5} className="input-base w-28" />
            <span className="text-sm text-gray-500 font-medium">minutes</span>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button onClick={submit} disabled={saving || !form.subject_id} className="btn-primary flex-1">
            {saving ? 'Saving…' : 'Log Session'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function StudyHub() {
  const { refreshToken, triggerRefresh, studentId } = useApp();
  const [subjects, setSubjects]     = useState([]);
  const [sessions, setSessions]     = useState([]);
  const [loading, setLoading]       = useState(true);
  const [showModal, setShowModal]   = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [subs, sess] = await Promise.all([
          api.getSubjects(studentId),
          api.getStudySessions(studentId),
        ]);
        if (!cancelled) { setSubjects(subs); setSessions(sess); }
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div variants={fadeUp} initial="hidden" animate="show" className="flex items-center justify-between">
        <div>
          <h1 className="section-title flex items-center gap-2.5">
            <BookOpen className="text-indigo-500" size={24} /> Study Hub
          </h1>
          <p className="section-sub">Track sessions, build subjects, own your schedule.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={15} /> Log Session
        </button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Focus Timer */}
        <div className="lg:col-span-1">
          <FocusTimer subjects={subjects} onSessionEnd={triggerRefresh} />
        </div>

        {/* Subjects + History */}
        <div className="lg:col-span-2 space-y-5">
          {/* Subjects */}
          <div className="glass rounded-3xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-navy-dark flex items-center gap-2">
                <Bookmark size={16} className="text-indigo-500" /> My Subjects
              </h3>
            </div>
            {loading ? (
              <div className="space-y-3">{Array.from({length:3}).map((_,i)=><SkeletonCard key={i} />)}</div>
            ) : subjects.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No subjects yet. Add them in your Profile.</p>
            ) : (
              <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {subjects.map(s => <SubjectChip key={s.id} subject={s} />)}
              </motion.div>
            )}
          </div>

          {/* Session History */}
          <div className="glass rounded-3xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-navy-dark flex items-center gap-2">
                <Clock size={16} className="text-indigo-500" /> Recent Sessions
              </h3>
              <span className="pill-indigo">{sessions.length} total</span>
            </div>
            {loading ? (
              <div className="space-y-3">{Array.from({length:4}).map((_,i)=><SkeletonCard key={i} />)}</div>
            ) : sessions.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No sessions recorded yet. Start the Focus Timer above!</p>
            ) : (
              <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-2.5">
                {sessions.slice().reverse().slice(0,8).map(s => <SessionCard key={s.id} session={s} />)}
              </motion.div>
            )}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {showModal && (
          <AddSessionModal
            subjects={subjects}
            onClose={() => setShowModal(false)}
            onSave={triggerRefresh}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
