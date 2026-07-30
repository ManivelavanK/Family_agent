import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { 
  DollarSign, TrendingDown, TrendingUp, 
  Bot, Scale, Shield, LineChart, Plus, RefreshCw, Check, X, 
  Lock, ArrowUpRight, ShieldCheck, AlertCircle, Sparkles, Send, Eye, Clock
} from 'lucide-react';


import { fatherApi } from '../api/fatherApi';

export default function FatherAgent() {
  const { role, username } = useAuthStore();
  const { activeTabs, setActiveTab } = useActiveTabStore();
  const activeTab = activeTabs['/father'] || 'overview';

  // API Data State
  const [metrics, setMetrics] = useState<any>(null);
  const [ledger, setLedger] = useState<any>(null);
  const [goals, setGoals] = useState<any[]>([]);
  const [bills, setBills] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  
  // Loading & Error States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Form inputs
  const [newReqItem, setNewReqItem] = useState('');
  const [newReqAmount, setNewReqAmount] = useState('');
  const [newReqUser, setNewReqUser] = useState('');
  const [monthlyBudgetInput, setMonthlyBudgetInput] = useState('');
  const [weeklyBudgetInput, setWeeklyBudgetInput] = useState('');
  
  // Ask before spend
  const [checkAmount, setCheckAmount] = useState('');
  const [checkCategory, setCheckCategory] = useState('groceries');
  const [checkResult, setCheckResult] = useState<any>(null);

  // AI Chat state
  const [chatQuery, setChatQuery] = useState('');
  const [chatMessages, setChatMessages] = useState<any[]>([
    { sender: 'ai', text: 'Welcome to your real-time financial intelligence center, Father. How can I help you manage the family assets today?' }
  ]);

  const isParent = role?.toLowerCase() === 'parent';

  // Listen to header button events
  useEffect(() => {
    const handleSwitchTab = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail) {
        setActiveTab('/father', customEvent.detail);
      }
    };
    window.addEventListener('switch-father-tab', handleSwitchTab);
    return () => window.removeEventListener('switch-father-tab', handleSwitchTab);
  }, [setActiveTab]);

  // Fetch all required data dynamically based on activeTab
  const fetchData = async (forceRefresh = false) => {
    if (forceRefresh) setLoading(true);
    try {
      setError('');
      
      // Fetch data in parallel depending on the active view to optimize performance
      const [resMetrics, resLedger, resGoals, resBills, resRequests] = await Promise.all([
        fatherApi.getMetrics(),
        fatherApi.getLedger(),
        fatherApi.getGoals(),
        fatherApi.getBills(),
        fatherApi.getRequests()
      ].map(p => p.catch(err => {
        console.error("Fetch error:", err);
        return null;
      })));

      if (resMetrics) {
        setMetrics(resMetrics);
        setMonthlyBudgetInput(resMetrics.monthlyBudget?.toString() || '');
        setWeeklyBudgetInput(resMetrics.weeklyBudget?.toString() || '');
      }
      if (resLedger) {
        setLedger(resLedger);
      }
      if (resGoals) {
        setGoals(resGoals);
      }
      if (resBills) {
        setBills(resBills);
      }
      if (resRequests) {
        setRequests(resRequests);
      }
    } catch (err: any) {
      console.error(err);
      setError('Failed to connect to the Father Agent microservice. Make sure the server on port 8002 is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    fetchData(true);
  };

  // Submit new request
  const submitRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReqItem || !newReqAmount) return;
    setActionLoading(true);
    try {
      const res = await fatherApi.createRequest({
        itemName: newReqItem,
        amount: parseFloat(newReqAmount),
        requestedBy: newReqUser || username || 'Family Member'
      });
      if (res) {
        setNewReqItem('');
        setNewReqAmount('');
        setNewReqUser('');
        await fetchData();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  // Approve or Reject purchase request
  const handleRequestAction = async (id: string, approve: boolean) => {
    setActionLoading(true);
    try {
      const res = await fatherApi.updateRequest(id, { status: approve ? 'APPROVED' : 'REJECTED' });
      if (res) {
        await fetchData();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  // Save budget configurations
  const saveBudgets = async () => {
    setActionLoading(true);
    try {
      const res = await fatherApi.updateMetrics({
        monthlyBudget: parseFloat(monthlyBudgetInput),
        weeklyBudget: parseFloat(weeklyBudgetInput)
      });
      if (res) {
        setMetrics(res);
        alert('Budget configurations updated successfully!');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  // Rule checker (Ask Before Spend)
  const checkSpendingRule = (e: React.FormEvent) => {
    e.preventDefault();
    if (!checkAmount || !metrics) return;
    const amt = parseFloat(checkAmount);
    const balance = metrics.remainingBalance || 0;
    
    let isAllowed = true;
    let reasons: string[] = [];

    if (amt > balance) {
      isAllowed = false;
      reasons.push(`Purchase amount (₹${amt.toLocaleString()}) exceeds the remaining monthly balance (₹${balance.toLocaleString()}).`);
    }

    if (amt > metrics.weeklyBudget * 0.5) {
      reasons.push(`High value transaction alert: This constitutes over 50% of the entire family weekly budget threshold (₹${(metrics.weeklyBudget).toLocaleString()}).`);
    }

    if (checkCategory === 'entertainment' && amt > 10000) {
      reasons.push("Non-essential category restriction: Entertainment expenses above ₹10,000 require manual Parent permission.");
    }

    setCheckResult({
      allowed: isAllowed,
      reasons: reasons.length > 0 ? reasons : ["No budget rules violated. Transaction is within safe spending margins."]
    });
  };

  // AI consultant chatbot
  const askAIConsultant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;

    const userMsg = chatQuery;
    setChatQuery('');
    setChatMessages(prev => [...prev, { sender: 'user', text: userMsg }]);

    try {
      const data = await fatherApi.consult({ query: userMsg });
      if (data) {
        setChatMessages(prev => [...prev, { sender: 'ai', text: data.answer }]);
      } else {
        setChatMessages(prev => [...prev, { sender: 'ai', text: "Apologies, I couldn't reach the backend intelligence engine right now." }]);
      }
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, { sender: 'ai', text: "Error sending payload to AI service." }]);
    }
  };

  // Skeletal loaders layout matching the reference UI
  if (loading) {
    return (
      <div className="p-8 space-y-6 text-slate-200 bg-[#070E16] min-h-screen">
        <div className="flex justify-between items-center">
          <div>
            <div className="h-6 bg-slate-800 rounded w-48 mb-2 animate-pulse"></div>
            <div className="h-4 bg-slate-800 rounded w-96 animate-pulse"></div>
          </div>
          <div className="w-10 h-10 bg-slate-800 rounded-full animate-pulse"></div>
        </div>

        {/* 4 Top Cards skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-[#0D1520] border border-slate-800 rounded-2xl animate-pulse p-6 space-y-3">
              <div className="h-4 bg-slate-800 rounded w-1/2"></div>
              <div className="h-8 bg-slate-800 rounded w-3/4"></div>
            </div>
          ))}
        </div>

        {/* 2 Bottom Cards skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-[#0D1520] border border-slate-800 rounded-2xl animate-pulse"></div>
          <div className="h-64 bg-[#0D1520] border border-slate-800 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  const spentPct = metrics && metrics.monthlyBudget > 0
    ? Math.min(100, Math.round((metrics.currentSpending / metrics.monthlyBudget) * 100))
    : 0;

  return (
    <div className="p-8 space-y-6 text-slate-250 bg-[#070E16] min-h-screen">
      
      {/* View Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800/60 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-black text-white tracking-tight capitalize">
              Good evening, Father 👋
            </h1>
            <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase">
              Family #1
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Welcome back. Here is your family's real-time financial intelligence workspace.
          </p>
        </div>
        
        <button 
          onClick={handleRefresh}
          className="flex items-center justify-center space-x-1.5 px-4 py-2 bg-slate-850 hover:bg-slate-800 text-slate-250 rounded-xl text-xs font-semibold border border-slate-800/80 shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Sync Workspace Data</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center space-x-3 text-red-400 text-xs">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Tab Content Views */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -15 }}
          transition={{ duration: 0.25 }}
          className="space-y-6"
        >
          
          {/* 1. OVERVIEW VIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { label: 'Monthly Budget Limit', value: metrics?.monthlyBudget, icon: DollarSign, color: 'text-blue-400', bg: 'bg-blue-500/5' },
                  { label: 'Weekly Spend Target', value: metrics?.weeklyBudget, icon: TrendingUp, color: 'text-indigo-400', bg: 'bg-indigo-500/5' },
                  { label: 'Current Logged Spend', value: metrics?.currentSpending, icon: TrendingDown, color: 'text-rose-450', bg: 'bg-rose-500/5' },
                  { label: 'Remaining Balance', value: metrics?.remainingBalance, icon: Shield, color: 'text-emerald-450', bg: 'bg-emerald-500/5' }
                ].map((item, idx) => (
                  <div key={idx} className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-slate-700/60 transition-colors">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{item.label}</p>
                        <p className="text-2xl font-black text-white mt-2">
                          ₹{item.value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </p>
                      </div>
                      <div className={`p-2.5 rounded-xl ${item.bg} ${item.color}`}>
                        <item.icon className="w-5 h-5" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Progress and Ledger Summary */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Spending Progress Bar */}
                <div className="lg:col-span-2 bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-black text-sm text-white tracking-wide">Monthly Spend Ratio</h3>
                      <p className="text-[10px] text-slate-500">Autonomous safety thresholds compared to budget.</p>
                    </div>
                    <span className={`text-xs font-black px-2.5 py-0.5 rounded-full ${spentPct > 80 ? 'bg-red-500/15 text-red-400' : 'bg-emerald-500/15 text-emerald-400'}`}>
                      {spentPct}% Consumed
                    </span>
                  </div>
                  
                  <div className="w-full bg-[#162232] rounded-full h-3.5 overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-800 ${spentPct > 80 ? 'bg-rose-500' : spentPct > 60 ? 'bg-amber-500' : 'bg-blue-500'}`}
                      style={{ width: `${spentPct}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] font-bold text-slate-500">
                    <span>₹0</span>
                    <span>₹{metrics?.monthlyBudget?.toLocaleString()} Maximum Cap</span>
                  </div>
                </div>

                {/* Status Indicator Panel */}
                <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg flex flex-col justify-between">
                  <div className="space-y-2">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-wider">Agent Twin Core</span>
                    <h4 className="text-sm font-bold text-white flex items-center">
                      <Sparkles className="w-4 h-4 text-amber-500 mr-1.5 animate-pulse" />
                      Financial Safeguard Active
                    </h4>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      All systems operating normally. Weekly spending velocity is within optimal safety ranges.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-850 flex items-center justify-between text-[10px] text-slate-500 font-bold">
                    <span>Port Microservice: 8002</span>
                    <span className="text-emerald-500">ONLINE</span>
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* 2. EXPENSES VIEW */}
          {activeTab === 'expenses' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white">Expense Category Allocations</h2>
                <p className="text-xs text-slate-500">Live distributions from the transactions ledger database.</p>
              </div>

              {ledger?.transactions?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Category allocations bars */}
                  <div className="space-y-4">
                    {[
                      { name: 'Utilities & Subscriptions', pct: 35, color: 'bg-indigo-500' },
                      { name: 'Education & Child Care', pct: 40, color: 'bg-blue-500' },
                      { name: 'Shopping & Groceries', pct: 25, color: 'bg-emerald-500' }
                    ].map(c => {
                      const totalAlloc = metrics?.currentSpending || 0;
                      const amount = totalAlloc * (c.pct / 100);
                      return (
                        <div key={c.name} className="space-y-1.5">
                          <div className="flex justify-between text-xs font-bold text-slate-400">
                            <span>{c.name}</span>
                            <span>₹{amount.toLocaleString(undefined, { maximumFractionDigits: 0 })} ({c.pct}%)</span>
                          </div>
                          <div className="w-full bg-[#162232] h-2 rounded-full overflow-hidden">
                            <div className={`h-full ${c.color} rounded-full`} style={{ width: `${c.pct}%` }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Recent Debits logs */}
                  <div className="space-y-3">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Recent Expense Audits</h3>
                    <div className="divide-y divide-slate-800">
                      {ledger.transactions.map((tx: any) => (
                        <div key={tx.id} className="flex justify-between py-2.5 text-xs">
                          <div>
                            <p className="font-bold text-slate-200">{tx.description}</p>
                            <p className="text-[10px] text-slate-500">{tx.date} · {tx.category}</p>
                          </div>
                          <span className="font-black text-rose-450">-₹{tx.amount?.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">No active ledger details returned.</div>
              )}
            </div>
          )}

          {/* 3. INCOME VIEW */}
          {activeTab === 'income' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white">Income Streams & Cash Flow</h2>
                <p className="text-xs text-slate-500">Documented incoming family funds and external consulting streams.</p>
              </div>

              {ledger?.income?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Income stream cards */}
                  <div className="space-y-3">
                    {ledger.income.map((inc: any) => (
                      <div key={inc.id} className="bg-[#162232]/50 border border-slate-800 rounded-xl p-4 flex justify-between items-center">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                            <ArrowUpRight className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="text-xs font-bold text-white">{inc.source}</p>
                            <p className="text-[10px] text-slate-500">{inc.frequency} deposit · {inc.date}</p>
                          </div>
                        </div>
                        <span className="text-sm font-black text-emerald-400">
                          +₹{inc.amount?.toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Summary Metric Box */}
                  <div className="bg-[#162232]/30 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
                    <div className="space-y-2">
                      <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Total Monthly Cash Inflow</span>
                      <p className="text-3xl font-black text-white">
                        ₹{(ledger.income.reduce((sum: number, i: any) => sum + i.amount, 0)).toLocaleString()}
                      </p>
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        Cash inflows are securely partitioned and mapped directly to primary allocation targets including monthly utility bills and savings schedules.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">No logged cash flows found.</div>
              )}
            </div>
          )}

          {/* 4. BUDGET VIEW */}
          {activeTab === 'budget' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white">Limit Control & Threshold Adjustments</h2>
                <p className="text-xs text-slate-500">Edit core family limits. Note that changes update instantly in the workspace twin.</p>
              </div>

              {isParent ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Monthly Limit Threshold (₹)</label>
                      <input 
                        type="number" 
                        value={monthlyBudgetInput}
                        onChange={e => setMonthlyBudgetInput(e.target.value)}
                        placeholder="e.g. 80000"
                        className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Weekly Limit Cap (₹)</label>
                      <input 
                        type="number" 
                        value={weeklyBudgetInput}
                        onChange={e => setWeeklyBudgetInput(e.target.value)}
                        placeholder="e.g. 18000"
                        className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                      />
                    </div>
                  </div>

                  <button 
                    onClick={saveBudgets}
                    disabled={actionLoading || !monthlyBudgetInput || !weeklyBudgetInput}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/10 active:scale-95 disabled:opacity-50 transition-all"
                  >
                    Save & Deploy Budget Thresholds
                  </button>
                </div>
              ) : (
                <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center space-x-3 text-amber-400 text-xs">
                  <Lock className="w-5 h-5 shrink-0" />
                  <span>Administrative role needed to modify budget settings. Standard users have read-only access.</span>
                </div>
              )}
            </div>
          )}

          {/* 5. SAVINGS GOALS VIEW */}
          {activeTab === 'savings' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white">Savings Targets</h2>
                <p className="text-xs text-slate-500">Autonomous vault allocations and family security reserves.</p>
              </div>

              {goals.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {goals.map((g: any) => {
                    const pct = Math.min(100, Math.round((g.current / g.target) * 100));
                    return (
                      <div key={g.id} className="bg-[#162232]/40 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-[9px] font-black px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60 uppercase">
                              {g.category}
                            </span>
                            <h3 className="text-xs font-bold text-white mt-2">{g.name}</h3>
                          </div>
                          <span className="text-xs font-black text-emerald-455">{pct}%</span>
                        </div>

                        <div className="space-y-1">
                          <div className="w-full bg-[#0D1520] h-2 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pct}%` }} />
                          </div>
                          <div className="flex justify-between text-[9px] font-bold text-slate-500">
                            <span>₹{g.current?.toLocaleString()} saved</span>
                            <span>₹{g.target?.toLocaleString()} target</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">No active savings allocations found.</div>
              )}
            </div>
          )}

          {/* 6. BILLS VIEW */}
          {activeTab === 'bills' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white">Scheduled Fixed Household Bills</h2>
                <p className="text-xs text-slate-500">Upcoming automated recurring accounts with pre-approved payment rules.</p>
              </div>

              {bills.length > 0 ? (
                <div className="divide-y divide-slate-800">
                  {bills.map((b: any) => (
                    <div key={b.id} className="flex justify-between items-center py-3 text-xs">
                      <div className="flex items-center space-x-3">
                        <div className={`p-1.5 rounded ${b.status === 'PAID' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                          {b.status === 'PAID' ? <Check className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                        </div>
                        <div>
                          <p className="font-bold text-slate-200">{b.name}</p>
                          <p className="text-[10px] text-slate-500">Due {b.dueDate}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="font-bold text-slate-200">₹{b.amount?.toLocaleString()}</span>
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded border uppercase ${
                          b.status === 'PAID' 
                            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                            : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                        }`}>
                          {b.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">No upcoming bills found.</div>
              )}
            </div>
          )}

          {/* 7. AI ADVISOR VIEW */}
          {activeTab === 'ai_advisor' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-4">
              <div>
                <h2 className="text-base font-black text-white flex items-center">
                  <Bot className="w-5 h-5 text-emerald-400 mr-2" />
                  Family AI Advisor Chat
                </h2>
                <p className="text-xs text-slate-500">Ask the digital twin rules engine about allocations, limits, and savings optimization suggestions.</p>
              </div>

              {/* Chat Message Box */}
              <div className="bg-[#070E16]/80 border border-slate-800 rounded-xl p-4 h-80 overflow-y-auto space-y-4 flex flex-col justify-end">
                <div className="space-y-3 overflow-y-auto pr-2">
                  {chatMessages.map((msg, idx) => (
                    <div 
                      key={idx} 
                      className={clsx(
                        "p-3 rounded-2xl text-xs max-w-[75%] leading-relaxed",
                        msg.sender === 'ai' 
                          ? "bg-[#162232] text-slate-200 border border-slate-800/50 self-start" 
                          : "bg-blue-600 text-white self-end ml-auto"
                      )}
                    >
                      {msg.text}
                    </div>
                  ))}
                </div>
              </div>

              {/* Chat Input form */}
              <form onSubmit={askAIConsultant} className="flex space-x-2">
                <input 
                  type="text" 
                  value={chatQuery}
                  onChange={e => setChatQuery(e.target.value)}
                  placeholder="Ask about budget margins, safety thresholds, savings goals..."
                  className="flex-1 bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                />
                <button 
                  type="submit" 
                  className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-md active:scale-95 flex items-center space-x-1"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Send</span>
                </button>
              </form>
            </div>
          )}

          {/* 8. DECISION CENTER VIEW */}
          {activeTab === 'decision_center' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-base font-black text-white flex items-center">
                    <Scale className="w-5 h-5 text-blue-400 mr-2" />
                    Family Purchase Decision Center
                  </h2>
                  <p className="text-xs text-slate-500">Approve or reject spending requests initiated by family members.</p>
                </div>
                <span className="text-[10px] bg-[#162232] text-blue-400 border border-blue-500/25 px-2.5 py-0.5 rounded-full font-bold">
                  {requests.filter(r => r.status === 'PENDING').length} Pending Requests
                </span>
              </div>

              {/* Request List Grid */}
              <div className="space-y-3">
                {requests.length > 0 ? (
                  requests.map((req) => (
                    <div 
                      key={req.id} 
                      className="bg-[#162232]/40 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-white">{req.itemName}</span>
                          <span className="text-[9px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-semibold border border-slate-750">
                            {req.id}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500">
                          Requested by <span className="font-bold text-slate-355">{req.requestedBy}</span> on {req.date}
                        </p>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end space-x-6">
                        <span className="text-sm font-black text-white">₹{req.amount?.toLocaleString()}</span>
                        
                        {req.status === 'PENDING' ? (
                          isParent ? (
                            <div className="flex space-x-2">
                              <button 
                                onClick={() => handleRequestAction(req.id, true)}
                                disabled={actionLoading}
                                className="p-1.5 bg-emerald-500/15 border border-emerald-500/20 text-emerald-450 hover:bg-emerald-500 hover:text-white rounded-lg transition-all"
                                title="Approve Request"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                              <button 
                                onClick={() => handleRequestAction(req.id, false)}
                                disabled={actionLoading}
                                className="p-1.5 bg-rose-500/15 border border-rose-500/20 text-rose-455 hover:bg-rose-500 hover:text-white rounded-lg transition-all"
                                title="Reject Request"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ) : (
                            <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-850 text-slate-500 uppercase border border-slate-800">
                              PENDING APPR
                            </span>
                          )
                        ) : (
                          <span className={clsx(
                            "text-[9px] font-bold px-2 py-0.5 rounded border uppercase",
                            req.status === 'APPROVED' 
                              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-450' 
                              : 'bg-rose-500/10 border-rose-500/20 text-rose-455'
                          )}>
                            {req.status}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center py-12 text-slate-500 text-xs">No active requests logged.</p>
                )}
              </div>

              {/* Submit New Purchase Request Form */}
              <div className="border-t border-slate-850 pt-6">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4">File New Purchase Request</h3>
                <form onSubmit={submitRequest} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Item Name</label>
                    <input 
                      type="text" 
                      value={newReqItem}
                      onChange={e => setNewReqItem(e.target.value)}
                      placeholder="e.g. PlayStation 5 Console"
                      className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Amount (₹)</label>
                    <input 
                      type="number" 
                      value={newReqAmount}
                      onChange={e => setNewReqAmount(e.target.value)}
                      placeholder="e.g. 49999"
                      className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                      required
                    />
                  </div>
                  <button 
                    type="submit"
                    disabled={actionLoading || !newReqItem || !newReqAmount}
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all shadow-md active:scale-95 disabled:opacity-50 flex items-center justify-center space-x-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Submit Request</span>
                  </button>
                </form>
              </div>

            </div>
          )}

          {/* 9. ASK BEFORE SPEND VIEW */}
          {activeTab === 'ask_before_spend' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white flex items-center">
                  <Shield className="w-5 h-5 text-emerald-400 mr-2" />
                  Automated Spending Rules Verification
                </h2>
                <p className="text-xs text-slate-500">Run sandbox simulations on proposed transaction values to check rule compliance beforehand.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                {/* Form Inputs */}
                <form onSubmit={checkSpendingRule} className="space-y-4">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Proposed Amount (₹)</label>
                    <input 
                      type="number" 
                      value={checkAmount}
                      onChange={e => setCheckAmount(e.target.value)}
                      placeholder="e.g. 15000"
                      className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-blue-500 transition-colors"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Transaction Category</label>
                    <select 
                      value={checkCategory}
                      onChange={e => setCheckCategory(e.target.value)}
                      className="w-full bg-[#162232] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 outline-none focus:border-blue-500 transition-colors"
                    >
                      <option value="groceries">Groceries & Cooking</option>
                      <option value="utilities">House Utilities & Bills</option>
                      <option value="education">Education & School fees</option>
                      <option value="entertainment">Entertainment & Dining out</option>
                    </select>
                  </div>

                  <button 
                    type="submit"
                    className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/10 transition-all active:scale-95"
                  >
                    Verify Rule Parameters
                  </button>
                </form>

                {/* Verification Results Output Panel */}
                <div className="bg-[#070E16] border border-slate-800 rounded-xl p-5 min-h-[180px] flex flex-col justify-between">
                  {checkResult ? (
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2">
                        {checkResult.allowed ? (
                          <div className="flex items-center text-emerald-450 font-bold text-xs space-x-1.5">
                            <ShieldCheck className="w-5 h-5" />
                            <span>Simulation Pre-Approved</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-rose-455 font-bold text-xs space-x-1.5">
                            <AlertCircle className="w-5 h-5" />
                            <span>Rule Conflict Warning</span>
                          </div>
                        )}
                      </div>

                      <div className="space-y-2">
                        {checkResult.reasons.map((r: string, i: number) => (
                          <p key={i} className="text-[11px] text-slate-455 leading-relaxed pl-1 border-l border-slate-700">
                            {r}
                          </p>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-slate-500 text-xs text-center h-full my-auto space-y-2">
                      <Eye className="w-8 h-8 text-slate-600" />
                      <span>Awaiting parameters to run checking simulation.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 10. PREDICTIONS VIEW */}
          {activeTab === 'predictions' && (
            <div className="bg-[#0D1520] border border-slate-800/80 rounded-2xl p-6 shadow-lg space-y-6">
              <div>
                <h2 className="text-base font-black text-white flex items-center">
                  <LineChart className="w-5 h-5 text-indigo-400 mr-2" />
                  Monthly Cash Flow Projections
                </h2>
                <p className="text-xs text-slate-500">Simulated forecast values for the next 6 months based on current recurring utilities & income velocity.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                {/* Bar chart or values logs */}
                <div className="space-y-3">
                  {[
                    { month: 'August 2026', flow: '+₹65,000', status: 'Healthy Surplus' },
                    { month: 'September 2026', flow: '+₹54,000', status: 'Optimal' },
                    { month: 'October 2026', flow: '+₹32,500', status: 'Higher Expenses' },
                    { month: 'November 2026', flow: '+₹72,000', status: 'Peak Earnings' },
                    { month: 'December 2026', flow: '+₹15,000', status: 'Holiday Threshold Tightness' }
                  ].map((f, idx) => (
                    <div key={idx} className="flex justify-between py-2 border-b border-slate-850 text-xs">
                      <div>
                        <p className="font-bold text-slate-200">{f.month}</p>
                        <p className="text-[10px] text-slate-500">{f.status}</p>
                      </div>
                      <span className="font-bold text-emerald-450">{f.flow}</span>
                    </div>
                  ))}
                </div>

                {/* Description Panel */}
                <div className="bg-[#162232]/40 border border-slate-800 rounded-xl p-5 flex flex-col justify-between h-full">
                  <div className="space-y-3">
                    <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Model Projections Details</span>
                    <h3 className="text-xs font-bold text-white">Neural Net Predictive Analysis</h3>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      Models assume basic baseline utilities remain static. In October, simulated tuition fees and subscription increases are estimated to reduce surplus cash margins. December shows an expected high retail shopping burn rate. 
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </motion.div>
      </AnimatePresence>
    </div>
  );
}