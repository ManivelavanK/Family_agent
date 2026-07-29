import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { safeToSpendApi } from '../services/safeToSpendApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { ShieldCheck, Calculator, ArrowRight, CheckCircle2, AlertTriangle, Sparkles, HelpCircle } from 'lucide-react';

export const SafeToSpend = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  // Interactive Affordability Evaluator state
  const [checkAmount, setCheckAmount] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);

  const fetchSafeToSpend = async () => {
    setLoading(true);
    try {
      const res = await safeToSpendApi.getSafeToSpend(familyId);
      setData(res);
    } catch (err) {
      console.error('Error fetching safe to spend:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSafeToSpend();
  }, [familyId]);

  const handleEvaluate = async (e) => {
    e.preventDefault();
    if (!checkAmount || Number(checkAmount) <= 0) return;

    setEvaluating(true);
    setEvalResult(null);
    try {
      const result = await safeToSpendApi.checkAffordability(familyId, checkAmount);
      setEvalResult(result);
    } catch (err) {
      console.error('Error evaluating affordability:', err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-emerald-400" />
            <span>Safe to Spend Intelligence</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time safe spending threshold deducting pending bills, savings goals, and emergency reserves.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400">Computing safe-to-spend allowance...</div>
      ) : data ? (
        <>
          {/* Main Allowances Hero Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard glow={true} className="p-6 border-emerald-500/30">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Safe to Spend Today</span>
              <div className="text-4xl font-black text-white mt-1">
                <AnimatedNumber value={data.safe_to_spend_today ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-2">Daily uncommitted allowance</p>
            </GlassCard>

            <GlassCard className="p-6">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Safe to Spend This Week</span>
              <div className="text-3xl font-black text-slate-100 mt-1">
                <AnimatedNumber value={data.safe_to_spend_this_week ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-2">Weekly budget capacity</p>
            </GlassCard>

            <GlassCard className="p-6">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Safe to Spend This Month</span>
              <div className="text-3xl font-black text-blue-400 mt-1">
                <AnimatedNumber value={data.safe_to_spend_this_month ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-2">Total unencumbered monthly balance</p>
            </GlassCard>
          </div>

          {/* Breakdown Equation Card */}
          <GlassCard className="p-6 space-y-4">
            <h3 className="text-lg font-bold text-white mb-2">Calculation Model Breakdown</h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Total Income</span>
                <div className="text-base font-bold text-emerald-400 mt-0.5">
                  +₹{Number(data.total_monthly_income || 0).toLocaleString('en-IN')}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Expenses Logged</span>
                <div className="text-base font-bold text-rose-400 mt-0.5">
                  -₹{Number(data.total_monthly_expenses || 0).toLocaleString('en-IN')}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Pending Bills</span>
                <div className="text-base font-bold text-amber-400 mt-0.5">
                  -₹{Number(data.pending_bills_amount || 0).toLocaleString('en-IN')}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Available Net</span>
                <div className="text-base font-bold text-blue-400 mt-0.5">
                  =₹{Number(data.available_balance || 0).toLocaleString('en-IN')}
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Interactive "Can I Afford This?" Purchase Evaluator */}
          <GlassCard glow={true} className="p-6 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/30">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400">
                <Calculator className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Can I Afford This Purchase?</h3>
                <p className="text-xs text-slate-400">Enter an intended purchase amount to run real-time decision agent evaluation.</p>
              </div>
            </div>

            <form onSubmit={handleEvaluate} className="flex flex-col sm:flex-row items-center gap-4 max-w-lg">
              <div className="relative w-full">
                <span className="absolute left-3.5 top-3 text-slate-400 font-bold text-sm">₹</span>
                <input
                  type="number"
                  required
                  placeholder="e.g. 5000"
                  value={checkAmount}
                  onChange={(e) => setCheckAmount(e.target.value)}
                  className="w-full pl-8 pr-4 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <button
                type="submit"
                disabled={evaluating}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-500/25 shrink-0 flex items-center justify-center gap-2"
              >
                {evaluating ? (
                  <span>Evaluating...</span>
                ) : (
                  <>
                    <span>Evaluate</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Evaluation Result Display */}
            {evalResult && (
              <div className="mt-6 p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider ${
                        evalResult.decision === 'AFFORDABLE'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      }`}
                    >
                      {evalResult.decision}
                    </span>
                    <span className="text-xs text-slate-400">Confidence: {((evalResult.confidence || 0.9) * 100).toFixed(0)}%</span>
                  </div>

                  <span className="text-xs font-bold text-slate-300">Risk Level: {evalResult.risk_level}</span>
                </div>

                <p className="text-sm font-semibold text-white">{evalResult.reason}</p>
                {evalResult.financial_impact && (
                  <p className="text-xs text-slate-400">Impact: {evalResult.financial_impact}</p>
                )}
                {evalResult.recommended_action && (
                  <p className="text-xs text-emerald-400 font-medium">Recommendation: {evalResult.recommended_action}</p>
                )}
              </div>
            )}
          </GlassCard>
        </>
      ) : (
        <div className="py-12 text-center text-slate-400">No safe-to-spend calculation available.</div>
      )}
    </div>
  );
};

export default SafeToSpend;
