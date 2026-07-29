import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CalendarDays, Sparkles, Zap, Route, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import AIOrb from '../components/AIOrb';
import AIExecutionLog from '../components/AIExecutionLog';
import { SkeletonText } from '../components/Skeleton';

export default function AIPlanner() {
  const { studentId } = useApp();

  const [rec,       setRec]       = useState(null);
  const [weaknesses,setWeaknesses]= useState(null);
  const [path,      setPath]      = useState(null);
  const [brief,     setBrief]     = useState(null);
  const [trace,     setTrace]     = useState(null);

  const [status, setStatus]         = useState('idle');
  const [activePanel, setActivePanel] = useState('study-now');
  const [skillInput, setSkillInput]  = useState('');

  const panels = [
    { id:'study-now',   label:'Study Now',      icon:Zap   },
    { id:'weaknesses',  label:'Weak Areas',     icon:AlertCircle },
    { id:'daily-brief', label:'Daily Brief',    icon:Sparkles },
    { id:'learn-path',  label:'Learning Path',  icon:Route  },
  ];

  const load = async (panel) => {
    setStatus('thinking');
    setTrace(null);
    try {
      let res;
      if (panel==='study-now')   res = await api.getStudyNow(studentId);
      if (panel==='weaknesses')  res = await api.getWeaknesses(studentId);
      if (panel==='daily-brief') res = await api.getDailyBrief(studentId);
      if (panel==='learn-path')  res = await api.getLearningPath(studentId, skillInput || 'Programming');
      setTrace(res);
      if (panel==='study-now')   setRec(res);
      if (panel==='weaknesses')  setWeaknesses(res);
      if (panel==='daily-brief') setBrief(res);
      if (panel==='learn-path')  setPath(res);
    } catch(e) { console.error(e); }
    finally { setStatus('idle'); }
  };

  const switchPanel = (id) => { setActivePanel(id); load(id); };

  useEffect(() => { load('study-now'); }, []);

  const renderContent = () => {
    if (status==='thinking') return <div className="py-10 flex flex-col items-center gap-4"><AIOrb status="thinking" size="md"/><SkeletonText lines={4}/></div>;

    if (activePanel==='study-now' && rec) return (
      <div className="space-y-5">
        <div className="gradient-navy text-white rounded-2xl p-6">
          <div className="text-xs font-bold uppercase tracking-widest text-indigo-300 mb-2">Recommended Right Now</div>
          <div className="text-2xl font-extrabold">{rec.subject || '—'}</div>
          <div className="text-indigo-200 text-sm mt-1">{rec.topic}</div>
          {rec.duration_minutes && <div className="mt-3 pill-indigo w-fit">{rec.duration_minutes} minutes</div>}
          {rec.reason && <p className="mt-4 text-sm text-slate-300 italic leading-relaxed">"{rec.reason}"</p>}
        </div>
      </div>
    );

    if (activePanel==='weaknesses' && weaknesses) return (
      <div className="space-y-3">
        <div className="text-sm font-bold text-navy-dark mb-2">AI-Identified Weak Areas</div>
        {(weaknesses.weaknesses ?? weaknesses.areas ?? []).map((w, i) => (
          <div key={i} className="glass rounded-xl p-4 border-l-4 border-rose-400">
            <div className="font-semibold text-navy-dark text-sm">{w.subject || w}</div>
            {w.reason && <p className="text-xs text-gray-400 mt-1">{w.reason}</p>}
          </div>
        ))}
        {weaknesses.recommendation && (
          <div className="rounded-xl bg-indigo-50 border border-indigo-100 p-4">
            <p className="text-sm text-indigo-800 font-medium">{weaknesses.recommendation}</p>
          </div>
        )}
      </div>
    );

    if (activePanel==='daily-brief' && brief) return (
      <div className="glass-dark rounded-2xl p-5 text-white">
        <div className="text-xs font-bold uppercase tracking-widest text-indigo-300 mb-3">Today's AI Brief</div>
        <p className="text-sm leading-relaxed text-slate-200">{brief.brief || brief.message || JSON.stringify(brief)}</p>
      </div>
    );

    if (activePanel==='learn-path' && path) return (
      <div className="space-y-4">
        <div className="text-sm font-bold text-navy-dark">Learning Path: {skillInput || 'Programming'}</div>
        {(path.steps ?? path.path ?? []).map((step, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg gradient-indigo-purple flex items-center justify-center text-white text-xs font-bold shrink-0 mt-0.5">
              {i+1}
            </div>
            <div className="glass rounded-xl p-3 flex-1">
              <div className="font-semibold text-navy-dark text-sm">{step.topic || step.title || step}</div>
              {step.description && <p className="text-xs text-gray-400 mt-1">{step.description}</p>}
              {step.duration && <span className="pill-indigo mt-2 inline-flex">{step.duration}</span>}
            </div>
          </div>
        ))}
      </div>
    );

    return (
      <div className="text-center py-16 text-gray-400">
        <Sparkles size={36} className="mx-auto mb-3 opacity-20"/>
        <p className="font-semibold">Click a panel to load AI analysis.</p>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><CalendarDays className="text-indigo-500" size={24}/> AI Planner</h1>
        <p className="section-sub">Groq-powered intelligent academic planning and analysis.</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Panel selector */}
        <div className="space-y-3">
          {panels.map(({ id, label, icon:Icon }) => (
            <button
              key={id}
              onClick={() => switchPanel(id)}
              className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-semibold transition-all border text-left ${
                activePanel===id
                  ? 'gradient-indigo-purple text-white border-transparent shadow-glow'
                  : 'glass text-navy-dark border-border hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              <Icon size={16}/> {label}
              {activePanel===id && status==='thinking' && (
                <span className="ml-auto w-2 h-2 rounded-full bg-white animate-pulse"/>
              )}
            </button>
          ))}

          {/* Learning path input */}
          {activePanel==='learn-path' && (
            <div className="space-y-2">
              <input
                value={skillInput}
                onChange={e=>setSkillInput(e.target.value)}
                onKeyDown={e=>e.key==='Enter'&&load('learn-path')}
                placeholder="Enter skill (e.g. Calculus)"
                className="input-base"
              />
              <button onClick={()=>load('learn-path')} className="btn-primary w-full">
                Generate Path
              </button>
            </div>
          )}
        </div>

        {/* Result panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass rounded-3xl p-6 min-h-[300px]">
            <AnimatePresence mode="wait">
              <motion.div key={activePanel+status} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={{opacity:0}} transition={{duration:0.2}}>
                {renderContent()}
              </motion.div>
            </AnimatePresence>
          </div>

          {trace && <AIExecutionLog data={trace} />}
        </div>
      </div>
    </div>
  );
}
