import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { financeApi } from '../services/financeApi';
import { safeToSpendApi } from '../services/safeToSpendApi';
import { healthScoreApi } from '../services/healthScoreApi';
import { expenseApi } from '../services/expenseApi';
import { billApi } from '../services/billApi';
import { earlyWarningApi } from '../services/earlyWarningApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { HealthScoreGauge } from '../components/ui/HealthScoreGauge';
import { NavLink } from 'react-router-dom';

import {
  Wallet,
  TrendingUp,
  CreditCard,
  ShieldCheck,
  Sparkles,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  ChevronRight,
  Bot,
  Activity,
  Calendar,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const Dashboard = () => {
  const { familyId, refreshCount } = useFamily();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [financialSummary, setFinancialSummary] = useState(null);
  const [safeToSpend, setSafeToSpend] = useState(null);
  const [healthScore, setHealthScore] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [upcomingBills, setUpcomingBills] = useState([]);
  const [earlyWarnings, setEarlyWarnings] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [summaryRes, stsRes, healthRes, expRes, billRes, ewRes] = await Promise.allSettled([
          financeApi.getFinancialSummary(familyId),
          safeToSpendApi.getSafeToSpend(familyId),
          healthScoreApi.getHealthScore(familyId),
          expenseApi.getExpenses(familyId),
          billApi.getUpcomingBills(familyId),
          earlyWarningApi.getEarlyWarnings(familyId),
        ]);

        if (summaryRes.status === 'fulfilled') setFinancialSummary(summaryRes.value);
        if (stsRes.status === 'fulfilled') setSafeToSpend(stsRes.value);
        if (healthRes.status === 'fulfilled') setHealthScore(healthRes.value);
        if (expRes.status === 'fulfilled') setExpenses(expRes.value);
        if (billRes.status === 'fulfilled') setUpcomingBills(billRes.value);
        if (ewRes.status === 'fulfilled') setEarlyWarnings(ewRes.value);

      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError('Failed to sync with Father Agent backend');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [familyId, refreshCount]);

  // Transform recent expenses for spending trend mini chart
  const trendData = React.useMemo(() => {
    if (!expenses || expenses.length === 0) return [];
    const sorted = [...expenses].reverse();
    return sorted.map((e) => ({
      date: e.expense_date,
      amount: Number(e.amount),
      category: e.category,
    }));
  }, [expenses]);

  return (
    <div className="space-y-8">
      {/* Header Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight">
              Good evening, Father 👋
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/20">
              Family #{familyId}
            </span>
          </div>
          <p className="text-[#627D98] text-sm mt-1">
            Welcome back. Here is your family's real-time financial intelligence workspace.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <NavLink
            to="/ai-advisor"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#102A43] via-[#243B53] to-[#0F766E] text-white font-medium text-sm shadow-lg shadow-[#102A43]/10 hover:shadow-[#102A43]/20 transition-all hover:scale-[1.02]"
          >
            <Bot className="w-4 h-4 animate-bounce" />
            <span>Consult Father AI</span>
          </NavLink>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-36 rounded-2xl bg-white border border-[#D9E2EC]" />
          ))}
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-[#C53030]/10 border border-[#C53030]/30 text-[#C53030] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-6 h-6 shrink-0" />
            <span>{error}. Please check if the FastAPI backend is running on port 8000.</span>
          </div>
        </div>
      ) : (
        <>
          {/* Hero Section: Financial Health Score + Safe To Spend + Monthly Surplus */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Health Score Card */}
            <GlassCard className="lg:col-span-4 flex flex-col items-center justify-center p-6 text-center" glow={true}>
              <div className="w-full flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-[#627D98]">
                  Financial Health
                </span>
                <Activity className="w-4 h-4 text-[#0F766E]" />
              </div>
              <HealthScoreGauge
                score={healthScore?.score ?? 80}
                status={healthScore?.status ?? 'Healthy'}
                size={170}
              />
              <div className="mt-4 w-full pt-4 border-t border-[#D9E2EC] flex items-center justify-around text-xs">
                <div>
                  <div className="text-[#627D98]">Bills</div>
                  <div className="font-semibold text-[#172B4D]">{healthScore?.bill_score ?? 30}/30</div>
                </div>
                <div className="h-6 w-[1px] bg-[#D9E2EC]" />
                <div>
                  <div className="text-[#627D98]">Budget</div>
                  <div className="font-semibold text-[#172B4D]">{healthScore?.budget_score ?? 40}/40</div>
                </div>
                <div className="h-6 w-[1px] bg-[#D9E2EC]" />
                <div>
                  <div className="text-[#627D98]">Expenses</div>
                  <div className="font-semibold text-[#172B4D]">{healthScore?.expense_score ?? 30}/30</div>
                </div>
              </div>
            </GlassCard>

            {/* Safe To Spend Hero Card */}
            <GlassCard className="lg:col-span-8 flex flex-col justify-between p-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/20 mb-3">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Real-time Allowance</span>
                  </div>
                  <h3 className="text-[#627D98] text-sm font-medium">Safe to Spend Today</h3>
                  <div className="text-4xl sm:text-5xl font-black text-[#102A43] mt-1">
                    <AnimatedNumber value={safeToSpend?.safe_to_spend_today ?? financialSummary?.safe_to_spend_today ?? 0} />
                  </div>
                </div>

                <NavLink
                  to="/safe-to-spend"
                  className="p-2.5 rounded-xl bg-[#F7F9FC] hover:bg-[#D9E2EC] text-[#102A43] border border-[#D9E2EC] transition-colors"
                >
                  <ArrowUpRight className="w-5 h-5" />
                </NavLink>
              </div>

              {/* Safe to Spend Sub Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-[#D9E2EC]">
                <div>
                  <span className="text-xs text-[#627D98]">Safe this Month</span>
                  <div className="text-lg font-bold text-[#172B4D] mt-0.5">
                    <AnimatedNumber value={safeToSpend?.safe_to_spend_this_month ?? 0} />
                  </div>
                </div>
                <div>
                  <span className="text-xs text-[#627D98]">Monthly Surplus</span>
                  <div className="text-lg font-bold text-[#2F855A] mt-0.5">
                    <AnimatedNumber value={financialSummary?.net_monthly_surplus ?? safeToSpend?.available_balance ?? 0} />
                  </div>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <span className="text-xs text-[#627D98]">Risk Level</span>
                  <div className="text-sm font-bold text-[#172B4D] mt-1 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#2F855A] animate-pulse" />
                    <span className="uppercase">{financialSummary?.financial_risk_level || 'LOW'}</span>
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard delay={0.1}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase text-[#627D98]">Total Income</span>
                <div className="p-2.5 rounded-xl bg-[#2F855A]/10 text-[#2F855A]">
                  <TrendingUp className="w-5 h-5" />
                </div>
              </div>
              <div className="text-2xl font-black text-[#102A43]">
                <AnimatedNumber value={safeToSpend?.total_monthly_income ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-2">Verified income records</p>
            </GlassCard>

            <GlassCard delay={0.2}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase text-[#627D98]">Total Expenses</span>
                <div className="p-2.5 rounded-xl bg-[#C53030]/10 text-[#C53030]">
                  <Wallet className="w-5 h-5" />
                </div>
              </div>
              <div className="text-2xl font-black text-[#102A43]">
                <AnimatedNumber value={safeToSpend?.total_monthly_expenses ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-2">Spent this month</p>
            </GlassCard>

            <GlassCard delay={0.3}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase text-[#627D98]">Pending Bills</span>
                <div className="p-2.5 rounded-xl bg-[#D97706]/10 text-[#D97706]">
                  <CreditCard className="w-5 h-5" />
                </div>
              </div>
              <div className="text-2xl font-black text-[#102A43]">
                <AnimatedNumber value={safeToSpend?.pending_bills_amount ?? 0} />
              </div>
              <p className="text-xs text-[#627D98] mt-2">{upcomingBills.length} upcoming bills</p>
            </GlassCard>

            <GlassCard delay={0.4}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase text-[#627D98]">Reserve Status</span>
                <div className="p-2.5 rounded-xl bg-[#243B53]/10 text-[#243B53]">
                  <Sparkles className="w-5 h-5" />
                </div>
              </div>
              <div className="text-xl font-bold text-[#102A43] mt-1">
                {financialSummary?.emergency_reserve_status || 'Sufficient'}
              </div>
              <p className="text-xs text-[#627D98] mt-2">Emergency buffer safe</p>
            </GlassCard>
          </div>

          {/* Charts & Activity Row */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Spending Trend Chart */}
            <GlassCard className="lg:col-span-8 p-6" delay={0.5}>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-bold text-[#102A43]">Recent Spending Activity</h3>
                  <p className="text-xs text-[#627D98]">Real ledger transactions over time</p>
                </div>
                <NavLink to="/expenses" className="text-xs font-semibold text-[#0F766E] hover:underline flex items-center gap-1">
                  View Ledger <ChevronRight className="w-4 h-4" />
                </NavLink>
              </div>

              {trendData.length > 0 ? (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData}>
                      <defs>
                        <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#0F766E" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#0F766E" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="date" stroke="#627D98" fontSize={11} />
                      <YAxis stroke="#627D98" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#FFFFFF',
                          borderColor: '#D9E2EC',
                          borderRadius: '0.75rem',
                          color: '#172B4D',
                        }}
                        formatter={(val) => [`₹${val}`, 'Amount']}
                      />
                      <Area
                        type="monotone"
                        dataKey="amount"
                        stroke="#0F766E"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#spendGrad)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-64 flex flex-col items-center justify-center text-[#627D98] text-sm">
                  <Wallet className="w-10 h-10 mb-2 opacity-40 text-[#627D98]" />
                  <span>No spending records logged yet.</span>
                </div>
              )}
            </GlassCard>

            {/* Upcoming Bills Column */}
            <GlassCard className="lg:col-span-4 p-6" delay={0.6}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-[#102A43]">Upcoming Bills</h3>
                <NavLink to="/bills" className="text-xs font-semibold text-[#0F766E] hover:underline">
                  All Bills
                </NavLink>
              </div>

              <div className="space-y-3">
                {upcomingBills.length > 0 ? (
                  upcomingBills.slice(0, 4).map((bill) => (
                    <div
                      key={bill.id}
                      className="p-3 rounded-xl bg-white border border-[#D9E2EC] flex items-center justify-between hover:border-[#627D98] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-[#D97706]/10 text-[#D97706]">
                          <Calendar className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-[#172B4D]">{bill.bill_type}</div>
                          <div className="text-xs text-[#627D98] flex items-center gap-1 mt-0.5">
                            <Clock className="w-3 h-3 text-[#627D98]" />
                            <span>Due: {bill.due_date}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-sm font-bold text-[#D97706]">
                        ₹{Number(bill.amount).toLocaleString('en-IN')}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-[#627D98] text-sm">
                    <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-[#2F855A] opacity-60" />
                    <span>All bills paid up to date!</span>
                  </div>
                )}
              </div>
            </GlassCard>
          </div>

          {/* AI Tips & Early Warnings Banner */}
          {healthScore?.tips && healthScore.tips.length > 0 && (
            <div className="p-6 rounded-2xl kinnest-ai-panel border border-[#0F766E]/30 relative overflow-hidden">
              <div className="absolute -top-12 -right-12 w-28 h-28 bg-[#0F766E]/15 rounded-full blur-xl pointer-events-none" />
              <div className="flex items-start gap-4 relative z-10">
                <div className="p-3 rounded-xl bg-[#0F766E]/20 text-[#D4A72C] shrink-0 mt-0.5">
                  <Sparkles className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <span className="text-[#D4A72C]">✦</span> KinNest AI Financial Intelligence
                  </h4>
                  <ul className="mt-2 space-y-1.5 text-sm text-[#F7F9FC]">
                    {healthScore.tips.map((tip, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#0F766E]" />
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;
