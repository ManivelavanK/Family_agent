import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { notificationApi } from '../services/notificationApi';
import { GlassCard } from '../components/ui/GlassCard';
import { Bell, AlertTriangle, FileText, PieChart, Activity, ShieldCheck } from 'lucide-react';

export const Notifications = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  useEffect(() => {
    const fetchNotifications = async () => {
      setLoading(true);
      try {
        const res = await notificationApi.getNotifications(familyId);
        setNotifications(res?.notifications || []);
      } catch (err) {
        console.error('Error fetching notifications:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, [familyId]);

  const filtered = notifications.filter((n) => priorityFilter === 'ALL' || n.priority === priorityFilter);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Bell className="w-8 h-8 text-blue-400" />
            <span>Notification Center</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            System priority alerts regarding upcoming bills, budget limits, and health scores.
          </p>
        </div>

        {/* Priority Filter */}
        <div className="flex items-center gap-2">
          {['ALL', 'High', 'Medium', 'Low'].map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                priorityFilter === p
                  ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/25'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {p} Priority
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400">Loading notifications...</div>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((n, idx) => (
            <GlassCard key={idx} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2.5 rounded-xl ${
                    n.priority === 'High'
                      ? 'bg-rose-500/10 text-rose-400'
                      : n.priority === 'Medium'
                      ? 'bg-amber-500/10 text-amber-400'
                      : 'bg-blue-500/10 text-blue-400'
                  }`}
                >
                  {n.type === 'Bill' ? (
                    <FileText className="w-5 h-5" />
                  ) : n.type === 'Budget' ? (
                    <PieChart className="w-5 h-5" />
                  ) : (
                    <Activity className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">{n.type} Alert</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                        n.priority === 'High'
                          ? 'bg-rose-500/20 text-rose-300'
                          : n.priority === 'Medium'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-blue-500/20 text-blue-300'
                      }`}
                    >
                      {n.priority} Priority
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1">{n.message}</p>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard className="py-12 text-center text-slate-400">
          <ShieldCheck className="w-10 h-10 mx-auto mb-2 text-emerald-400 opacity-80" />
          <span>No notifications found for this priority filter.</span>
        </GlassCard>
      )}
    </div>
  );
};

export default Notifications;
