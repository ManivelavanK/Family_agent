import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Map, Sparkles, ChevronRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import AIOrb from '../components/AIOrb';
import AIExecutionLog from '../components/AIExecutionLog';

const PRESET_SKILLS = [
  'Machine Learning','Web Development','Calculus','Physics Mechanics',
  'Organic Chemistry','Data Structures','English Writing','Robotics',
];

export default function LearningPath() {
  const { studentId } = useApp();
  const [skill, setSkill]   = useState('');
  const [path,  setPath]    = useState(null);
  const [trace, setTrace]   = useState(null);
  const [status, setStatus] = useState('idle');

  const generate = async (s) => {
    const target = s ?? skill;
    if (!target.trim()) return;
    setSkill(target);
    setStatus('thinking');
    setPath(null); setTrace(null);
    try {
      const res = await api.getLearningPath(studentId, target);
      setPath(res); setTrace(res);
    } catch(e) { console.error(e); }
    finally { setStatus('idle'); }
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><Map className="text-indigo-500" size={24}/> Learning Path</h1>
        <p className="section-sub">AI-generated skill roadmaps tailored to your goals and profile.</p>
      </motion.div>

      {/* Input */}
      <div className="glass rounded-3xl p-6">
        <div className="flex gap-3">
          <input
            value={skill}
            onChange={e=>setSkill(e.target.value)}
            onKeyDown={e=>e.key==='Enter'&&generate()}
            placeholder="Enter skill or subject (e.g. Machine Learning, Calculus, Python)"
            className="input-base flex-1"
          />
          <button onClick={()=>generate()} disabled={!skill.trim()||status==='thinking'} className="btn-primary px-6">
            {status==='thinking'?<Loader2 size={15} className="animate-spin"/>:<><Sparkles size={14}/> Generate</>}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-xs text-gray-400 font-medium mr-1">Quick:</span>
          {PRESET_SKILLS.map(s=>(
            <button key={s} onClick={()=>generate(s)}
              className="text-xs px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 font-semibold transition-colors">
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Result */}
      {status==='thinking' && (
        <div className="glass rounded-3xl p-10 flex flex-col items-center gap-4">
          <AIOrb status="thinking" size="md"/>
          <p className="text-sm text-gray-400 font-medium">Building your personalized learning roadmap…</p>
        </div>
      )}

      {path && status==='idle' && (
        <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} className="space-y-4">
          <div className="glass-dark rounded-3xl p-6 text-white">
            <div className="text-xs font-bold uppercase tracking-widest text-indigo-300 mb-1">Learning Path</div>
            <div className="text-xl font-extrabold">{skill}</div>
            {path.overview && <p className="text-sm text-slate-300 mt-2 leading-relaxed">{path.overview}</p>}
          </div>

          <div className="space-y-3">
            {(path.steps ?? path.path ?? []).map((step, i) => (
              <motion.div
                key={i}
                initial={{opacity:0,x:-10}}
                animate={{opacity:1,x:0}}
                transition={{delay:i*0.06}}
                className="glass rounded-2xl p-4 flex items-start gap-4 card-hover"
              >
                <div className="w-9 h-9 rounded-xl gradient-indigo-purple flex items-center justify-center text-white font-extrabold text-sm shrink-0 mt-0.5">
                  {i+1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-navy-dark text-sm">{step.topic || step.title || step}</div>
                  {step.description && <p className="text-xs text-gray-400 mt-1 leading-relaxed">{step.description}</p>}
                  <div className="flex gap-2 mt-2 flex-wrap">
                    {step.duration    && <span className="pill-indigo">{step.duration}</span>}
                    {step.difficulty  && <span className="pill-purple">{step.difficulty}</span>}
                    {step.resources?.map((r,ri)=><span key={ri} className="pill-gold">{r}</span>)}
                  </div>
                </div>
                <ChevronRight size={14} className="text-gray-300 shrink-0 mt-1"/>
              </motion.div>
            ))}
          </div>

          {trace && <AIExecutionLog data={trace}/>}
        </motion.div>
      )}
    </div>
  );
}
