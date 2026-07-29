import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Brain, RotateCcw, Smile } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import AIOrb from '../components/AIOrb';

const WELCOME = {
  role: 'ai',
  content: `Hey! I'm your AI Companion — not just a tutor, but a study buddy who gets you. 🎓\n\nI know your subjects, your goals, and your schedule. Talk to me about anything: stress, procrastination, study hacks, or just tell me how your day went. I'm here!`,
};

const MOODS = [
  { emoji:'😊', label:'Great',      prompt:'I am feeling great today!'          },
  { emoji:'😐', label:'Okay',       prompt:'I am feeling okay, just meh.'       },
  { emoji:'😤', label:'Stressed',   prompt:'I am feeling really stressed right now.' },
  { emoji:'😴', label:'Tired',      prompt:'I am really tired and low on energy.'},
  { emoji:'🔥', label:'Motivated',  prompt:'I am super motivated!'              },
];

function TypingDots() {
  return (
    <div className="flex gap-1 p-3 bg-white border border-border rounded-2xl w-fit">
      {[0,1,2].map(i=>(
        <motion.div key={i} className="w-2 h-2 rounded-full bg-indigo-400"
          animate={{y:[0,-4,0]}} transition={{duration:0.6,repeat:Infinity,delay:i*0.12}}/>
      ))}
    </div>
  );
}

export default function AICompanion() {
  const { studentId } = useApp();
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('idle');
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({behavior:'smooth'}); }, [messages, status]);

  const send = async (text) => {
    const q = (text ?? input).trim();
    if (!q || status !== 'idle') return;
    setInput('');
    setMessages(m=>[...m,{role:'user',content:q}]);
    setStatus('thinking');
    try {
      const res = await api.queryAI(studentId, q);
      setMessages(m=>[...m,{role:'ai',content:res.response ?? res.answer ?? 'I hear you! Let me help.'}]);
    } catch {
      setMessages(m=>[...m,{role:'ai',content:'Having a little trouble connecting right now. Try again!'}]);
    } finally { setStatus('idle'); }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-h-[800px]">
      {/* Header */}
      <div className="glass rounded-t-3xl px-6 py-4 flex items-center gap-4 border-b border-border">
        <AIOrb status={status} size="sm"/>
        <div>
          <h1 className="font-extrabold text-navy-dark">AI Companion</h1>
          <p className="text-xs text-gray-400">Your personalized study buddy · Always here</p>
        </div>
        <button onClick={()=>setMessages([WELCOME])} className="ml-auto btn-ghost text-xs px-3 py-1.5">
          <RotateCcw size={12}/> Reset
        </button>
      </div>

      {/* Mood bar */}
      {messages.length <= 1 && (
        <div className="glass px-6 py-3 flex items-center gap-2 border-b border-border">
          <Smile size={14} className="text-gray-400 shrink-0"/>
          <span className="text-xs font-semibold text-gray-400 mr-1">How are you?</span>
          {MOODS.map(m=>(
            <button key={m.label} onClick={()=>send(m.prompt)}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-gray-50 hover:bg-indigo-50 hover:text-indigo-600 text-xs font-medium transition-colors border border-transparent hover:border-indigo-100">
              {m.emoji} {m.label}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto glass rounded-none px-6 py-5 space-y-4">
        {messages.map((msg,i)=>(
          <div key={i} className={`flex gap-3 ${msg.role==='ai'?'flex-row':'flex-row-reverse'}`}>
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-sm shrink-0 mt-0.5 ${msg.role==='ai'?'gradient-indigo-purple text-white':'bg-navy-dark text-white'}`}>
              {msg.role==='ai'?<Brain size={14}/>:'✦'}
            </div>
            <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role==='ai'?'bg-white border border-border text-navy-dark':'gradient-indigo-purple text-white'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {status==='thinking' && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-xl gradient-indigo-purple flex items-center justify-center shrink-0">
              <Brain size={14} className="text-white"/>
            </div>
            <TypingDots/>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* Input */}
      <div className="glass rounded-b-3xl px-4 py-4 border-t border-border flex gap-3 items-end">
        <textarea
          value={input}
          onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}}
          placeholder="Talk to your companion… (Enter to send)"
          rows={1}
          className="input-base flex-1 resize-none min-h-[44px] max-h-28 overflow-y-auto"
        />
        <button onClick={()=>send()} disabled={!input.trim()||status!=='idle'} className="btn-primary w-11 h-11 p-0 rounded-xl shrink-0 disabled:opacity-40">
          <Send size={16}/>
        </button>
      </div>
    </div>
  );
}
