import { motion } from 'framer-motion';
import { Bell, ShieldAlert, Sparkles, CheckSquare } from 'lucide-react';

interface NotificationsPageProps {
  notifications: Array<{
    id: number;
    title: string;
    description: string;
    time: string;
    unread: boolean;
    type: 'ALERT' | 'INSIGHT' | 'SUCCESS';
  }>;
  onMarkAllAsRead: () => void;
}

export default function NotificationsPage({ notifications, onMarkAllAsRead }: NotificationsPageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-rose-50 text-rose-600">
            <Bell className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Notifications</h3>
            <p className="text-[11px] text-slate-400 font-semibold">Real-time status updates and planner alerts</p>
          </div>
        </div>

        {notifications.some(n => n.unread) && (
          <button
            onClick={onMarkAllAsRead}
            className="text-xs text-blue-600 hover:underline font-bold"
          >
            Mark all as read
          </button>
        )}
      </div>

      <div className="white-card p-6 space-y-3">
        {notifications.length === 0 ? (
          <p className="text-xs text-slate-400 italic py-8 text-center">No alerts in your inbox.</p>
        ) : (
          notifications.map((notif) => (
            <div 
              key={notif.id}
              className={`p-4 rounded-xl border flex items-start gap-4 transition-all ${
                notif.unread ? 'bg-blue-50/20 border-blue-100' : 'bg-slate-50/30 border-slate-200'
              }`}
            >
              <div className={`p-2 rounded-xl shrink-0 ${
                notif.type === 'ALERT' ? 'bg-rose-50 text-rose-600' : notif.type === 'INSIGHT' ? 'bg-purple-50 text-purple-600' : 'bg-emerald-50 text-emerald-600'
              }`}>
                {notif.type === 'ALERT' ? <ShieldAlert className="h-4.5 w-4.5" /> : notif.type === 'INSIGHT' ? <Sparkles className="h-4.5 w-4.5" /> : <CheckSquare className="h-4.5 w-4.5" />}
              </div>
              <div className="space-y-1 w-full">
                <div className="flex justify-between items-start gap-4">
                  <p className={`text-xs font-bold ${notif.unread ? 'text-slate-800' : 'text-slate-600'}`}>{notif.title}</p>
                  <span className="text-[10px] text-slate-400 font-bold shrink-0">{notif.time}</span>
                </div>
                <p className="text-xs text-slate-500 leading-normal font-medium">{notif.description}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
}
