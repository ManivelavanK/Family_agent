import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, User, RotateCcw, Copy, ChevronDown } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import AIOrb from '../components/AIOrb';
import AIExecutionLog from '../components/AIExecutionLog';

const WELCOME = {
  role: 'ai',
  content: `Hello! I'm your AI Tutor powered by Groq's llama-3.3-70b. I have full context of your academic profile — your subjects, upcoming exams, study history, and goals.\n\nAsk me anything: explain a concept, quiz me, create a study plan, analyze my weaknesses, or suggest what to study next.`,
  trace: null,
};

function MessageBubble({ msg, isLast }) {
  const isAI = msg.role === 'ai';
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <motion.div
      initial={{ opacity:0, y:10 }}
      animate={{ opacity:1, y:0 }}
      transition={{ duration:0.25 }}
      className={`flex gap-3 ${isAI ? 'flex-row' : 'flex-row-reverse'}`}
    >
      {/* Avatar */}
      <div className="shrink-0 mt-1">
        {isAI ? (
          <div className="w-8 h-8 rounded-xl gradient-indigo-purple flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-xl bg-navy-dark flex items-center justify-center">
            <User size={14} className="text-white" />
          </div>
        )}
      </div>

      <div className={`group max-w-[78%] space-y-1 ${isAI ? '' : 'items-end flex flex-col'}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
            isAI
              ? 'bg-white border border-border text-navy-dark'
              : 'gradient-indigo-purple text-white'
          }`}
        >
          {msg.content}
        </div>

        {/* Action row */}
        {isAI && (
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity pl-1">
            <button onClick={copy} className="flex items-center gap-1 text-[11px] text-gray-400 hover:text-indigo-500">
              <Copy size={11} /> {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        )}

        {/* Execution trace for AI messages */}
        {isAI && msg.trace && (
          <div className="mt-2 w-full">
            <AIExecutionLog data={msg.trace} compact />
          </div>
        )}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3 items-end">
      <div className="w-8 h-8 rounded-xl gradient-indigo-purple flex items-center justify-center shrink-0">
        <Sparkles size={14} className="text-white" />
      </div>
      <div className="bg-white border border-border rounded-2xl px-4 py-3 flex items-center gap-1.5">
        {[0,1,2].map(i => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full bg-indigo-400"
            animate={{ y: [0,-4,0] }}
            transition={{ duration:0.7, repeat:Infinity, delay: i * 0.12 }}
          />
        ))}
      </div>
    </div>
  );
}

const SUGGESTED = [
  'Explain the chain rule in calculus',
  'Create a 7-day exam prep plan for Physics',
  'What are my weakest subjects?',
  'Quiz me on Newton\'s laws',
  'What should I study right now?',
  'Help me understand photosynthesis',
];

export default function AITutor() {
  const { studentId } = useApp();
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput]       = useState('');
  const [status, setStatus]     = useState('idle');  // idle | thinking | responding
  const [devMode, setDevMode]   = useState(false);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:'smooth' });
  }, [messages, status]);

  const send = async (text) => {
    const q = (text ?? input).trim();
    if (!q || status === 'thinking') return;

    setInput('');
    setMessages(m => [...m, { role:'user', content:q, trace:null }]);
    setStatus('thinking');

    try {
      const res = await api.queryAI(studentId, q);
      setStatus('responding');
      setMessages(m => [...m, {
        role:'ai',
        content: res.response ?? res.answer ?? 'I\'m here to help! Could you rephrase that?',
        trace: devMode ? res : null,
      }]);
    } catch {
      setMessages(m => [...m, { role:'ai', content:'Sorry, I encountered an error. Please try again.', trace:null }]);
    } finally {
      setStatus('idle');
      inputRef.current?.focus();
    }
  };

  const reset = () => {
    setMessages([WELCOME]);
    setStatus('idle');
    setInput('');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-h-[860px]">

      {/* ── Header ── */}
      <div className="glass rounded-t-3xl px-6 py-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-4">
          <AIOrb status={status} size="sm" />
          <div>
            <h1 className="font-extrabold text-navy-dark text-base">AI Tutor</h1>
            <div className="text-xs text-gray-400 font-medium">
              {status === 'idle' && 'Ready · Groq · llama-3.3-70b'}
              {status === 'thinking' && '🧠 Reasoning through your question…'}
              {status === 'responding' && '✨ Generating response…'}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setDevMode(d => !d)}
            className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all border ${devMode ? 'bg-indigo-50 text-indigo-600 border-indigo-200' : 'border-border text-gray-400 hover:text-indigo-500'}`}
          >
            {devMode ? '⚙ Trace ON' : '⚙ Trace'}
          </button>
          <button onClick={reset} className="btn-ghost text-xs px-3 py-1.5">
            <RotateCcw size={12} /> Reset
          </button>
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto glass rounded-none px-6 py-5 space-y-5">
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} isLast={i === messages.length - 1} />
        ))}
        {status === 'thinking' && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* ── Suggestions ── */}
      <AnimatePresence>
        {messages.length <= 1 && status === 'idle' && (
          <motion.div
            initial={{ opacity:0, height:0 }}
            animate={{ opacity:1, height:'auto' }}
            exit={{ opacity:0, height:0 }}
            className="glass px-6 py-3 overflow-hidden"
          >
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs font-medium px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Input ── */}
      <div className="glass rounded-b-3xl px-4 py-4 border-t border-border">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
              }}
              placeholder="Ask anything… Shift+Enter for new line"
              rows={1}
              className="input-base resize-none min-h-[44px] max-h-32 pr-10 py-3 overflow-y-auto"
              style={{ height:'auto' }}
            />
          </div>
          <button
            onClick={() => send()}
            disabled={!input.trim() || status === 'thinking'}
            className="btn-primary w-11 h-11 p-0 rounded-xl shrink-0 disabled:opacity-40"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
