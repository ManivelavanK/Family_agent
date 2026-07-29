import React, { useState, useRef, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { financeApi } from '../services/financeApi';
import { GlassCard } from '../components/ui/GlassCard';
import { Bot, Send, User, Sparkles, Cpu, RefreshCw, AlertCircle, Check, X, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SUGGESTED_PROMPTS = [
  "Can I buy a ₹15,000 smartwatch?",
  "Remember that I prefer to avoid unnecessary electronics purchases.",
  "What if I wait until next month?",
  "Would buying it next month affect my ₹50,000 goal?",
];

export const AIAdvisor = () => {
  const { familyId } = useFamily();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: "Hello! I am KinNest Father Agent — your family's autonomous financial intelligence supervisor. How can I help you plan, save, or evaluate a financial decision today?",
      agentsUsed: ['Supervisor Agent', 'Finance Intelligence'],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentState, setCurrentState] = useState('Ready');
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText) => {
    const query = questionText || input;
    if (!query.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!questionText) setInput('');
    setLoading(true);
    setCurrentState('Analyzing user intent & planning required context...');

    // Simulate backend steps for realistic visual state progression
    const timers = [
      setTimeout(() => setCurrentState('Retrieving financial context from PostgreSQL...'), 800),
      setTimeout(() => setCurrentState('Consulting specialized agents (Budget, Expense, Bills)...'), 1600),
      setTimeout(() => setCurrentState('Retrieving relevant financial memory preferences...'), 2400),
      setTimeout(() => setCurrentState('Reasoning over verified context...'), 3200),
    ];

    try {
      const res = await financeApi.askSupervisor(familyId, query);
      timers.forEach(clearTimeout);
      
      let agentsUsedList = [];
      if (res.agents_used && typeof res.agents_used === 'object') {
        agentsUsedList = Object.keys(res.agents_used);
      } else if (Array.isArray(res.agents_used)) {
        agentsUsedList = res.agents_used;
      }

      const aiMsg = {
        id: Date.now() + 1,
        sender: 'ai',
        text: res.answer || res.message || 'Analysis complete.',
        intent: res.intent,
        agentsUsed: agentsUsedList.length > 0 ? agentsUsedList : ['Supervisor Agent'],
        toolsUsed: res.tools_used || [],
        dataSources: res.data_sources || [],
        memoryUsed: res.memory_used || [],
        requiresConfirmation: res.requires_confirmation,
        action: res.action,
        actionStatus: null, // 'confirmed' | 'rejected'
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error('Error in AI Advisor call:', err);
      timers.forEach(clearTimeout);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'ai',
          text: 'I encountered an error connecting to the AI backend. Please verify that Groq API key and backend service are active.',
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
      setCurrentState('Ready');
    }
  };

  const handleConfirmAction = async (msgId, action) => {
    // Optimistic UI updates
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, actionStatus: 'confirming' } : m))
    );

    try {
      const res = await fetch(`http://localhost:8000/finance/action/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          family_id: familyId,
          action_type: action.type,
          payload: action.payload,
        }),
      });

      if (!res.ok) throw new Error('Action execution failed');
      
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msgId
            ? {
                ...m,
                actionStatus: 'confirmed',
                text: m.text + '\n\n✅ Action recorded successfully in the database!',
              }
            : m
        )
      );
    } catch (err) {
      console.error(err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msgId
            ? {
                ...m,
                actionStatus: 'failed',
                text: m.text + '\n\n❌ Failed to commit the proposed action.',
              }
            : m
        )
      );
    }
  };

  const handleRejectAction = (msgId) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === msgId
          ? {
              ...m,
              actionStatus: 'rejected',
              text: m.text + '\n\nDon\'t worry, I won\'t record anything.',
            }
          : m
      )
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <Bot className="w-8 h-8 text-[#0F766E]" />
            <span>✦ Father AI Guardian Chat</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Connected to KinNest Multi-Agent Orchestration & Financial Memory engine.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0F766E]/10 border border-[#0F766E]/20 text-[#0F766E] text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-[#0F766E] animate-ping" />
          <span>Guardian Orchestrator Active</span>
        </div>
      </div>

      {/* Chat Window Container */}
      <div className="flex-1 p-4 sm:p-6 flex flex-col justify-between overflow-hidden rounded-2xl kinnest-ai-panel">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center text-white shrink-0 shadow-lg ${
                    msg.sender === 'user'
                      ? 'bg-[#102A43] shadow-emerald-950/20'
                      : msg.isError
                      ? 'bg-[#C53030]'
                      : 'bg-gradient-to-tr from-[#0F766E] to-[#D4A72C] shadow-[#0F766E]/20'
                  }`}
                >
                  {msg.sender === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-[#F7F9FC]" />}
                </div>

                {/* Message Bubble */}
                <div className={`space-y-1.5 ${msg.sender === 'user' ? 'text-right' : ''}`}>
                  {/* Agent Metadata Chips */}
                  {msg.agentsUsed && msg.agentsUsed.length > 0 && (
                    <div className="flex items-center gap-1.5 flex-wrap text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      <Cpu className="w-3 h-3 text-[#D4A72C]" />
                      <span>Agents consulted:</span>
                      {msg.agentsUsed.map((agent, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-[#0F766E]/30 text-emerald-300 border border-[#0F766E]/40"
                        >
                          {agent}
                        </span>
                      ))}
                    </div>
                  )}

                  <div
                    className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.sender === 'user'
                        ? 'bg-[#0F766E] text-[#F7F9FC] rounded-tr-none shadow-lg shadow-emerald-900/10'
                        : msg.isError
                        ? 'bg-[#C53030]/10 border border-[#C53030]/30 text-rose-300 rounded-tl-none'
                        : 'bg-[#102A43] border border-[#243B53] text-slate-100 rounded-tl-none'
                    }`}
                  >
                    {msg.text}

                    {/* Inline Action proposal */}
                    {msg.requiresConfirmation && msg.action && (
                      <div className="mt-4 p-4 rounded-xl bg-slate-950/40 border border-slate-700/50 space-y-3 text-slate-200">
                        <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest block">
                          AI Action Proposal: {msg.action.type.replace('_', ' ')}
                        </span>
                        <div className="text-xs space-y-1 font-mono">
                          {Object.entries(msg.action.payload).map(([k, v]) => (
                            <div key={k}>
                              <span className="text-slate-400">{k}:</span> {String(v)}
                            </div>
                          ))}
                        </div>
                        {msg.actionStatus === null && (
                          <div className="flex items-center gap-2 pt-1.5">
                            <button
                              onClick={() => handleRejectAction(msg.id)}
                              className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 text-xs font-semibold hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-1"
                            >
                              <X className="w-3.5 h-3.5" />
                              <span>Reject</span>
                            </button>
                            <button
                              onClick={() => handleConfirmAction(msg.id, msg.action)}
                              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1 shadow-md shadow-emerald-900/20"
                            >
                              <Check className="w-3.5 h-3.5" />
                              <span>Confirm</span>
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Provenance Footer */}
                  {msg.dataSources && msg.dataSources.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-semibold pt-1">
                      <Database className="w-3 h-3 text-[#38BDF8]" />
                      <span>Based on:</span>
                      <span className="text-slate-300">{msg.dataSources.join(', ')}</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Thinking Animation State */}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3 max-w-md p-4 rounded-2xl bg-[#102A43] border border-[#0F766E]/30 text-[#F7F9FC] text-sm"
            >
              <div className="w-8 h-8 rounded-xl bg-[#0F766E]/20 flex items-center justify-center shrink-0">
                <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
              </div>
              <div className="space-y-1">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <span className="text-[#D4A72C]">✦</span> Father AI status
                </span>
                <p className="text-xs text-slate-400">{currentState}</p>
              </div>
            </motion.div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Suggested Prompt Pills */}
        <div className="pt-4 pb-2 border-t border-[#243B53] flex items-center gap-2 overflow-x-auto scrollbar-none">
          <span className="text-xs font-semibold text-slate-400 shrink-0">Suggestions:</span>
          {SUGGESTED_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              disabled={loading}
              className="px-3 py-1.5 rounded-full text-xs font-medium bg-[#102A43] hover:bg-[#243B53] border border-[#243B53] text-[#F7F9FC] hover:text-[#D4A72C] shrink-0 transition-colors cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="pt-2 flex items-center gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Father AI for financial advice..."
            rows={1}
            className="flex-1 px-4 py-3 rounded-xl bg-[#102A43] border border-[#243B53] text-white text-sm resize-none focus:outline-none focus:border-[#0F766E] focus:ring-1 focus:ring-[#0F766E]"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="p-3 rounded-xl bg-[#0F766E] hover:bg-emerald-600 disabled:opacity-50 text-white font-bold shadow-lg shadow-[#0f766e]/25 transition-all cursor-pointer"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAdvisor;
