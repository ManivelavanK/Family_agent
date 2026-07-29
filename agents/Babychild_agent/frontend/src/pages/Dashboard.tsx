import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Milk, Moon, TrendingUp, Syringe, Bell, Sparkles,
  ChevronRight, Layers, HeartPulse,
} from 'lucide-react';
import { db } from '../data/mockData';
import { aiService } from '../services/aiService';
import MetricCard from '../components/cards/MetricCard';
import { DashboardSkeleton } from '../components/common/SkeletonLoader';

export default function Dashboard() {
  const navigate = useNavigate();
  const [insight, setInsight] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    aiService.getDashboardInsight().then((text) => {
      setInsight(text);
      setLoading(false);
    });
  }, []);

  const upcomingVaccine = db.vaccinations.find((v) => v.status === 'Upcoming');
  const daysUntilVaccine = upcomingVaccine
    ? Math.ceil((new Date(upcomingVaccine.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  const unreadAlerts = db.alerts.filter((a) => !a.read).length;

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-6">
      {/* AI Summary Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 p-6 text-white shadow-lg shadow-violet-200">
        {/* Decorative blobs */}
        <div className="pointer-events-none absolute -top-10 -right-10 h-48 w-48 rounded-full bg-white/10 blur-2xl" />
        <div className="pointer-events-none absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-white/10 blur-xl" />

        <div className="relative flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-white/80 uppercase tracking-wide">AI Baby Summary</h2>
              <span className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-bold text-white uppercase">Live</span>
            </div>
            <p className="mt-2 text-base font-medium leading-relaxed text-white/95">
              {insight}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={() => navigate('/feeding')}
                className="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/30"
              >
                View Schedule <ChevronRight className="h-3 w-3" />
              </button>
              <button
                onClick={() => navigate('/health-logs')}
                className="flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/20"
              >
                Open Health Logs <ChevronRight className="h-3 w-3" />
              </button>
              <button
                onClick={() => navigate('/ai')}
                className="flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/20"
              >
                Ask AI <Sparkles className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-5">
        <MetricCard
          icon={Milk}
          iconBg="bg-blue-100"
          iconColor="text-blue-600"
          label="Today's Feedings"
          primary="8"
          secondaryLabel="Next Feed"
          secondaryValue="1:30 PM"
        />
        <MetricCard
          icon={Moon}
          iconBg="bg-indigo-100"
          iconColor="text-indigo-600"
          label="Total Sleep"
          primary="13.2h"
          badge="Excellent"
          badgeColor="bg-emerald-100 text-emerald-700"
        />
        <MetricCard
          icon={Layers}
          iconBg="bg-amber-100"
          iconColor="text-amber-600"
          label="Diaper Changes"
          primary="6"
          secondaryLabel="Dirty · Wet"
          secondaryValue="2 · 4"
        />
        <MetricCard
          icon={TrendingUp}
          iconBg="bg-emerald-100"
          iconColor="text-emerald-600"
          label="Current Weight"
          primary="8.4 kg"
          secondaryLabel="Monthly Gain"
          secondaryValue="+0.5 kg"
        />
        <MetricCard
          icon={Syringe}
          iconBg="bg-rose-100"
          iconColor="text-rose-600"
          label="Next Vaccine"
          primary={daysUntilVaccine ? `${daysUntilVaccine}d` : '—'}
          badge={unreadAlerts > 0 ? `${unreadAlerts} Alerts` : undefined}
          badgeColor="bg-rose-100 text-rose-700"
          secondaryLabel="Needs Attention"
          secondaryValue="2 AI"
        />
      </div>

      {/* Bottom Row: AI Baby Insight + Quick Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Large AI Insight Card */}
        <div className="col-span-2 rounded-2xl border border-violet-100 bg-gradient-to-br from-violet-50 to-indigo-50 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-5 w-5 text-violet-600" />
            <h3 className="text-sm font-bold text-violet-700 uppercase tracking-wide">✨ Baby Care Insight</h3>
          </div>
          <div className="space-y-3 text-sm text-slate-700">
            <p className="flex items-start gap-2">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-violet-400" />
              Aarav has been feeding more frequently over the past two days — possibly a growth spurt.
            </p>
            <p className="flex items-start gap-2">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
              Sleep quality remains excellent — 8.5 hours last night with no disruptions.
            </p>
            <p className="flex items-start gap-2">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-blue-400" />
              Growth is perfectly on track at the 50th WHO percentile.
            </p>
            <p className="flex items-start gap-2">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-rose-400" />
              Measles / MR Vaccination is due in 5 days. Schedule an appointment with Dr. Priya now.
            </p>
          </div>
          <div className="mt-5 flex gap-3">
            <button
              onClick={() => navigate('/vaccinations')}
              className="flex items-center gap-1.5 rounded-lg bg-violet-600 px-4 py-2 text-xs font-semibold text-white hover:bg-violet-700 transition-colors"
            >
              View Schedule <ChevronRight className="h-3 w-3" />
            </button>
            <button
              onClick={() => navigate('/health-logs')}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Open Health Logs
            </button>
          </div>
        </div>

        {/* Quick Action Panel */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-700 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {[
              { label: 'Log a Feeding', icon: Milk, route: '/feeding', color: 'text-blue-600 bg-blue-50' },
              { label: 'Log Sleep', icon: Moon, route: '/sleep', color: 'text-indigo-600 bg-indigo-50' },
              { label: 'View Alerts', icon: Bell, route: '/alerts', color: 'text-rose-600 bg-rose-50' },
              { label: 'Check Growth', icon: TrendingUp, route: '/growth', color: 'text-emerald-600 bg-emerald-50' },
              { label: 'AI Assistant', icon: Sparkles, route: '/ai', color: 'text-violet-600 bg-violet-50' },
              { label: 'Health Logs', icon: HeartPulse, route: '/health-logs', color: 'text-pink-600 bg-pink-50' },
            ].map(({ label, icon: Icon, route, color }) => (
              <button
                key={route}
                onClick={() => navigate(route)}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 hover:bg-slate-50 transition-colors text-left group"
              >
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${color}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900">{label}</span>
                <ChevronRight className="ml-auto h-4 w-4 text-slate-300 group-hover:text-slate-500 transition-colors" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts Strip */}
      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-700">Recent Alerts</h3>
          <button onClick={() => navigate('/alerts')} className="text-xs font-medium text-violet-600 hover:underline">
            View All
          </button>
        </div>
        <div className="space-y-2">
          {db.alerts.slice(0, 3).map((alert) => (
            <div
              key={alert.id}
              className={`flex items-center gap-3 rounded-xl p-3 ${
                alert.type === 'danger' ? 'bg-rose-50' :
                alert.type === 'warning' ? 'bg-amber-50' : 'bg-emerald-50'
              }`}
            >
              <span
                className={`h-2 w-2 shrink-0 rounded-full ${
                  alert.type === 'danger' ? 'bg-rose-500' :
                  alert.type === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
              />
              <span className="flex-1 text-sm font-medium text-slate-700">{alert.message}</span>
              {!alert.read && (
                <span className="rounded-full bg-rose-500 px-2 py-0.5 text-[10px] font-bold text-white">NEW</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
