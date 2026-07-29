import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { savingsApi } from '../services/savingsApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { Target, Sparkles, TrendingUp, AlertCircle, ShieldCheck, CheckCircle2, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

export const Savings = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchSavings = async () => {
      setLoading(true);
      try {
        const res = await savingsApi.getSavingsRecommendation(familyId);
        setData(res);
      } catch (err) {
        console.error('Error fetching savings recommendation:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSavings();
  }, [familyId]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <Target className="w-8 h-8 text-[#0F766E]" />
            <span>Savings & Goals AI</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Autonomous target tracking, reserve optimization, and Groq-powered savings advice.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-[#627D98]">Father Agent is calculating savings recommendations...</div>
      ) : data ? (
        <>
          {/* AI Recommendation Hero Card */}
          <div className="p-6 rounded-2xl kinnest-ai-panel border border-[#0F766E]/30 relative overflow-hidden">
            <div className="absolute -top-12 -right-12 w-28 h-28 bg-[#0F766E]/15 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-start gap-4 relative z-10">
              <div className="p-3 rounded-2xl bg-[#0F766E]/20 text-[#D4A72C] shrink-0">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#0F766E]/20 text-emerald-300 border border-[#0F766E]/30">
                  <span>✦ Father AI Savings Recommendation</span>
                </div>
                <h3 className="text-lg font-bold text-white">Autonomous Savings Strategy</h3>
                <p className="text-sm text-slate-200 leading-relaxed">
                  {data.recommendation}
                </p>
              </div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Total Spent</div>
              <div className="text-2xl font-black text-[#102A43] mt-1">
                <AnimatedNumber value={data.total_spent ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Highest spending in {data.highest_category || 'N/A'}</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Budget Remaining</div>
              <div className="text-2xl font-black text-[#2F855A] mt-1">
                <AnimatedNumber value={data.budget_remaining ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Available for savings</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Pending Bills</div>
              <div className="text-2xl font-black text-[#D97706] mt-1">
                <AnimatedNumber value={data.pending_bill_amount ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Short term obligations</p>
            </GlassCard>

            <GlassCard>
              <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Predicted Month-End</div>
              <div className="text-2xl font-black text-[#0F766E] mt-1">
                <AnimatedNumber value={data.predicted_month_end ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-1">Confidence: {((data.prediction_confidence || 0.85) * 100).toFixed(0)}%</p>
            </GlassCard>
          </div>

          {/* Sample Active Goals Showcase */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-[#102A43]">Active Family Goals</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <GlassCard>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-bold text-[#172B4D] text-base">Emergency Buffer Reserve</h4>
                    <span className="text-xs text-[#627D98]">Target: ₹1,00,000</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#2F855A]/10 text-[#2F855A] border border-[#2F855A]/25">
                    65% Reached
                  </span>
                </div>
                <div className="space-y-1 mt-4">
                  <div className="h-3 w-full bg-[#F7F9FC] rounded-full overflow-hidden border border-[#D9E2EC]">
                    <div className="h-full w-[65%] bg-[#2F855A] rounded-full" />
                  </div>
                  <div className="flex justify-between text-xs text-[#627D98] pt-1">
                    <span>Current: ₹65,000</span>
                    <span>Target: ₹1,00,000</span>
                  </div>
                </div>
              </GlassCard>

              <GlassCard>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-bold text-[#172B4D] text-base">Family Vacation Fund</h4>
                    <span className="text-xs text-[#627D98]">Target: ₹50,000</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#D4A72C]/15 text-[#D4A72C] border border-[#D4A72C]/30">
                    42% Reached
                  </span>
                </div>
                <div className="space-y-1 mt-4">
                  <div className="h-3 w-full bg-[#F7F9FC] rounded-full overflow-hidden border border-[#D9E2EC]">
                    <div className="h-full w-[42%] bg-[#D4A72C] rounded-full" />
                  </div>
                  <div className="flex justify-between text-xs text-[#627D98] pt-1">
                    <span>Current: ₹21,000</span>
                    <span>Target: ₹50,000</span>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        </>
      ) : (
        <div className="py-12 text-center text-slate-400">No savings data available for family #{familyId}.</div>
      )}
    </div>
  );
};

export default Savings;
