import React, { useState } from 'react';
import { useFamily } from '../context/FamilyContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Bot, ShieldCheck, ShieldAlert, Shield, ShoppingCart, HelpCircle, Check, X, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CATEGORIES = [
  'Food & Groceries',
  'Housing & Rent',
  'Utilities & Bills',
  'Transportation',
  'Shopping & Lifestyle',
  'Electronics & Tech',
  'Entertainment & Leisure',
  'Healthcare & Fitness',
  'Education',
  'Miscellaneous'
];

export const AskBeforeSpend = () => {
  const { familyId } = useFamily();
  const [purchaseName, setPurchaseName] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(false);

  const handleEvaluate = async (e) => {
    e.preventDefault();
    if (!purchaseName || !amount || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setActionSuccess(false);

    try {
      const res = await fetch(`http://localhost:8000/finance/ask-before-spend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          family_id: familyId,
          purchase_name: purchaseName,
          amount: parseFloat(amount),
          category: category
        })
      });

      if (!res.ok) throw new Error('Failed to evaluate purchase');
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to connect to the evaluation guardian. Ensure the backend is online.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecord = async () => {
    if (!result || actionLoading) return;
    setActionLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/finance/action/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          family_id: familyId,
          action_type: 'create_expense',
          payload: {
            category: category,
            description: `AI Purchase: ${purchaseName}`,
            amount: parseFloat(amount),
            expense_date: new Date().toISOString().split('T')[0]
          }
        })
      });

      if (!res.ok) throw new Error('Failed to record purchase');
      setActionSuccess(true);
      setTimeout(() => {
        // Reset form
        setPurchaseName('');
        setAmount('');
        setResult(null);
        setActionSuccess(false);
      }, 2000);
    } catch (err) {
      console.error(err);
      setError('Failed to record purchase. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  const getDecisionBadge = (decision) => {
    switch (decision) {
      case 'SAFE':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-bold uppercase tracking-wider">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>SAFE</span>
          </div>
        );
      case 'CAUTION':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm font-bold uppercase tracking-wider">
            <Shield className="w-5 h-5 text-amber-400 animate-pulse" />
            <span>CAUTION</span>
          </div>
        );
      case 'NOT RECOMMENDED':
      default:
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm font-bold uppercase tracking-wider">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>NOT RECOMMENDED</span>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
          <Bot className="w-8 h-8 text-[#0F766E]" />
          <span>Ask Before I Spend</span>
        </h1>
        <p className="text-[#627D98] text-sm mt-1">
          Consult the Father Agent to evaluate the short and long term impacts of a prospective purchase.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form Column */}
        <div className="lg:col-span-5">
          <GlassCard className="p-6 border border-[#243B53]/20 text-slate-100">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 mb-4">
              <ShoppingCart className="w-5 h-5 text-[#D4A72C]" />
              <span>Purchase Details</span>
            </h2>
            <form onSubmit={handleEvaluate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Purchase Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Smartwatch, Grocery Bulk..."
                  value={purchaseName}
                  onChange={(e) => setPurchaseName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0F2942] border border-[#243B53] text-white text-sm focus:outline-none focus:border-[#0F766E]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  placeholder="e.g. 15000"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0F2942] border border-[#243B53] text-white text-sm focus:outline-none focus:border-[#0F766E]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0F2942] border border-[#243B53] text-white text-sm focus:outline-none focus:border-[#0F766E]"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-[#0F766E] hover:bg-emerald-600 disabled:opacity-50 text-white font-bold shadow-lg shadow-[#0f766e]/25 transition-all cursor-pointer flex items-center justify-center gap-2 mt-6"
              >
                {loading ? 'Evaluating AFFORDABILITY...' : 'Consult Guardian'}
              </button>
            </form>
          </GlassCard>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-7">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm"
              >
                {error}
              </motion.div>
            )}

            {!result && !loading && !error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full min-h-[300px] flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-700 rounded-2xl"
              >
                <HelpCircle className="w-12 h-12 text-slate-500 mb-3" />
                <h3 className="text-base font-semibold text-slate-300">Awaiting consultation</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-sm">
                  Fill in the purchase name, amount, and category on the left to invoke the Guardian.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full min-h-[300px] flex flex-col items-center justify-center text-center p-6"
              >
                <div className="w-10 h-10 rounded-xl bg-[#0F766E]/20 flex items-center justify-center mb-3">
                  <div className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                </div>
                <h3 className="text-base font-semibold text-slate-200">Father Agent Reasoning...</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Querying recent transactions, budget utilization, and future bill obligations.
                </p>
              </motion.div>
            )}

            {result && !loading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-6"
              >
                {/* Guardian Decision Card */}
                <GlassCard className="p-6 border border-[#243B53]/30">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#243B53]/40 pb-4 mb-4">
                    <div>
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                        Guardian Decision
                      </span>
                      <h3 className="text-lg font-extrabold text-white mt-0.5">
                        {purchaseName} — ₹{parseFloat(amount).toLocaleString()}
                      </h3>
                    </div>
                    {getDecisionBadge(result.decision)}
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-xs font-bold text-[#D4A72C] uppercase tracking-wider flex items-center gap-1.5 mb-1">
                        <Info className="w-3.5 h-3.5" />
                        <span>Recommendation Summary</span>
                      </h4>
                      <p className="text-sm text-slate-200">{result.recommendation}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                      <div className="p-3.5 rounded-xl bg-[#0F2942]/60 border border-[#243B53]/30">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Why?
                        </span>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">{result.why}</p>
                      </div>

                      <div className="p-3.5 rounded-xl bg-[#0F2942]/60 border border-[#243B53]/30">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Financial Impact
                        </span>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">{result.financial_impact}</p>
                      </div>

                      <div className="p-3.5 rounded-xl bg-[#0F2942]/60 border border-[#243B53]/30">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Goal Impact
                        </span>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">{result.goal_impact}</p>
                      </div>

                      <div className="p-3.5 rounded-xl bg-[#0F2942]/60 border border-[#243B53]/30">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Commitments
                        </span>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">{result.relevant_commitments}</p>
                      </div>
                    </div>

                    <div className="border-t border-[#243B53]/40 pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-[10px] font-bold text-slate-400 uppercase">Considered Data:</span>
                        {result.data_considered && result.data_considered.map((d, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-[#0F766E]/20 text-[#38BDF8] text-[10px] font-bold uppercase border border-[#0F766E]/30">
                            {d}
                          </span>
                        ))}
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => setResult(null)}
                          className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 text-xs font-semibold hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-1.5"
                        >
                          <X className="w-3.5 h-3.5" />
                          <span>Cancel</span>
                        </button>
                        <button
                          onClick={handleRecord}
                          disabled={actionLoading || actionSuccess}
                          className="px-4 py-2 rounded-xl bg-[#0F766E] hover:bg-emerald-600 text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-lg shadow-[#0f766e]/20"
                        >
                          {actionLoading ? (
                            <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
                          ) : actionSuccess ? (
                            <Check className="w-3.5 h-3.5 text-emerald-300" />
                          ) : (
                            <Check className="w-3.5 h-3.5" />
                          )}
                          <span>{actionSuccess ? 'Recorded!' : 'Record Purchase'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default AskBeforeSpend;
