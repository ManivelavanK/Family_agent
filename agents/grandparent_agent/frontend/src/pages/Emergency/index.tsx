import React, { useEffect, useState } from 'react';
import { emergencyService } from '../../services/emergencyService';
import { EmergencyAlert } from '../../types';
import { AlertTriangle, Phone, CheckCircle, Clock, ShieldAlert, Siren } from 'lucide-react';
import toast from 'react-hot-toast';
import StatusBadge from '../../components/common/StatusBadge';
import { motion, AnimatePresence } from 'framer-motion';

export const Emergency: React.FC = () => {
  const [history, setHistory] = useState<EmergencyAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [sosActive, setSosActive] = useState(false);

  const emergencyContacts = [
    { name: 'Karthik Srinivasan', relation: 'Son (Primary Contact)', phone: '+91 98765 43210' },
    { name: 'Dr. Srinivasa Raghavan', relation: 'Diabetologist', phone: '+91 44 2345 6789' },
    { name: 'Kauvery Hospital Emergency', relation: 'Hospital 24/7 Emergency Line', phone: '1800-419-1019' },
    { name: 'National Emergency', relation: 'Ambulance Services', phone: '108' },
  ];

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await emergencyService.getSOSHistory();
      setHistory(data);
    } catch (e) {
      toast.error('Failed to load SOS history.');
    } finally {
      setLoading(false);
    }
  };

  const handleSOS = async () => {
    setTriggering(true);
    setSosActive(true);
    try {
      const res = await emergencyService.triggerSOS();
      toast.error(`🚨 EMERGENCY ALERT SENT! Notified: ${res.contact_notified}`, {
        duration: 10000,
        position: 'top-center',
        style: {
          border: '3px solid #e11d48',
          padding: '20px',
          color: '#9f1239',
          fontSize: '20px',
          fontWeight: 'bold',
          background: '#fff1f2',
        },
      });
      loadHistory();
    } catch (e) {
      toast.error('Network error — offline SOS triggered locally.');
    } finally {
      setTriggering(false);
      setTimeout(() => setSosActive(false), 5000);
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await emergencyService.resolveSOS(id);
      toast.success('Alert resolved and contacts notified.');
      loadHistory();
    } catch (e) {
      toast.error('Failed to resolve alert.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Giant SOS Button Hero */}
      <div className="bg-gradient-to-br from-rose-50 to-rose-100 border-2 border-rose-200 rounded-3xl p-8 md:p-12 flex flex-col items-center justify-center text-center gap-6">
        <div className="flex items-center gap-3 text-rose-700">
          <ShieldAlert className="h-8 w-8" />
          <h3 className="text-2xl font-extrabold">Emergency SOS System</h3>
        </div>
        <p className="text-base font-semibold text-rose-600 max-w-md">
          Press the button below during any medical emergency. Your son, doctor, and nearby hospital will be instantly alerted.
        </p>

        <AnimatePresence>
          <motion.button
            onClick={handleSOS}
            disabled={triggering}
            className={`relative flex flex-col items-center justify-center w-52 h-52 rounded-full border-8 font-black text-2xl text-white shadow-2xl transition-all cursor-pointer
              ${triggering
                ? 'bg-rose-400 border-rose-300 animate-pulse'
                : 'bg-rose-600 border-rose-400 hover:bg-rose-700 active:scale-95 hover:scale-105'
              }`}
            whileTap={{ scale: 0.92 }}
          >
            <Siren className="h-14 w-14 mb-2" />
            <span className="text-xl font-black">{triggering ? 'SENDING...' : 'SOS'}</span>
            <span className="text-sm font-bold opacity-80">EMERGENCY</span>

            {sosActive && (
              <motion.div
                className="absolute inset-0 rounded-full border-8 border-rose-400"
                initial={{ scale: 1, opacity: 0.8 }}
                animate={{ scale: 1.6, opacity: 0 }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
            )}
          </motion.button>
        </AnimatePresence>

        <p className="text-xs font-semibold text-rose-400">Hold your phone clearly and stay still after pressing.</p>
      </div>

      {/* Emergency Contacts Grid */}
      <div>
        <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Phone className="h-5 w-5 text-sky-500" />
          <span>Emergency Contacts Directory</span>
        </h4>
        <div className="grid gap-4 md:grid-cols-2">
          {emergencyContacts.map((c, i) => (
            <div key={i} className="bg-white border border-sky-100 p-5 rounded-2xl flex items-center justify-between hover:shadow-md transition-shadow">
              <div>
                <h5 className="text-base font-black text-slate-800">{c.name}</h5>
                <span className="text-xs font-semibold text-slate-400">{c.relation}</span>
                <span className="block text-base font-bold text-sky-700 mt-1">{c.phone}</span>
              </div>
              <a
                href={`tel:${c.phone.replace(/\s/g, '')}`}
                className="flex items-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm rounded-xl transition-colors"
              >
                <Phone className="h-4 w-4" />
                <span>Call</span>
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* SOS History Log */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h4 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Clock className="h-5 w-5 text-slate-400" />
            <span>SOS Alert History</span>
          </h4>
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent" />
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {history.map((alert) => (
              <div key={alert.id} className="p-5 flex items-start justify-between gap-4 hover:bg-slate-50/50">
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 p-2 rounded-xl ${alert.status === 'Resolved' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
                    {alert.status === 'Resolved' ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-800">{alert.message}</p>
                    <p className="text-xs font-semibold text-slate-400 mt-0.5">
                      {new Date(alert.timestamp).toLocaleString()} · Notified: {alert.contact_notified}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <StatusBadge status={alert.status} />
                  {alert.status !== 'Resolved' && (
                    <button
                      onClick={() => handleResolve(alert.id)}
                      className="text-xs font-bold px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors cursor-pointer"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            ))}
            {history.length === 0 && (
              <p className="text-center py-8 text-slate-400 font-medium">No SOS alerts triggered yet. System is ready.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
export default Emergency;
