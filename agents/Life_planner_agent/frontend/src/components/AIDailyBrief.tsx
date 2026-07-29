import { Sparkles, Bot, ArrowRight } from 'lucide-react';

interface AIDailyBriefProps {
  bullets?: string[];
  onOpenAiPlanner: () => void;
}

export default function AIDailyBrief({ bullets, onOpenAiPlanner }: AIDailyBriefProps) {
  const defaultBullets = [
    "You have three high-priority tasks today.",
    "Shopping should be completed before 6 PM.",
    "Your child has an exam tomorrow.",
    "Electricity bill is due in two days."
  ];

  const displayBullets = bullets && bullets.length > 0 ? bullets : defaultBullets;

  return (
    <div className="dark-panel p-6 relative overflow-hidden flex flex-col justify-between h-full shadow-lg border border-[#1D3A5F]">
      <div className="absolute right-0 bottom-0 w-48 h-48 bg-[#7C3AED]/5 rounded-full blur-2xl"></div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-[#7C3AED]" />
            <div>
              <h4 className="text-xs uppercase font-extrabold tracking-wider text-slate-300">AI Daily Brief</h4>
              <p className="text-[9px] text-[#7C3AED] font-semibold tracking-wide uppercase">Powered by Groq</p>
            </div>
          </div>
          <span className="px-2 py-0.5 rounded bg-[#7C3AED]/25 text-[#A78BFA] text-[9px] font-bold border border-[#7C3AED]/35 flex items-center gap-1">
            <Sparkles className="h-3 w-3" /> Real-time
          </span>
        </div>

        {/* Dynamic bullet items */}
        <div className="space-y-2.5">
          {displayBullets.map((bullet, idx) => (
            <div key={idx} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed font-medium">
              <span className="h-1.5 w-1.5 rounded-full bg-[#7C3AED] mt-1.5 shrink-0"></span>
              <p>{bullet}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-5 border-t border-white/5 mt-4">
        <button
          onClick={onOpenAiPlanner}
          className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition border border-white/10"
        >
          Consult AI Planner <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
