import React from 'react';
import { Sparkles, Terminal, Activity } from 'lucide-react';

interface ActivityPanelProps {
  steps: string[];
  loading: boolean;
}

export const ActivityPanel: React.FC<ActivityPanelProps> = ({ steps, loading }) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-900 text-slate-100 p-6 shadow-md relative overflow-hidden">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
        <Terminal className="h-4.5 w-4.5 text-indigo-400" />
        <h3 className="font-bold text-sm text-slate-200">Agent Activity Monitor</h3>
      </div>

      {loading ? (
        <div className="space-y-3 py-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
            <Activity className="h-4 w-4 animate-pulse" />
            <span>Agent executing pipeline...</span>
          </div>
          <div className="space-y-2 opacity-50">
            <div className="h-4 bg-slate-800 rounded w-3/4 animate-pulse"></div>
            <div className="h-4 bg-slate-800 rounded w-1/2 animate-pulse"></div>
            <div className="h-4 bg-slate-800 rounded w-5/6 animate-pulse"></div>
          </div>
        </div>
      ) : steps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center text-slate-500">
          <Sparkles className="h-6 w-6 mb-2 text-slate-600" />
          <p className="text-xs font-semibold">Ready for User Prompt</p>
          <p className="text-[10px] mt-1 text-slate-600 max-w-[200px]">Ask "What should I buy this week?" to view agent reasoning logs.</p>
        </div>
      ) : (
        <div className="space-y-3.5 max-h-[400px] overflow-y-auto">
          {steps.map((step, idx) => {
            const isCompleted = idx < steps.length - 1 || steps.length === 6; // mock finality check
            return (
              <div key={idx} className="flex gap-3 text-xs leading-relaxed font-mono">
                <span className="text-slate-55 select-none">{idx + 1}.</span>
                <div>
                  <span className={isCompleted ? 'text-slate-300' : 'text-indigo-400 font-bold'}>
                    {step}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
export default ActivityPanel;
