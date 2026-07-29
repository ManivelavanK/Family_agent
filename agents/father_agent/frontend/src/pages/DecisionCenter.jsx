import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Bot, AlertOctagon, AlertTriangle, AlertCircle, CheckCircle, Shield, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DecisionCenter = () => {
  const { familyId } = useFamily();
  const [autopilot, setAutopilot] = useState(false);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  const fetchStatusAndPriorities = async () => {
    setLoading(true);
    try {
      // Fetch autopilot status
      const autoRes = await fetch(`http://localhost:8000/finance/autopilot/${familyId}`);
      if (autoRes.ok) {
        const autoData = await autoRes.json();
        setAutopilot(autoData.enabled);
      }

      // Fetch dynamic priorities
      const prioRes = await fetch(`http://localhost:8000/finance/decision-center/${familyId}`);
      if (prioRes.ok) {
        const prioData = await prioRes.json();
        setPriorities(prioData.priorities || []);
      }
    } catch (err) {
      console.error('Error fetching decision center data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatusAndPriorities();
  }, [familyId]);

  const handleToggleAutopilot = async () => {
    setToggling(true);
    try {
      const res = await fetch(`http://localhost:8000/finance/autopilot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          family_id: familyId,
          enabled: !autopilot
        })
      });
      if (res.ok) {
        const data = await res.json();
        setAutopilot(data.enabled);
      }
    } catch (err) {
      console.error('Failed to toggle autopilot:', err);
    } finally {
      setToggling(false);
    }
  };

  const getSeverityStyles = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return {
          icon: <AlertOctagon className="w-6 h-6 text-rose-400" />,
          border: 'border-rose-500/30',
          bg: 'bg-rose-500/5',
          text: 'text-rose-400'
        };
      case 'HIGH':
        return {
          icon: <AlertTriangle className="w-6 h-6 text-amber-400 animate-pulse" />,
          border: 'border-amber-500/30',
          bg: 'bg-amber-500/5',
          text: 'text-amber-400'
        };
      case 'MEDIUM':
        return {
          icon: <AlertCircle className="w-6 h-6 text-sky-400" />,
          border: 'border-sky-500/30',
          bg: 'bg-sky-500/5',
          text: 'text-sky-400'
        };
      case 'LOW':
      default:
        return {
          icon: <CheckCircle className="w-6 h-6 text-emerald-400" />,
          border: 'border-emerald-500/30',
          bg: 'bg-emerald-500/5',
          text: 'text-emerald-400'
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <Bot className="w-8 h-8 text-[#0F766E]" />
            <span>Father AI Decision Center</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Real-time financial guardian oversight, active risks, priorities, and autopilot.
          </p>
        </div>

        {/* Autopilot Controls */}
        <div className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-[#102A43] border border-[#243B53] text-slate-100">
          <Shield className={`w-5 h-5 ${autopilot ? 'text-emerald-400' : 'text-slate-400'}`} />
          <div className="flex flex-col">
            <span className="text-xs font-bold">Financial Autopilot</span>
            <span className="text-[10px] text-slate-400">{autopilot ? 'Active Monitoring' : 'Inactive'}</span>
          </div>
          <button
            onClick={handleToggleAutopilot}
            disabled={toggling}
            className={`w-12 h-6 rounded-full p-1 transition-colors cursor-pointer ml-2 ${
              autopilot ? 'bg-emerald-500' : 'bg-slate-700'
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-white transition-transform ${
                autopilot ? 'translate-x-6' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex flex-col items-center justify-center text-center">
          <RefreshCw className="w-8 h-8 text-emerald-500 animate-spin mb-2" />
          <p className="text-slate-400 text-sm">Evaluating live financials and generating priority concern list...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {priorities.map((card, idx) => {
            const styles = getSeverityStyles(card.severity);
            return (
              <GlassCard
                key={idx}
                className={`p-6 border ${styles.border} ${styles.bg} transition-all duration-300 hover:scale-[1.01]`}
              >
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-xl bg-slate-900/40 border border-slate-700/50">
                    {styles.icon}
                  </div>
                  <div className="flex-1 space-y-2 text-slate-100">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[10px] font-bold uppercase tracking-widest ${styles.text}`}>
                        {card.subtitle}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase bg-slate-900/40 border border-slate-700/30 ${styles.text}`}>
                        {card.severity}
                      </span>
                    </div>
                    <h3 className="text-base font-extrabold text-white">{card.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{card.description}</p>

                    <div className="pt-2">
                      {card.action_link.startsWith('/') ? (
                        <Link
                          to={card.action_link}
                          className="inline-flex items-center px-4 py-2 rounded-xl bg-[#0F766E] hover:bg-emerald-600 text-white text-xs font-bold transition-all shadow-md shadow-[#0f766e]/10"
                        >
                          {card.action_label}
                        </Link>
                      ) : (
                        <a
                          href={card.action_link}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center px-4 py-2 rounded-xl bg-[#0F766E] hover:bg-emerald-600 text-white text-xs font-bold transition-all shadow-md shadow-[#0f766e]/10"
                        >
                          {card.action_label}
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DecisionCenter;
