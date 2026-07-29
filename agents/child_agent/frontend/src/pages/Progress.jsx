import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Clock, Zap } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonChart, SkeletonCard } from '../components/Skeleton';

const stagger = { hidden:{}, show:{ transition:{ staggerChildren:0.07 } } };
const fadeUp  = { hidden:{ opacity:0, y:14 }, show:{ opacity:1, y:0, transition:{ type:'spring', stiffness:260, damping:22 } } };

const tooltipStyle = {
  contentStyle: { background:'#0B1F33', border:'1px solid rgba(99,102,241,0.3)', borderRadius:12, color:'#fff', fontSize:12 },
};

export default function Progress() {
  const { refreshToken, studentId } = useApp();
  const [progress, setProgress] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [p, s] = await Promise.all([api.getProgress(studentId), api.getStudySessions(studentId)]);
        if (!cancelled) { setProgress(p); setSessions(s); }
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const totalHours = progress.reduce((s,p) => s + (p.study_hours||0), 0);
  const avgFocus   = sessions.length ? Math.round(sessions.reduce((s,ss)=>s+(ss.focus_score||0),0)/sessions.length) : 0;
  const totalSessions = sessions.length;
  const longestDay = progress.reduce((m,p)=>p.study_hours>m?p.study_hours:m, 0);

  const dailyData = progress.slice(-14).map(p=>({
    date: p.date?.slice(5) ?? '',
    hours: parseFloat((p.study_hours||0).toFixed(1)),
    score: p.performance_score ?? 0,
  }));

  // Per-session bar data (last 10)
  const sessionData = sessions.slice().reverse().slice(0,10).map((s,i)=>({
    name: `S${i+1}`,
    mins: s.duration_minutes,
    focus: s.focus_score ?? 0,
  }));

  return (
    <div className="space-y-6">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><BarChart3 className="text-indigo-500" size={24}/> Progress Analytics</h1>
        <p className="section-sub">Your academic performance and study consistency over time.</p>
      </motion.div>

      {/* Summary cards */}
      <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {icon:Clock,    label:'Total Hours',    value:`${totalHours.toFixed(1)}h`, color:'bg-indigo-50 text-indigo-600'},
          {icon:TrendingUp,label:'Sessions',       value:totalSessions,              color:'bg-purple-50 text-purple-600'},
          {icon:Zap,      label:'Avg Focus Score', value:`${avgFocus}/100`,           color:'bg-amber-50 text-amber-600'},
          {icon:BarChart3,label:'Best Day',        value:`${longestDay.toFixed(1)}h`, color:'bg-emerald-50 text-emerald-600'},
        ].map(({icon:Icon,label,value,color}) => (
          <motion.div key={label} variants={fadeUp} className="glass rounded-2xl p-5 flex items-center gap-3 card-hover">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
              <Icon size={18}/>
            </div>
            <div>
              <div className="text-xs font-semibold text-gray-400">{label}</div>
              <div className="text-xl font-extrabold text-navy-dark">{loading?'—':value}</div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Daily Study Trend */}
      <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass rounded-3xl p-6">
        <h3 className="font-bold text-navy-dark mb-5 flex items-center gap-2">
          <TrendingUp size={16} className="text-indigo-500"/> Daily Study Trend (14 days)
        </h3>
        {loading ? <SkeletonChart/> : dailyData.length===0 ? (
          <div className="h-52 flex items-center justify-center text-sm text-gray-400">No data yet. Record your first study session!</div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={dailyData}>
              <defs>
                <linearGradient id="pGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#6366F1" stopOpacity={0.4}/>
                  <stop offset="100%" stopColor="#6366F1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f8"/>
              <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false}/>
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} unit="h"/>
              <Tooltip {...tooltipStyle} formatter={v=>[`${v}h`, 'Study']}/>
              <Area type="monotone" dataKey="hours" stroke="#6366F1" strokeWidth={2.5} fill="url(#pGrad)" dot={{fill:'#6366F1',r:3}}/>
            </AreaChart>
          </ResponsiveContainer>
        )}
      </motion.div>

      {/* Session Quality */}
      <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass rounded-3xl p-6">
        <h3 className="font-bold text-navy-dark mb-5 flex items-center gap-2">
          <Zap size={16} className="text-amber-500"/> Session Quality (last 10)
        </h3>
        {loading ? <SkeletonChart/> : sessionData.length===0 ? (
          <div className="h-48 flex items-center justify-center text-sm text-gray-400">No sessions recorded yet.</div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sessionData} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f8"/>
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false}/>
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false}/>
              <Tooltip {...tooltipStyle}/>
              <Legend wrapperStyle={{fontSize:12}}/>
              <Bar dataKey="mins"  name="Minutes"    fill="#6366F1" radius={[4,4,0,0]}/>
              <Bar dataKey="focus" name="Focus Score" fill="#7C3AED" radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        )}
      </motion.div>
    </div>
  );
}
