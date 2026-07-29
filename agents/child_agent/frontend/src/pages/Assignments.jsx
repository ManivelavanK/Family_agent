import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, FileText, Trash2, CheckCircle2, Clock, AlertTriangle, Filter } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard } from '../components/Skeleton';

const stagger = { hidden:{}, show:{ transition:{ staggerChildren:0.06 } } };
const fadeUp  = { hidden:{ opacity:0, y:14 }, show:{ opacity:1, y:0, transition:{ type:'spring', stiffness:260, damping:22 } } };

const PRIORITY_STYLE = {
  High:   'pill-red',
  Medium: 'pill-gold',
  Low:    'pill-green',
};
const STATUS_CONFIG = {
  Pending:     { icon: Clock,         className:'pill-indigo', label:'Pending'     },
  'In Progress':{ icon: AlertTriangle, className:'pill-gold',   label:'In Progress' },
  Completed:   { icon: CheckCircle2,  className:'pill-green',  label:'Completed'   },
};

function AssignmentCard({ assignment, subjects, onDelete, onUpdate }) {
  const cfg = STATUS_CONFIG[assignment.status] ?? STATUS_CONFIG.Pending;
  const Icon = cfg.icon;
  const sub = subjects.find(s => s.id === assignment.subject_id);
  const [loading, setLoading] = useState(false);

  const cycle = async () => {
    const next = { Pending:'In Progress', 'In Progress':'Completed', Completed:'Pending' };
    setLoading(true);
    try { await api.updateAssignment(assignment.id, { status: next[assignment.status] }); onUpdate?.(); }
    finally { setLoading(false); }
  };

  const del = async () => {
    try { await api.deleteAssignment(assignment.id); onUpdate?.(); }
    catch(e) { console.error(e); }
  };

  const isDue = assignment.due_date && new Date(assignment.due_date) < new Date();

  return (
    <motion.div
      variants={fadeUp}
      layout
      className={`glass rounded-2xl p-4 flex items-center gap-4 card-hover group transition-all ${assignment.status === 'Completed' ? 'opacity-60' : ''}`}
    >
      <button
        onClick={cycle}
        disabled={loading}
        className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-indigo-50 hover:bg-indigo-100 transition-colors"
      >
        <Icon size={18} className={assignment.status === 'Completed' ? 'text-emerald-500' : 'text-indigo-500'} />
      </button>

      <div className="flex-1 min-w-0">
        <div className={`font-semibold text-navy-dark text-sm ${assignment.status === 'Completed' ? 'line-through text-gray-400' : ''}`}>
          {assignment.title}
        </div>
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {sub && <span className="text-xs text-gray-400">{sub.name}</span>}
          {assignment.due_date && (
            <span className={`text-xs font-medium ${isDue && assignment.status !== 'Completed' ? 'text-rose-500' : 'text-gray-400'}`}>
              {isDue && assignment.status !== 'Completed' ? '⚠ Overdue · ' : 'Due '}
              {new Date(assignment.due_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <span className={PRIORITY_STYLE[assignment.priority] || 'pill-indigo'}>{assignment.priority}</span>
        <span className={cfg.className}>{cfg.label}</span>
        <button
          onClick={del}
          className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-rose-500 transition-all p-1 rounded-lg"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </motion.div>
  );
}

function AddModal({ subjects, onClose, onSave }) {
  const { studentId } = useApp();
  const [form, setForm] = useState({ subject_id:'', title:'', due_date:'', priority:'Medium', description:'' });
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!form.title.trim() || !form.subject_id) return;
    setSaving(true);
    try {
      await api.createAssignment({ student_id:studentId, ...form, subject_id:parseInt(form.subject_id) });
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
        className="glass rounded-3xl p-6 w-full max-w-md shadow-card-hover"
      >
        <h3 className="font-extrabold text-navy-dark text-lg mb-5">New Assignment</h3>
        <div className="space-y-3">
          <input value={form.title} onChange={e=>setForm(f=>({...f,title:e.target.value}))} placeholder="Assignment title *" className="input-base" />
          <select value={form.subject_id} onChange={e=>setForm(f=>({...f,subject_id:e.target.value}))} className="input-base">
            <option value="">Select Subject *</option>
            {subjects.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input type="date" value={form.due_date} onChange={e=>setForm(f=>({...f,due_date:e.target.value}))} className="input-base" />
          <select value={form.priority} onChange={e=>setForm(f=>({...f,priority:e.target.value}))} className="input-base">
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
          <textarea value={form.description} onChange={e=>setForm(f=>({...f,description:e.target.value}))} placeholder="Description (optional)" rows={3} className="input-base resize-none" />
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button onClick={submit} disabled={saving||!form.title.trim()||!form.subject_id} className="btn-primary flex-1">
            {saving ? 'Saving…' : 'Add Assignment'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function Assignments() {
  const { refreshToken, triggerRefresh, studentId } = useApp();
  const [assignments, setAssignments] = useState([]);
  const [subjects,    setSubjects]    = useState([]);
  const [loading, setLoading]         = useState(true);
  const [filter,  setFilter]          = useState('All');
  const [showModal, setShowModal]     = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [a, s] = await Promise.all([api.getAssignments(studentId), api.getSubjects(studentId)]);
        if (!cancelled) { setAssignments(a); setSubjects(s); }
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const FILTERS = ['All','Pending','In Progress','Completed'];
  const filtered = assignments.filter(a => filter === 'All' || a.status === filter);
  const counts = {
    All: assignments.length,
    Pending: assignments.filter(a=>a.status==='Pending').length,
    'In Progress': assignments.filter(a=>a.status==='In Progress').length,
    Completed: assignments.filter(a=>a.status==='Completed').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="section-title flex items-center gap-2.5"><FileText className="text-indigo-500" size={24} /> Assignments</h1>
          <p className="section-sub">Manage, track, and complete your academic tasks.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={15} /> New Assignment
        </button>
      </motion.div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`glass rounded-2xl py-3 px-4 text-sm font-semibold transition-all text-left ${filter===f ? 'border-brand-indigo border-2 text-brand-indigo' : 'text-navy-dark hover:border-indigo-200 border border-transparent'}`}
          >
            <div className="text-lg font-extrabold">{counts[f]}</div>
            <div className="text-xs text-gray-400">{f}</div>
          </button>
        ))}
      </div>

      {/* List */}
      <div className="glass rounded-3xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={15} className="text-indigo-500" />
          <span className="font-bold text-navy-dark text-sm">{filter} Assignments</span>
        </div>

        {loading ? (
          <div className="space-y-3">{Array.from({length:4}).map((_,i)=><SkeletonCard key={i} />)}</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <FileText size={40} className="mx-auto mb-3 opacity-20" />
            <p className="font-semibold">No assignments here.</p>
            <p className="text-sm mt-1">Click "New Assignment" to add one.</p>
          </div>
        ) : (
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-2.5">
            <AnimatePresence mode="popLayout">
              {filtered.map(a => (
                <AssignmentCard
                  key={a.id} assignment={a} subjects={subjects}
                  onDelete={triggerRefresh} onUpdate={triggerRefresh}
                />
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {showModal && <AddModal subjects={subjects} onClose={() => setShowModal(false)} onSave={triggerRefresh} />}
      </AnimatePresence>
    </div>
  );
}
