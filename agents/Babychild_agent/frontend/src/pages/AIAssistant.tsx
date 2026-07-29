import React, { useEffect, useRef, useState } from 'react';
import { Sparkles, Send, User, CheckCircle, Loader2, Bot } from 'lucide-react';
import { aiService, ChatMessage } from '../services/aiService';

// Simple markdown-like bold parser
function parseBold(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function formatMessage(text: string) {
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return <br key={i} />;
    return (
      <p key={i} className="mb-1 leading-relaxed">
        {parseBold(line)}
      </p>
    );
  });
}

const AGENT_STEPS_LABELS: Record<string, string> = {
  'Sleep Analysis': '😴 Checking sleep logs',
  'Feeding Analysis': '🍼 Checking feeding patterns',
  'Growth Monitoring': '📈 Checking growth data',
  'Health History': '🩺 Reviewing health history',
  'Vaccination Schedule': '💉 Checking vaccination records',
  'Nutrition Monitoring': '🥗 Reviewing nutrition balance',
  'WHO Standards Database': '📊 Comparing WHO standards',
  'Appointment Manager': '📅 Checking appointments',
};

export default function AIAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentSteps, setAgentSteps] = useState<string[]>([]);
  const [runningStepIdx, setRunningStepIdx] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    aiService.getMessages().then(setMessages);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, agentSteps, runningStepIdx]);

  const runStepAnimation = (steps: string[]) => {
    setAgentSteps(steps);
    setRunningStepIdx(0);
    return new Promise<void>((resolve) => {
      let idx = 0;
      const advance = () => {
        idx++;
        if (idx < steps.length) {
          setRunningStepIdx(idx);
          setTimeout(advance, 350);
        } else {
          setTimeout(resolve, 200);
        }
      };
      setTimeout(advance, 350);
    });
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');
    setIsLoading(true);
    setAgentSteps([]);
    setRunningStepIdx(-1);

    // Optimistic user message
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);

    const agentReply = await aiService.sendMessage(text);
    await runStepAnimation(agentReply.steps ?? []);

    setMessages((prev) => [...prev, agentReply]);
    setAgentSteps([]);
    setRunningStepIdx(-1);
    setIsLoading(false);
  };

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSend();
  };

  const suggestions = [
    "Why is my baby waking frequently?",
    "What should Aarav eat now?",
    "When is next vaccination?",
    "Is Aarav's growth normal?",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-h-[calc(100vh-5rem)] -mx-6 -my-6 md:-mx-8">
      {/* Header */}
      <div className="flex-none border-b border-slate-200 bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">✨ Baby Care Agent</h2>
            <p className="text-xs text-white/70">Your AI Parenting Assistant — powered by KinNest</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-white/70 font-medium">Online</span>
          </div>
        </div>

        {/* AI Modules */}
        <div className="mt-3 flex flex-wrap gap-2">
          {Object.keys(AGENT_STEPS_LABELS).slice(0, 4).map((mod) => (
            <span key={mod} className="flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 text-[11px] font-medium text-white/80">
              <CheckCircle className="h-3 w-3 text-emerald-300" />
              {mod}
            </span>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-slate-50/80">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                msg.sender === 'user'
                  ? 'bg-violet-600 text-white'
                  : 'bg-gradient-to-br from-violet-500 to-indigo-600 text-white shadow-sm'
              }`}
            >
              {msg.sender === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>

            <div className={`max-w-[80%] space-y-2 ${msg.sender === 'user' ? 'items-end' : ''}`}>
              {/* Bubble */}
              <div
                className={`rounded-2xl px-4 py-3 text-sm ${
                  msg.sender === 'user'
                    ? 'bg-violet-600 text-white rounded-tr-none'
                    : 'bg-white border border-slate-100 text-slate-800 rounded-tl-none shadow-sm'
                }`}
              >
                {formatMessage(msg.text)}
              </div>

              {/* Agent modules used */}
              {msg.sender === 'agent' && msg.toolsUsed && msg.toolsUsed.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {msg.toolsUsed.map((tool) => (
                    <span
                      key={tool}
                      className="flex items-center gap-1 rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-semibold text-violet-600 border border-violet-100"
                    >
                      <CheckCircle className="h-2.5 w-2.5" />
                      {tool}
                    </span>
                  ))}
                </div>
              )}

              <p className="text-[10px] text-slate-400 px-1">{msg.timestamp}</p>
            </div>
          </div>
        ))}

        {/* Agent Activity Panel while loading */}
        {isLoading && agentSteps.length > 0 && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white shadow-sm">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl border border-violet-100 bg-white px-4 py-3 shadow-sm space-y-2 rounded-tl-none">
              <p className="text-xs font-semibold text-violet-700 mb-2">🤖 Agent Activity</p>
              {agentSteps.map((step, idx) => (
                <div key={idx} className={`flex items-center gap-2 text-xs transition-opacity ${idx <= runningStepIdx ? 'opacity-100' : 'opacity-30'}`}>
                  {idx < runningStepIdx ? (
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                  ) : idx === runningStepIdx ? (
                    <Loader2 className="h-3.5 w-3.5 text-violet-500 animate-spin shrink-0" />
                  ) : (
                    <span className="h-3.5 w-3.5 shrink-0 rounded-full border border-slate-200" />
                  )}
                  <span className={idx === runningStepIdx ? 'text-violet-700 font-medium' : 'text-slate-500'}>{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Simple typing indicator before steps appear */}
        {isLoading && agentSteps.length === 0 && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1.5 rounded-2xl border border-violet-100 bg-white px-4 py-3 shadow-sm rounded-tl-none">
              <span className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggestions (only when no input) */}
      {!isLoading && messages.length <= 1 && (
        <div className="flex-none border-t border-slate-100 bg-white px-4 py-3">
          <p className="text-xs text-slate-400 mb-2 font-medium">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => setInput(s)}
                className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700 hover:bg-violet-100 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Bar */}
      <div className="flex-none border-t border-slate-200 bg-white px-4 py-3">
        <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 focus-within:border-violet-400 focus-within:ring-2 focus-within:ring-violet-100 transition-all">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about feeding, sleep, growth, vaccinations..."
            className="flex-1 bg-transparent text-sm text-slate-800 placeholder-slate-400 outline-none"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600 text-white transition-colors hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
