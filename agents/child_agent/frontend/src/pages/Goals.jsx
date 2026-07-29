import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Plus, Trash2, CheckCircle2, Circle, TrendingUp } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard } from '../components/Skeleton';

const stagger = { hidden:{}, show:{ transition:{ staggerChildren:0.06 } } };
const fadeUp  = { hidden:{ opacity:0, y:14 }, show:{ opacity:1, y:0, transition:{ type:'spring', stiffness:260, damping:22 } } };

const CATEGORY_COLORS = {
  Academic: 'bg-indigo-50 text-indigo-600 border-indigo-100',
  Skill:    'bg-purple-50 text-purple-600 border-purple-100',
  Health:   'bg-emerald-50 text-emerald-600 border-emerald-100',
  Personal: 'bg-amber-50 text-amber-600 border-amber-100',
};

function ProgressBar({ value, color = '#6366F1' }) {
  return (
    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <motion.div
        initial={{ width:0 }}
        animate={{ width:`${Math.min(value ?? 0, 100)}%` }}
        transition={{ duration:0.8, ease:'easeOut' }}
        className="h-full rounded-full"
        style={{ background: color }}
      />
    </div>
  );
}

function GoalCard({ goal, onDelete, onUpdate }) {
  const [loading, setLoading] = useState(false);
  const done = goal.status === 'Completed';

  const toggle = async () => {
    setLoading(true);
    try {
      await api.updateGoal(goal.id, { status: done ? 'In Progress' : 'Completed', progress: done ? goal.progress : 100 });
      onUpdate?.();
    } finally { setLoading(false); }
  };

  const del = async () => {
    try { await api.deleteGoal(goal.id); onDelete?.(); } catch(e){console.error(e);}
  };

  const catStyle = CATEGORY_COLORS[goal.category] || 'bg-gray-50 text-gray-600 border-gray-100';

  return (
    <motion.div
      variants={fadeUp}
      layout
      className={`glass rounded-2xl p-5 card-hover group transition-all ${done ? 'opacity-60' : ''}`}
    >
      <div className="flex items-start gap-3">
        <button onClick={toggle} disabled={loading} className="mt-0.5 shrink-0 text-indigo-500 hover:text-indigo-700 transition-colors">
          {done ? <CheckCircle2 size={20} className="text-emerald-500" /> : <Circle size={20} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className={`font-semibold text-navy-dark text-sm ${done ? 'line-through text-gray-400' : ''}`}>
            {goal.title}
          </div>
          {goal.description && (
            <p className="text-xs text-gray-400 mt-1 leading-relaxed">{goal.description}</p>
          )}
          <div className="mt-3 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-gray-400">Progress</span>
              <span className="text-[11px] font-bold text-indigo-600">{goal.progress ?? 0}%</span>
            </div>
            <ProgressBar value={goal.progress} />
          </div>
          <div className="flex items-center gap-2 mt-3">
            {goal.category && (
              <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${catStyle}`}>
                {goal.category}
              </span>
            )}
            {goal.deadline && (
              <span className="text-[11px] text-gray-400">
                By {new Date(goal.deadline).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={del}
          className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-rose-500 transition-all p-1 rounded-lg shrink-0"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </motion.div>
  );
}

function AddModal({ onClose, onSave }) {
  const { studentId } = useApp();
  const [form, setForm] = useState({ title:'', description:'', category:'Academic', deadline:'', progress:0 });
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      await api.createGoal({ student_id:studentId, ...form });
      onSave?.(); onClose();
    } finally { setSaving(false); }
  };

  return (
    <motion.div
      initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={e => e.target===e.currentTarget && onClose()}
    >
      <motion.div
        initial={{scale:0.94,opacity:0}} animate={{scale:1,opacity:1}} exit={{scale:0.94,opacity:0}}
        className="glass rounded-3xl p-6 w-full max-w-md"
      >
        <h3 className="font-extrabold text-navy-dark text-lg mb-5">New Goal</h3>
        <div className="space-y-3">
          <input value={form.title} onChange={e=>setForm(f=>({...f,title:e.target.value}))} placeholder="Goal title *" className="input-base" />
          <textarea value={form.description} onChange={e=>setForm(f=>({...f,description:e.target.value}))} placeholder="Description" rows={2} className="input-base resize-none" />
          <select value={form.category} onChange={e=>setForm(f=>({...f,category:e.target.value}))} className="input-base">
            <option>Academic</option><option>Skill</option><option>Health</option><option>Personal</option>
          </select>
          <input type="date" value={form.deadline} onChange={e=>setForm(f=>({...f,deadline:e.target.value}))} className="input-base" />
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button onClick={submit} disabled={saving||!form.title.trim()} className="btn-primary flex-1">
            {saving ? 'Saving…' : 'Create Goal'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function Goals() {
  const { refreshToken, triggerRefresh, studentId } = useApp();
  const [goals, setGoals]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [filter, setFilter]     = useState('All');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const g = await api.getGoals(studentId);
        if (!cancelled) setGoals(g);
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const FILTERS = ['All','In Progress','Completed'];
  const filtered = goals.filter(g => filter==='All' || g.status===filter);
  const pct = goals.length ? Math.round(goals.filter(g=>g.status==='Completed').length/goals.length*100) : 0;

  return (
    <div className="space-y-6">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="section-title flex items-center gap-2.5"><Target className="text-indigo-500" size={24}/> Goals</h1>
          <p className="section-sub">Track academic and personal milestones.</p>
        </div>
        <button onClick={()=>setShowModal(true)} className="btn-primary"><Plus size={15}/> New Goal</button>
      </motion.div>

      {/* Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label:'Total', value:goals.length, color:'text-navy-dark' },
          { label:'In Progress', value:goals.filter(g=>g.status==='In Progress').length, color:'text-indigo-600' },
          { label:'Completed', value:goals.filter(g=>g.status==='Completed').length, color:'text-emerald-600' },
        ].map(({label, value, color}) => (
          <div key={label} className="glass rounded-2xl p-5">
            <div className={`text-2xl font-extrabold ${color}`}>{loading ? '—' : value}</div>
            <div className="text-xs text-gray-400 font-medium mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Overall progress bar */}
      {!loading && goals.length > 0 && (
        <div className="glass rounded-2xl p-4 flex items-center gap-4">
          <TrendingUp size={18} className="text-indigo-500 shrink-0" />
          <div className="flex-1">
            <div className="flex justify-between text-xs font-semibold mb-1.5">
              <span className="text-gray-500">Overall Completion</span>
              <span className="text-indigo-600">{pct}%</span>
            </div>
            <ProgressBar value={pct} />
          </div>
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-2">
        {FILTERS.map(f => (
          <button key={f} onClick={()=>setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${filter===f ? 'gradient-indigo-purple text-white shadow-glow' : 'glass text-navy-dark hover:text-indigo-600 border border-border'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* Goals list */}
      <div className="glass rounded-3xl p-5">
        {loading ? (
          <div className="space-y-3">{Array.from({length:3}).map((_,i)=><SkeletonCard key={i}/>)}</div>
        ) : filtered.length===0 ? (
          <div className="text-center py-16 text-gray-400">
            <Target size={40} className="mx-auto mb-3 opacity-20"/>
            <p className="font-semibold">No goals here.</p>
            <p className="text-sm mt-1">Set your first goal above!</p>
          </div>
        ) : (
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-3">
            <AnimatePresence mode="popLayout">
              {filtered.map(g=><GoalCard key={g.id} goal={g} onDelete={triggerRefresh} onUpdate={triggerRefresh}/>)}
            </AnimatePresence>
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {showModal && <AddModal onClose={()=>setShowModal(false)} onSave={triggerRefresh}/>}
      </AnimatePresence>
    </div>
  );
}
