import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, RotateCcw, Timer, Flame, Coffee } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';

const MODES = [
  { id:'pomodoro',   label:'Pomodoro',    workMins:25, breakMins:5,  icon:Flame,  color:'text-indigo-600', bg:'bg-indigo-50' },
  { id:'deep',       label:'Deep Work',   workMins:50, breakMins:10, icon:Timer,  color:'text-purple-600', bg:'bg-purple-50' },
  { id:'short',      label:'Quick Study', workMins:15, breakMins:3,  icon:Coffee, color:'text-amber-600',  bg:'bg-amber-50'  },
];

export default function FocusHabits() {
  const { studentId } = useApp();
  const [mode, setMode]       = useState(MODES[0]);
  const [running, setRunning] = useState(false);
  const [phase, setPhase]     = useState('work');   // work | break
  const [seconds, setSeconds] = useState(MODES[0].workMins * 60);
  const [sessions, setSessions] = useState([]);

  // Timer
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setSeconds(s => {
        if (s <= 1) {
          // Phase complete
          const nextPhase = phase==='work'?'break':'work';
          setPhase(nextPhase);
          return (nextPhase==='work' ? mode.workMins : mode.breakMins) * 60;
        }
        return s-1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [running, phase, mode]);

  const selectMode = (m) => {
    if (running) return;
    setMode(m); setPhase('work'); setSeconds(m.workMins*60);
  };

  const toggleTimer = async () => {
    if (running) {
      // Stopping — save session if in work phase
      const elapsed = (mode.workMins*60 - seconds);
      if (phase==='work' && elapsed > 60) {
        try {
          const subs = await api.getSubjects(studentId);
          if (subs.length > 0) {
            await api.recordStudySession({
              student_id: studentId,
              subject_id: subs[0].id,
              topic: `${mode.label} Focus Block`,
              duration_minutes: Math.round(elapsed/60),
            });
            setSessions(s=>[...s, { mode:mode.label, mins:Math.round(elapsed/60) }]);
          }
        } catch(e){console.error(e);}
      }
      setRunning(false); setPhase('work'); setSeconds(mode.workMins*60);
    } else {
      setRunning(true);
    }
  };

  const fmt = (s) => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
  const total = (phase==='work'?mode.workMins:mode.breakMins)*60;
  const pct = ((total-seconds)/total)*100;
  const phaseColor = phase==='work' ? '#6366F1' : '#10B981';

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><Timer className="text-indigo-500" size={24}/> Focus & Habits</h1>
        <p className="section-sub">Time-box your deep work. Sessions auto-save to your study log.</p>
      </motion.div>

      {/* Mode selector */}
      <div className="grid grid-cols-3 gap-3">
        {MODES.map(m=>{
          const Icon=m.icon;
          return (
            <button key={m.id} onClick={()=>selectMode(m)}
              className={`glass rounded-2xl p-4 text-left transition-all border-2 ${mode.id===m.id?'border-brand-indigo shadow-glow':'border-transparent hover:border-indigo-100'} ${running?'opacity-60 cursor-not-allowed':''}`}
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-2.5 ${m.bg}`}>
                <Icon size={18} className={m.color}/>
              </div>
              <div className="font-bold text-navy-dark text-sm">{m.label}</div>
              <div className="text-xs text-gray-400">{m.workMins}min work / {m.breakMins}min break</div>
            </button>
          );
        })}
      </div>

      {/* Timer */}
      <div className="glass-dark rounded-3xl p-8 flex flex-col items-center gap-6 text-white">
        <div className="text-xs font-bold uppercase tracking-widest" style={{color:phaseColor}}>
          {phase==='work'?'Focus Time':'Break Time'}
        </div>

        {/* Circle timer */}
        <div className="relative w-52 h-52">
          <svg viewBox="0 0 120 120" className="-rotate-90 w-full h-full">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8"/>
            <motion.circle
              cx="60" cy="60" r="52" fill="none"
              stroke={phaseColor} strokeWidth="8" strokeLinecap="round"
              strokeDasharray={`${2*Math.PI*52}`}
              animate={{ strokeDashoffset: 2*Math.PI*52*(1-pct/100) }}
              transition={{ duration:0.5, ease:'linear' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-5xl font-black tracking-tight">{fmt(seconds)}</span>
            <span className="text-xs text-slate-400 mt-1 font-medium">{mode.label}</span>
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={toggleTimer}
            className={`flex items-center gap-2.5 px-8 py-3.5 rounded-2xl font-bold transition-all ${
              running
                ? 'bg-rose-500/80 text-white border border-rose-400/30 hover:bg-rose-500'
                : 'gradient-indigo-purple text-white shadow-glow hover:shadow-glow-lg'
            }`}
          >
            {running?<><Square size={16}/> Stop & Save</>:<><Play size={16}/> Start Timer</>}
          </button>
          <button onClick={()=>{setRunning(false);setPhase('work');setSeconds(mode.workMins*60);}}
            className="px-5 py-3.5 rounded-2xl border border-white/15 text-slate-400 hover:text-white hover:border-white/30 transition-all">
            <RotateCcw size={16}/>
          </button>
        </div>
      </div>

      {/* Session log */}
      {sessions.length > 0 && (
        <div className="glass rounded-3xl p-5">
          <h3 className="font-bold text-navy-dark mb-3 text-sm">Today's Sessions</h3>
          <div className="space-y-2">
            {sessions.map((s,i)=>(
              <div key={i} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
                <div className="w-2 h-2 rounded-full bg-indigo-400"/>
                <span className="text-sm text-navy-dark font-medium">{s.mode}</span>
                <span className="ml-auto pill-indigo">{s.mins} min</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
