import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Cpu, Wrench, Database, Zap, Brain } from 'lucide-react';

export default function AIExecutionLog({ data, compact = false }) {
  const [open, setOpen] = useState(!compact);

  if (!data || !data.intent) return null;

  const { intent, agents_used = [], tools_used = [], data_sources = [], memory_used = [] } = data;

  const sections = [
    { label: 'Intent',     icon: Brain,    items: [intent],    color: 'text-violet-400 bg-violet-500/10 border-violet-500/20' },
    { label: 'Agents',     icon: Cpu,      items: agents_used, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'  },
    { label: 'Tools',      icon: Wrench,   items: tools_used,  color: 'text-cyan-400   bg-cyan-500/10   border-cyan-500/20'    },
    { label: 'Data',       icon: Database, items: data_sources,color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'},
    { label: 'Memory',     icon: Zap,      items: memory_used, color: 'text-amber-400  bg-amber-500/10  border-amber-500/20'   },
  ].filter(s => s.items.length > 0);

  return (
    <div className="glass-dark rounded-2xl border border-white/8 overflow-hidden text-white">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-white/4 transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Supervisor Execution Trace</span>
        </div>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 border-t border-white/8 pt-4">
              {sections.map(({ label, icon: Icon, items, color }) => (
                <div key={label} className={`rounded-xl border p-3 ${color} bg-opacity-10`}>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Icon size={12} />
                    <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">{label}</span>
                  </div>
                  <div className="space-y-1">
                    {items.map((item, i) => (
                      <div key={i} className="text-[11px] font-medium text-white/80 truncate" title={item}>
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
