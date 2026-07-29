import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Award, Plus, Trash2, Zap, Calendar, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard } from '../components/Skeleton';

const stagger = { hidden:{}, show:{ transition:{ staggerChildren:0.06 } } };
const fadeUp  = { hidden:{ opacity:0, y:14 }, show:{ opacity:1, y:0, transition:{ type:'spring', stiffness:260, damping:22 } } };

const RISK_COLORS = {
  Low:    'pill-green',
  Medium: 'pill-gold',
  High:   'pill-red',
};

function ReadinessGauge({ score }) {
  const pct = Math.min(score ?? 50, 100);
  const color = pct >= 70 ? '#10B981' : pct >= 45 ? '#F59E0B' : '#EF4444';
  return (
    <div className="relative w-14 h-14">
      <svg viewBox="0 0 60 60" className="-rotate-90 w-full h-full">
        <circle cx="30" cy="30" r="25" fill="none" stroke="#e5e7eb" strokeWidth="5" />
        <motion.circle
          cx="30" cy="30" r="25" fill="none"
          stroke={color} strokeWidth="5" strokeLinecap="round"
          strokeDasharray={`${2*Math.PI*25}`}
          initial={{ strokeDashoffset: 2*Math.PI*25 }}
          animate={{ strokeDashoffset: 2*Math.PI*25*(1-pct/100) }}
          transition={{ duration:0.9, ease:'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-xs font-extrabold" style={{ color }}>
        {pct}
      </div>
    </div>
  );
}

function ExamCard({ exam, subjects, onDelete, onEval }) {
  const [evalLoading, setEvalLoading] = useState(false);
  const sub = subjects.find(s=>s.id===exam.subject_id);
  const daysLeft = exam.exam_date ? Math.ceil((new Date(exam.exam_date)-new Date())/(1000*60*60*24)) : null;

  const evaluate = async () => {
    setEvalLoading(true);
    try { await api.evaluateExamReadiness(exam.id); onEval?.(); }
    catch(e) { console.error(e); }
    finally { setEvalLoading(false); }
  };

  const del = async () => {
    try { await api.deleteExam(exam.id); onDelete?.(); } catch(e){console.error(e);}
  };

  return (
    <motion.div variants={fadeUp} layout className="glass rounded-2xl p-5 card-hover group">
      <div className="flex items-start gap-4">
        <ReadinessGauge score={exam.readiness_score} />
        <div className="flex-1 min-w-0">
          <div className="font-bold text-navy-dark">{exam.title || exam.topic || 'Exam'}</div>
          {sub && <div className="text-xs text-gray-400 mt-0.5">{sub.name}</div>}
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className={RISK_COLORS[exam.risk_level] || 'pill-indigo'}>Risk: {exam.risk_level}</span>
            {exam.target_score && <span className="pill-indigo">Target: {exam.target_score}%</span>}
            {daysLeft !== null && (
              <span className={`text-xs font-semibold ${daysLeft < 0 ? 'text-rose-500' : daysLeft<=3 ? 'text-amber-500' : 'text-gray-400'}`}>
                {daysLeft < 0 ? `${Math.abs(daysLeft)}d ago` : daysLeft===0 ? 'Today!' : `${daysLeft}d left`}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <button
            onClick={evaluate} disabled={evalLoading}
            className="text-xs px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 font-semibold transition-all disabled:opacity-50 flex items-center gap-1"
          >
            <Zap size={11} /> {evalLoading ? 'Analyzing…' : 'Evaluate'}
          </button>
          <button onClick={del} className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-rose-500 transition-all p-1 rounded-lg">
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function AddModal({ subjects, onClose, onSave }) {
  const { studentId } = useApp();
  const [form, setForm] = useState({ subject_id:'', topic:'', exam_date:'', target_score:80, readiness_score:50, risk_level:'Medium' });
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!form.subject_id || !form.topic) return;
    setSaving(true);
    try {
      await api.createExam({ student_id:studentId, ...form, subject_id:parseInt(form.subject_id), target_score:+form.target_score, readiness_score:+form.readiness_score });
      onSave?.(); onClose();
    } finally { setSaving(false); }
  };

  return (
    <motion.div initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={e=>e.target===e.currentTarget&&onClose()}
    >
      <motion.div initial={{scale:0.94,opacity:0}} animate={{scale:1,opacity:1}} exit={{scale:0.94,opacity:0}}
        className="glass rounded-3xl p-6 w-full max-w-md"
      >
        <h3 className="font-extrabold text-navy-dark text-lg mb-5">Add Exam</h3>
        <div className="space-y-3">
          <select value={form.subject_id} onChange={e=>setForm(f=>({...f,subject_id:e.target.value}))} className="input-base">
            <option value="">Select Subject *</option>
            {subjects.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input value={form.topic} onChange={e=>setForm(f=>({...f,topic:e.target.value}))} placeholder="Exam topic / title *" className="input-base" />
          <input type="date" value={form.exam_date} onChange={e=>setForm(f=>({...f,exam_date:e.target.value}))} className="input-base" />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-400 font-medium">Target Score %</label>
              <input type="number" value={form.target_score} onChange={e=>setForm(f=>({...f,target_score:e.target.value}))} min={0} max={100} className="input-base mt-1" />
            </div>
            <div>
              <label className="text-xs text-gray-400 font-medium">Risk Level</label>
              <select value={form.risk_level} onChange={e=>setForm(f=>({...f,risk_level:e.target.value}))} className="input-base mt-1">
                <option>Low</option><option>Medium</option><option>High</option>
              </select>
            </div>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button onClick={submit} disabled={saving||!form.subject_id||!form.topic} className="btn-primary flex-1">
            {saving?'Saving…':'Add Exam'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function Exams() {
  const { refreshToken, triggerRefresh, studentId } = useApp();
  const [exams,    setExams]    = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [e,s] = await Promise.all([api.getExams(studentId), api.getSubjects(studentId)]);
        if (!cancelled) { setExams(e); setSubjects(s); }
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const upcoming = exams.filter(e => e.exam_date && new Date(e.exam_date) >= new Date());
  const past     = exams.filter(e => !e.exam_date || new Date(e.exam_date) < new Date());

  return (
    <div className="space-y-6">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="section-title flex items-center gap-2.5"><Award className="text-indigo-500" size={24}/> Exams</h1>
          <p className="section-sub">Track readiness scores, risk levels, and exam prep.</p>
        </div>
        <button onClick={()=>setShowModal(true)} className="btn-primary"><Plus size={15}/> Add Exam</button>
      </motion.div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          {label:'Total Exams',    value:exams.length,          color:'text-navy-dark'},
          {label:'Upcoming',       value:upcoming.length,       color:'text-amber-600'},
          {label:'High Risk',      value:exams.filter(e=>e.risk_level==='High').length, color:'text-rose-600'},
        ].map(({label,value,color})=>(
          <div key={label} className="glass rounded-2xl p-5">
            <div className={`text-2xl font-extrabold ${color}`}>{loading?'—':value}</div>
            <div className="text-xs text-gray-400 font-medium">{label}</div>
          </div>
        ))}
      </div>

      {/* Upcoming */}
      <div className="glass rounded-3xl p-5">
        <h3 className="font-bold text-navy-dark mb-4 flex items-center gap-2"><Calendar size={16} className="text-indigo-500"/>Upcoming Exams</h3>
        {loading ? (
          <div className="space-y-3">{Array.from({length:3}).map((_,i)=><SkeletonCard key={i}/>)}</div>
        ) : upcoming.length===0 ? (
          <div className="text-center py-10 text-gray-400">
            <CheckCircle2 size={36} className="mx-auto mb-2 opacity-20"/>
            <p className="text-sm font-medium">No upcoming exams. Great job!</p>
          </div>
        ) : (
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-3">
            {upcoming.map(e=><ExamCard key={e.id} exam={e} subjects={subjects} onDelete={triggerRefresh} onEval={triggerRefresh}/>)}
          </motion.div>
        )}
      </div>

      {past.length>0 && (
        <div className="glass rounded-3xl p-5">
          <h3 className="font-bold text-navy-dark mb-4 flex items-center gap-2"><AlertTriangle size={16} className="text-gray-400"/>Past Exams</h3>
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-3">
            {past.map(e=><ExamCard key={e.id} exam={e} subjects={subjects} onDelete={triggerRefresh} onEval={triggerRefresh}/>)}
          </motion.div>
        </div>
      )}

      <AnimatePresence>
        {showModal && <AddModal subjects={subjects} onClose={()=>setShowModal(false)} onSave={triggerRefresh}/>}
      </AnimatePresence>
    </div>
  );
}
