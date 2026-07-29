import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { digitalTwinApi } from '../services/digitalTwinApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { Cpu, Activity, ShieldCheck, Zap, Sparkles, TrendingUp } from 'lucide-react';

export const DigitalTwin = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [twinState, setTwinState] = useState(null);

  useEffect(() => {
    const fetchTwin = async () => {
      setLoading(true);
      try {
        const res = await digitalTwinApi.getDigitalTwin(familyId);
        setTwinState(res);
      } catch (err) {
        console.error('Error fetching digital twin:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTwin();
  }, [familyId]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Cpu className="w-8 h-8 text-indigo-400 animate-pulse" />
            <span>Family Financial Digital Twin</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Continuously updated virtual model simulating household cash flows, obligations, and scenario projections.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400">Synchronizing Financial Digital Twin state...</div>
      ) : twinState ? (
        <>
          {/* Main Twin Status Banner */}
          <GlassCard glow={true} className="p-6 bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Active Simulator State</span>
                <h3 className="text-2xl font-black text-white mt-1">Digital Twin Synchronized</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Affordability Score: <span className="text-emerald-400 font-bold">{twinState.affordability_score || 85}/100</span>
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className="px-3 py-1.5 rounded-full text-xs font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Risk Level: {twinState.financial_risk_level || twinState.risk_level || 'LOW'}
                </span>
              </div>
            </div>
          </GlassCard>

          {/* Core Twin Dimensions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard>
              <div className="text-xs font-semibold text-slate-400 uppercase">Current Position</div>
              <div className="text-2xl font-black text-white mt-1">
                <AnimatedNumber value={twinState.current_financial_position?.available_balance ?? twinState.current_position?.net_monthly_surplus ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-1">Net monthly cash flow balance</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-slate-400 uppercase">Month-End Prediction</div>
              <div className="text-2xl font-black text-purple-400 mt-1">
                <AnimatedNumber value={twinState.month_end_prediction?.predicted_month_end ?? twinState.predicted_month_end ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-1">Projected month-end balance</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-slate-400 uppercase">Emergency Reserve Status</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">
                {twinState.emergency_reserve_status || twinState.emergency_reserve?.reserve_status || 'Sufficient'}
              </div>
              <p className="text-xs text-slate-400 mt-1">Safety buffer status</p>
            </GlassCard>
          </div>

          {/* Recommended Actions */}
          {twinState.recommended_actions && twinState.recommended_actions.length > 0 && (
            <GlassCard className="p-6">
              <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <span>Digital Twin Recommendations</span>
              </h3>
              <div className="space-y-2">
                {twinState.recommended_actions.map((act, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-sm text-slate-300 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 shrink-0" />
                    <span>{typeof act === 'string' ? act : act.action || act.description}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}
        </>
      ) : (
        <div className="py-12 text-center text-slate-400">No Digital Twin state available for family #{familyId}.</div>
      )}
    </div>
  );
};

export default DigitalTwin;
