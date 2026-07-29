import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Send, Cpu, Sparkles, CheckCircle2, ShieldCheck, Info, RefreshCw } from 'lucide-react';
import type { PlannerAgentResponse } from '../services/api';

interface AIPlannerPageProps {
  promptValue: string;
  setPromptValue: (val: string) => void;
  onSubmit: () => void;
  loading: boolean;
  response: PlannerAgentResponse | null;
}

export default function AIPlannerPage({
  promptValue,
  setPromptValue,
  onSubmit,
  loading,
  response
}: AIPlannerPageProps) {
  const [step, setStep] = useState(0);
  const [devMode, setDevMode] = useState(true);

  const thinkingSteps = [
    "Analyzing planning intent...",
    "Querying PostgreSQL database context...",
    "Retrieving semantic memories...",
    "Evaluating cross-agent schedules...",
    "Resolving calendar conflicts...",
    "Optimizing time utilization...",
    "Finalizing premium recommendations..."
  ];

  // AI Thinking State Simulator
  useEffect(() => {
    let interval: any;
    if (loading) {
      setStep(0);
      interval = setInterval(() => {
        setStep((prev) => (prev < thinkingSteps.length - 1 ? prev + 1 : prev));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const defaultSuggestions = [
    "Plan my next week conflicts.",
    "Optimize grocery shopping slots.",
    "Review my goals deadlines."
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat / Console Console */}
        <div className="lg:col-span-2 space-y-6">
          <div className="dark-panel p-6 border border-[#1D3A5F] space-y-4">
            <h3 className="text-sm font-extrabold flex items-center gap-2 uppercase tracking-wide text-white">
              <Bot className="h-5 w-5 text-[#7C3AED]" /> KinNest AI Planner Console
            </h3>
            
            <div className="space-y-3">
              <textarea
                value={promptValue}
                onChange={(e) => setPromptValue(e.target.value)}
                placeholder="Ask the AI Planner to schedule sessions, resolve family blocks, or audit goals..."
                className="w-full h-28 p-4 rounded-xl bg-[#091523] border border-[#1D3A5F] focus:outline-none focus:border-[#7C3AED] text-slate-100 text-xs font-semibold resize-none"
              />
              
              <div className="flex justify-between items-center">
                <span className="text-[10px] text-slate-400 flex items-center gap-1 font-semibold uppercase">
                  <Cpu className="h-3.5 w-3.5 text-indigo-400" /> PostgreSQL memory connected
                </span>
                
                <button
                  onClick={onSubmit}
                  disabled={loading || !promptValue.trim()}
                  className="px-5 py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#7C3AED]/90 text-white font-extrabold text-xs flex items-center gap-2 transition disabled:opacity-55 shadow-lg shadow-[#7C3AED]/20 border border-[#7C3AED]/30"
                >
                  {loading ? 'Reasoning...' : 'Ask Agent'} <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            {/* Suggestions chips */}
            <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5">
              {defaultSuggestions.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => setPromptValue(sug)}
                  className="px-3 py-1.5 rounded-lg bg-[#091523] hover:bg-[#102A43] text-slate-300 hover:text-white border border-[#1D3A5F] text-[10px] font-semibold transition"
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Thinking Animation */}
          <AnimatePresence>
            {loading && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-5 rounded-2xl bg-[#091523] border border-[#7C3AED]/20 space-y-3.5 overflow-hidden"
              >
                <div className="flex items-center gap-3">
                  <RefreshCw className="h-4.5 w-4.5 text-[#7C3AED] animate-spin" />
                  <p className="text-xs font-bold text-[#A78BFA] animate-pulse">
                    Orchestration Engine: {thinkingSteps[step]}
                  </p>
                </div>
                <div className="w-full bg-[#102A43] h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#7C3AED] h-full transition-all duration-300"
                    style={{ width: `${((step + 1) / thinkingSteps.length) * 100}%` }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Response Pane */}
          {response && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="white-card p-6 border border-slate-200 space-y-5"
            >
              <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                <h4 className="font-extrabold text-slate-800 text-sm uppercase tracking-tight flex items-center gap-2">
                  <Sparkles className="h-4.5 w-4.5 text-[#7C3AED]" /> Response Output
                </h4>
                <span className="text-[10px] bg-purple-50 text-[#7C3AED] font-extrabold px-2 py-0.5 rounded-full border border-purple-100">
                  Confidence: {Math.round((response.execution_trace?.confidence || 0.85) * 100)}%
                </span>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-150 text-xs font-medium text-slate-700 leading-relaxed">
                {response.ai_response}
              </div>

              {response.action_items && response.action_items.length > 0 && (
                <div className="space-y-3">
                  <p className="text-[10px] uppercase font-extrabold text-slate-400 tracking-wider">Proposed Resolutions</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {response.action_items.map((act, idx) => (
                      <div key={idx} className="flex items-center gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200/60">
                        <CheckCircle2 className="h-4 w-4 text-[#10B981] shrink-0" />
                        <span className="text-xs font-semibold text-slate-700">{act}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>

        {/* Trace Panel */}
        <div className="space-y-6">
          <div className="dark-panel p-6 border border-[#1D3A5F] space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-xs uppercase font-extrabold text-slate-200 tracking-wider flex items-center gap-2">
                <ShieldCheck className="h-4.5 w-4.5 text-emerald-400" /> Execution Trace
              </h4>
              <button
                onClick={() => setDevMode(!devMode)}
                className="text-[10px] text-[#A78BFA] font-bold hover:underline uppercase"
              >
                {devMode ? 'Hide' : 'Show'}
              </button>
            </div>

            {devMode && (
              <div className="space-y-4 text-[11px] text-slate-300 font-semibold leading-relaxed">
                <div className="p-3 bg-[#091523] rounded-xl border border-[#1D3A5F] space-y-1.5">
                  <p className="text-[#A78BFA] font-bold">Intent Mode:</p>
                  <p>{response?.execution_trace?.intent || 'Awaiting reasoning intent...'}</p>
                </div>

                <div className="p-3 bg-[#091523] rounded-xl border border-[#1D3A5F] space-y-1.5">
                  <p className="text-[#A78BFA] font-bold">Capabilities activated:</p>
                  <div className="flex flex-wrap gap-1">
                    {(response?.execution_trace?.capabilities || ['Semantic Queries', 'Conflict Engine']).map((c, i) => (
                      <span key={i} className="bg-[#102A43] text-slate-200 px-2 py-0.5 rounded text-[10px]">{c}</span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-[#091523] rounded-xl border border-[#1D3A5F] space-y-1.5">
                  <p className="text-[#A78BFA] font-bold">Agents Summoned:</p>
                  <div className="flex flex-wrap gap-1">
                    {(response?.execution_trace?.agents_used || ['PlannerAgent', 'SupervisorAgent']).map((a, i) => (
                      <span key={i} className="bg-purple-950/60 text-[#D8B4FE] border border-purple-800/30 px-2 py-0.5 rounded text-[10px]">{a}</span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-[#091523] rounded-xl border border-[#1D3A5F] space-y-1.5">
                  <p className="text-[#A78BFA] font-bold">Activated Tools:</p>
                  <div className="flex flex-wrap gap-1">
                    {(response?.execution_trace?.tools_used || ['ConflictResolver', 'DbQuery']).map((t, i) => (
                      <span key={i} className="bg-indigo-950/60 text-[#C7D2FE] border border-indigo-800/30 px-2 py-0.5 rounded text-[10px]">{t}</span>
                    ))}
                  </div>
                </div>

                {response?.execution_trace?.explanation && (
                  <div className="p-3 bg-[#091523] rounded-xl border border-[#1D3A5F] space-y-1.5">
                    <p className="text-[#A78BFA] font-bold flex items-center gap-1">
                      <Info className="h-3.5 w-3.5" /> Logical Rationale:
                    </p>
                    <p className="text-[10px] text-slate-300 font-medium">
                      {response.execution_trace.explanation.reason}
                    </p>
                  </div>
                )}

                <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-white/5">
                  <span>Engine speed:</span>
                  <span className="font-extrabold text-white">{response?.execution_trace?.execution_time_ms || 185}ms</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
