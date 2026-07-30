import { useAuthStore } from '../store/useAuthStore';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Shield, LogOut, Key, Server } from 'lucide-react';

export default function Settings() {
  const { username, role, familyId, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/workspace');
  };

  const infoCards = [
    { label: 'Username',    value: username || '--',      icon: User },
    { label: 'Role',        value: role || '--',           icon: Shield },
    { label: 'Family ID',  value: familyId || '--',       icon: Key },
    { label: 'Backend',     value: 'localhost:8000',       icon: Server },
  ];

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 text-sm mt-1">Your KinNest account and workspace configuration</p>
      </div>

      {/* Account Info */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="font-semibold text-slate-800 mb-5 text-lg">Account Information</h2>
        <div className="space-y-4">
          {infoCards.map((card, i) => (
            <motion.div key={card.label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
              className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center">
                  <card.icon className="w-4 h-4 text-slate-500" />
                </div>
                <span className="text-sm text-slate-500 font-medium">{card.label}</span>
              </div>
              <span className="text-sm font-semibold text-slate-800 font-mono bg-slate-50 px-3 py-1 rounded-lg">{card.value}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Role Permissions */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="font-semibold text-slate-800 mb-4 text-lg">Role Permissions</h2>
        <div className="space-y-2 text-sm">
          {[
            { context: 'budget',   access: role?.toLowerCase() === 'parent' ? 'WRITE' : 'NONE' },
            { context: 'shopping', access: 'WRITE' },
            { context: 'health',   access: role?.toLowerCase() === 'parent' ? 'WRITE' : 'READ' },
            { context: 'child',    access: 'WRITE' },
            { context: 'baby',     access: role?.toLowerCase() === 'baby caregiver' ? 'WRITE' : 'READ' },
            { context: 'planner',  access: 'WRITE' },
          ].map(item => (
            <div key={item.context} className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
              <span className="text-slate-600 capitalize font-medium">{item.context}</span>
              <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                item.access === 'WRITE' ? 'bg-emerald-100 text-emerald-700' :
                item.access === 'READ' ? 'bg-blue-100 text-blue-700' :
                'bg-red-100 text-red-600'}`}>
                {item.access}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Logout */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleLogout}
        className="w-full flex items-center justify-center space-x-2 py-3.5 bg-red-50 border border-red-200 text-red-600 font-semibold rounded-xl hover:bg-red-100 transition-colors"
      >
        <LogOut className="w-4 h-4" />
        <span>Logout from KinNest</span>
      </motion.button>
    </div>
  );
}