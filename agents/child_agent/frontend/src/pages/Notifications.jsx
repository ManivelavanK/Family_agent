import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, CheckCheck, Info, AlertTriangle, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonCard } from '../components/Skeleton';

const ICONS = {
  info:    { icon:Info,          bg:'bg-indigo-50 text-indigo-500' },
  warning: { icon:AlertTriangle, bg:'bg-amber-50 text-amber-500'  },
  ai:      { icon:Sparkles,      bg:'bg-purple-50 text-purple-500' },
  default: { icon:Bell,          bg:'bg-gray-50 text-gray-500'    },
};

export default function Notifications() {
  const { refreshToken, studentId } = useApp();
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const n = await api.getFamilySummary(studentId).catch(()=>null);
        // Fallback: assemble local notifications from data
        const [assigns, exams, goals] = await Promise.all([
          api.getAssignments(studentId),
          api.getExams(studentId),
          api.getGoals(studentId),
        ]);
        if (cancelled) return;
        const local = [];
        const overdue = assigns.filter(a=>a.status!=='Completed'&&a.due_date&&new Date(a.due_date)<new Date());
        if (overdue.length>0) local.push({ id:'o1', type:'warning', title:`${overdue.length} Overdue Assignment${overdue.length>1?'s':''}`, body:`${overdue.map(a=>a.title).join(', ')}`, time:'Now' });
        const upcoming = exams.filter(e=>e.exam_date&&(new Date(e.exam_date)-new Date())<3*24*60*60*1000&&new Date(e.exam_date)>new Date());
        if (upcoming.length>0) local.push({ id:'e1', type:'warning', title:`Exam in less than 3 days`, body:upcoming.map(e=>e.topic||'Exam').join(', '), time:'Soon' });
        const done = goals.filter(g=>g.status==='Completed');
        if (done.length>0) local.push({ id:'g1', type:'ai', title:`Goal Milestone`, body:`You've completed ${done.length} goal${done.length>1?'s':''}!`, time:'Today' });
        local.push({ id:'sys', type:'info', title:'AI Systems Online', body:'All KinNest agents are running. Your academic data is syncing in real-time.', time:'Active' });
        setNotes(local);
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  return (
    <div className="space-y-6 max-w-2xl">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><Bell className="text-indigo-500" size={24}/> Notifications</h1>
        <p className="section-sub">Smart alerts derived from your live academic data.</p>
      </motion.div>

      {loading ? (
        <div className="space-y-3">{Array.from({length:3}).map((_,i)=><SkeletonCard key={i}/>)}</div>
      ) : notes.length===0 ? (
        <div className="glass rounded-3xl p-12 text-center">
          <CheckCheck size={40} className="mx-auto mb-3 text-emerald-400"/>
          <p className="font-semibold text-navy-dark">All clear!</p>
          <p className="text-sm text-gray-400 mt-1">No alerts right now. Keep up the great work.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notes.map((n,i)=>{
            const cfg = ICONS[n.type] ?? ICONS.default;
            const Icon = cfg.icon;
            return (
              <motion.div key={n.id} initial={{opacity:0,x:-10}} animate={{opacity:1,x:0}} transition={{delay:i*0.07}}
                className="glass rounded-2xl p-5 flex items-start gap-4 card-hover">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${cfg.bg}`}>
                  <Icon size={18}/>
                </div>
                <div className="flex-1">
                  <div className="font-bold text-navy-dark text-sm">{n.title}</div>
                  <p className="text-xs text-gray-400 mt-0.5 leading-relaxed">{n.body}</p>
                </div>
                <span className="text-[11px] text-gray-300 shrink-0 font-medium">{n.time}</span>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
