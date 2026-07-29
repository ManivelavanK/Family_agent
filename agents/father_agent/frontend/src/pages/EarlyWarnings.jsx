import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { earlyWarningApi } from '../services/earlyWarningApi';
import { GlassCard } from '../components/ui/GlassCard';
import { ShieldAlert, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const EarlyWarnings = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchWarnings = async () => {
      setLoading(true);
      try {
        const res = await earlyWarningApi.getEarlyWarnings(familyId);
        setData(res);
      } catch (err) {
        console.error('Error fetching early warnings:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWarnings();
  }, [familyId]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-rose-400" />
            <span>Early Warning System</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Proactive cash-flow risk analysis, budget exhaustion velocity, and goal deficit warnings.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400">Evaluating proactive early warnings...</div>
      ) : data ? (
        <div className="space-y-4">
          <GlassCard glow={true}>
            <span className="text-xs font-bold text-slate-400 uppercase">Warning Count</span>
            <div className="text-3xl font-black text-white mt-1">
              {data.warnings ? data.warnings.length : 0} Active Early Warnings
            </div>
          </GlassCard>

          {data.warnings && data.warnings.length > 0 ? (
            <div className="space-y-4">
              {data.warnings.map((warn, idx) => (
                <GlassCard key={idx} className="p-5 border-l-4 border-l-rose-500">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-white text-base">{warn.warning_type || warn.title || 'Financial Risk Warning'}</h4>
                      <p className="text-sm text-slate-300 mt-1">{warn.message || warn.description}</p>
                      {warn.recommended_action && (
                        <p className="text-xs text-emerald-400 mt-2 font-semibold">Action: {warn.recommended_action}</p>
                      )}
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>
          ) : (
            <GlassCard className="py-12 text-center text-slate-400">
              <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-emerald-400 opacity-80" />
              <span className="text-slate-200 font-semibold">No early warnings triggered!</span>
              <p className="text-xs text-slate-400 mt-1">Your financial health, budget velocity, and cash flows are completely stable.</p>
            </GlassCard>
          )}
        </div>
      ) : (
        <div className="py-12 text-center text-slate-400">No early warning data available.</div>
      )}
    </div>
  );
};

export default EarlyWarnings;
