import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { predictionApi } from '../services/predictionApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { Sparkles, TrendingUp, Cpu, AlertCircle, ShieldCheck } from 'lucide-react';

export const Predictions = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      setLoading(true);
      try {
        const res = await predictionApi.getSpendingPrediction(familyId);
        setData(res);
      } catch (err) {
        console.error('Error loading prediction:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [familyId]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-[#0F766E]" />
            <span>ML Spending Predictions</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Machine learning spending forecasting based on historical transaction velocity.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-[#627D98]">ML model running month-end forecasting...</div>
      ) : data ? (
        <>
          {/* Main Forecast Hero */}
          <div className="p-6 rounded-2xl kinnest-ai-panel border border-[#0F766E]/30 relative overflow-hidden">
            <div className="absolute -top-12 -right-12 w-28 h-28 bg-[#0F766E]/15 rounded-full blur-xl pointer-events-none" />
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#0F766E]/20 text-emerald-300 border border-[#0F766E]/30 mb-3">
                  <Cpu className="w-3.5 h-3.5 animate-pulse" />
                  <span>ML Linear Trajectory Model</span>
                </div>
                <h3 className="text-slate-300 text-sm font-medium">Forecasted Month-End Total</h3>
                <div className="text-4xl sm:text-5xl font-black text-white mt-1">
                  <AnimatedNumber value={data.predicted_month_end ?? 0} />
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Based on {data.days_recorded || 30} days of recorded spending activity
                </p>
              </div>

              <div className="flex flex-col gap-3">
                <div className="p-4 rounded-xl bg-[#102A43] border border-[#243B53] text-center">
                  <span className="text-xs text-slate-400 uppercase">Model Confidence</span>
                  <div className="text-2xl font-black text-[#D4A72C] mt-0.5">
                    {((data.confidence || 0.85) * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase">Current Month Spending</div>
              <div className="text-3xl font-black text-[#102A43] mt-1">
                <AnimatedNumber value={data.current_spending ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Real ledger spent to date</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase">Expected Additional Spend</div>
              <div className="text-3xl font-black text-[#0F766E] mt-1">
                <AnimatedNumber value={Math.max((data.predicted_month_end || 0) - (data.current_spending || 0), 0)} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Projected before month end</p>
            </GlassCard>
          </div>

          {/* AI Prediction Advice Banner */}
          {data.advice && (
            <GlassCard className="p-6">
              <h3 className="text-base font-bold text-[#102A43] mb-2 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#0F766E]" />
                <span>Prediction Advisory</span>
              </h3>
              <p className="text-sm text-[#172B4D] leading-relaxed">{data.advice}</p>
            </GlassCard>
          )}
        </>
      ) : (
        <div className="py-12 text-center text-[#627D98]">No spending prediction available for family #{familyId}.</div>
      )}
    </div>
  );
};

export default Predictions;
