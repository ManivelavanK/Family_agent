import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../../types/ai';
import { Send, Sparkles, Loader2, Check } from 'lucide-react';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  loading: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  loading
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    'What should I buy this week?',
    'Tell me about food waste this month',
    'How is my grocery budget looking?'
  ];

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  // Scroll to bottom whenever messages load or append
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex flex-col h-[500px] border border-slate-200 rounded-2xl bg-white overflow-hidden shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/50 px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold">
            ✨
          </div>
          <div>
            <h3 className="font-bold text-slate-800 text-sm">Mother Agent</h3>
            <span className="block text-[10px] font-medium text-slate-400">Household & Grocery Intelligence</span>
          </div>
        </div>
      </div>

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => {
          const isAgent = msg.sender === 'agent';
          return (
            <div key={msg.id} className={`flex ${isAgent ? 'justify-start' : 'justify-end'}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed border shadow-2xs
                ${isAgent 
                  ? 'bg-slate-55/40 text-slate-800 border-slate-100 rounded-tl-none' 
                  : 'bg-indigo-600 text-white border-indigo-500 rounded-tr-none'}
              `}>
                <p className="font-medium whitespace-pre-line">{msg.text}</p>
                
                {/* Tools Used section */}
                {isAgent && msg.toolsUsed && msg.toolsUsed.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200/60">
                    <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-2">Agents & tools used:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.toolsUsed.map((tool, idx) => (
                        <span key={idx} className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                          <Check className="h-3 w-3" />
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <span className={`block text-[9px] mt-1.5 text-right font-medium
                  ${isAgent ? 'text-slate-400' : 'text-indigo-200'}
                `}>
                  {msg.timestamp}
                </span>
              </div>
            </div>
          );
        })}

        {/* Typing loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl p-4 bg-slate-50 border border-slate-150 rounded-tl-none text-slate-500 text-xs font-semibold flex items-center gap-2 shadow-2xs">
              <Loader2 className="h-4.5 w-4.5 animate-spin text-indigo-600" />
              <span>✨ Mother Agent is analyzing your household...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick suggestions */}
      {!loading && messages.length <= 1 && (
        <div className="px-6 pb-2 pt-1.5 border-t border-slate-50 flex flex-wrap gap-2 justify-center">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt)}
              className="text-[11px] font-semibold text-indigo-600 bg-indigo-50/50 hover:bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100/50 transition-colors cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSend} className="flex border-t border-slate-150 p-4 gap-3 bg-white">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={loading ? 'Mother Agent is thinking...' : 'Ask Mother Agent about your pantry, budgets, or recipes...'}
          className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none bg-slate-50/50 focus:bg-white transition-colors"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={!inputText.trim() || loading}
          className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-100 disabled:bg-slate-200 disabled:shadow-none active:scale-95 transition-all cursor-pointer"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};
export default ChatInterface;
