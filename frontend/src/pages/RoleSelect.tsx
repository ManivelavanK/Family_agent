import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LogOut, ArrowRight, ArrowLeft, Lock, Home, CheckCircle, Copy, X, Loader
} from 'lucide-react';
import { authApi } from '../api/authApi';

// ── Role Card Config ─────────────────────────────────────────────────────────
const ROLES = [
  {
    id: 'father',
    label: 'Father',
    emoji: '👨',
    color: 'from-blue-500 to-blue-700',
    light: 'bg-blue-50 border-blue-200',
    accent: 'text-blue-600',
    ring: 'ring-blue-400',
    desc: 'Budget, Finance & Family Decisions',
    role: 'Parent',
    path: '/father',
    canSetup: true,
  },
  {
    id: 'mother',
    label: 'Mother',
    emoji: '👩',
    color: 'from-pink-500 to-rose-600',
    light: 'bg-pink-50 border-pink-200',
    accent: 'text-pink-600',
    ring: 'ring-pink-400',
    desc: 'Shopping, Groceries & Home Care',
    role: 'Parent',
    path: '/mother',
    canSetup: true,
  },
  {
    id: 'grandparent',
    label: 'Grandparent',
    emoji: '👴',
    color: 'from-emerald-500 to-teal-600',
    light: 'bg-emerald-50 border-emerald-200',
    accent: 'text-emerald-600',
    ring: 'ring-emerald-400',
    desc: 'Health, Wellness & Wisdom',
    role: 'Grandparent',
    path: '/grandparent',
    canSetup: true,
  },
  {
    id: 'child',
    label: 'Child',
    emoji: '👧',
    color: 'from-amber-500 to-orange-600',
    light: 'bg-amber-50 border-amber-200',
    accent: 'text-amber-600',
    ring: 'ring-amber-400',
    desc: 'Education, Tasks & Activities',
    role: 'Child',
    path: '/children',
    canSetup: false,
  },
  {
    id: 'baby',
    label: 'Baby Caregiver',
    emoji: '👶',
    color: 'from-violet-500 to-purple-700',
    light: 'bg-violet-50 border-violet-200',
    accent: 'text-violet-600',
    ring: 'ring-violet-400',
    desc: 'Infant Monitoring & Caregiving',
    role: 'Baby Caregiver',
    path: '/baby',
    canSetup: false,
  },
  {
    id: 'planner',
    label: 'Life Planner',
    emoji: '📅',
    color: 'from-indigo-500 to-blue-700',
    light: 'bg-indigo-50 border-indigo-200',
    accent: 'text-indigo-600',
    ring: 'ring-indigo-400',
    desc: 'Events, Goals & Family Planning',
    role: 'Parent',
    path: '/planner',
    canSetup: false,
  },
];

// ── Setup Wizard (multi-step) ────────────────────────────────────────────────
function SetupWizard({ roleConfig, onClose, onSuccess }: {
  roleConfig: typeof ROLES[0];
  onClose: () => void;
  onSuccess: (token: string, familyId: string, role: string, familyName: string, familyPw: string) => void;
}) {
  const { username } = useAuthStore();
  const [step, setStep] = useState(1);
  const [familyName, setFamilyName] = useState('');
  const [houseAddress, setHouseAddress] = useState('');
  const [memberCount, setMemberCount] = useState('4');
  const [childrenAges, setChildrenAges] = useState('');
  const [specialNeeds, setSpecialNeeds] = useState('');
  const [familyPassword, setFamilyPassword] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSetup = async () => {
    if (familyPassword !== confirmPw) { setError('Passwords do not match.'); return; }
    if (familyPassword.length < 4) { setError('Family password must be at least 4 characters.'); return; }
    setLoading(true); setError('');
    try {
      const data = await authApi.setupFamily({
        email: username,
        role: roleConfig.role,
        family_name: familyName,
        house_address: houseAddress,
        member_count: memberCount,
        children_ages: childrenAges,
        special_needs: specialNeeds,
        family_password: familyPassword
      });
      onSuccess(data.access_token, data.family_id, data.role, data.family_name, familyPassword);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 20 }}
        className="w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className={`bg-gradient-to-r ${roleConfig.color} p-6 text-white relative`}>
          <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30 transition-colors">
            <X className="w-4 h-4" />
          </button>
          <div className="text-4xl mb-2">{roleConfig.emoji}</div>
          <h2 className="text-2xl font-bold">Set Up as {roleConfig.label}</h2>
          <p className="text-white/80 text-sm mt-1">Create your family workspace</p>
          {/* Step dots */}
          <div className="flex space-x-2 mt-4">
            {[1,2,3].map(s => (
              <div key={s} className={`h-1.5 rounded-full transition-all ${s <= step ? 'bg-white w-8' : 'bg-white/30 w-4'}`} />
            ))}
          </div>
        </div>

        <div className="p-6">
          {error && <div className="mb-4 text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-2 rounded-xl">{error}</div>}

          {/* Step 1: Family Details */}
          {step === 1 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
              <h3 className="text-lg font-bold text-slate-800">Family Details</h3>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Family Name *</label>
                <input value={familyName} onChange={e => setFamilyName(e.target.value)}
                  placeholder="e.g. The Kumars" required
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Home Address *</label>
                <input value={houseAddress} onChange={e => setHouseAddress(e.target.value)}
                  placeholder="123 Main Street, Chennai"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <button
                onClick={() => { if (!familyName.trim()) { setError('Family name is required.'); return; } setError(''); setStep(2); }}
                className="w-full py-3 bg-slate-900 text-white rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-800 transition-colors">
                Continue <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </motion.div>
          )}

          {/* Step 2: Family Profile */}
          {step === 2 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
              <h3 className="text-lg font-bold text-slate-800">About Your Family</h3>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Total Family Members</label>
                <select value={memberCount} onChange={e => setMemberCount(e.target.value)}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300">
                  {['2','3','4','5','6','7','8+'].map(n => <option key={n} value={n}>{n} members</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Children's Ages (optional)</label>
                <input value={childrenAges} onChange={e => setChildrenAges(e.target.value)}
                  placeholder="e.g. 5, 8, 12"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Special Needs / Notes (optional)</label>
                <input value={specialNeeds} onChange={e => setSpecialNeeds(e.target.value)}
                  placeholder="e.g. Diabetic grandparent, nut allergy"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <div className="flex space-x-3">
                <button onClick={() => setStep(1)} className="flex-1 py-3 border border-slate-200 text-slate-600 rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-50">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Back
                </button>
                <button onClick={() => { setError(''); setStep(3); }}
                  className="flex-1 py-3 bg-slate-900 text-white rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-800 transition-colors">
                  Continue <ArrowRight className="w-4 h-4 ml-2" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Family Password */}
          {step === 3 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
              <h3 className="text-lg font-bold text-slate-800">Set Family Password</h3>
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
                <Lock className="w-4 h-4 inline mr-1.5 mb-0.5" />
                This password is shared with your family. Others use it to <strong>connect</strong> to your family workspace.
              </div>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Family Password *</label>
                <input type="password" value={familyPassword} onChange={e => setFamilyPassword(e.target.value)}
                  placeholder="Min. 4 characters"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <div>
                <label className="text-sm font-semibold text-slate-600 block mb-1">Confirm Family Password *</label>
                <input type="password" value={confirmPw} onChange={e => setConfirmPw(e.target.value)}
                  placeholder="Re-enter password"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
              </div>
              <div className="flex space-x-3">
                <button onClick={() => setStep(2)} className="flex-1 py-3 border border-slate-200 text-slate-600 rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-50">
                  <ArrowLeft className="w-4 h-4 mr-2" /> Back
                </button>
                <button onClick={handleSetup} disabled={loading}
                  className={`flex-1 py-3 rounded-xl font-semibold text-sm flex items-center justify-center transition-colors bg-gradient-to-r ${roleConfig.color} text-white hover:opacity-90 disabled:opacity-60`}>
                  {loading ? <Loader className="w-4 h-4 animate-spin mr-2" /> : null}
                  {loading ? 'Creating...' : 'Create Family'}
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Join Family Modal (using family password) ────────────────────────────────
function JoinFamilyModal({ roleConfig, onClose, onSuccess }: {
  roleConfig: typeof ROLES[0];
  onClose: () => void;
  onSuccess: (token: string, familyId: string, role: string) => void;
}) {
  const { username } = useAuthStore();
  const [familyPassword, setFamilyPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConnect = async () => {
    if (!familyPassword.trim()) { setError('Please enter the family password.'); return; }
    setLoading(true); setError('');
    try {
      const data = await authApi.connectFamily({
        email: username,
        role: roleConfig.role,
        family_password: familyPassword
      });
      onSuccess(data.access_token, data.family_id, data.role);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 20 }}
        className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden">
        <div className={`bg-gradient-to-r ${roleConfig.color} p-6 text-white relative`}>
          <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30">
            <X className="w-4 h-4" />
          </button>
          <div className="text-4xl mb-2">{roleConfig.emoji}</div>
          <h2 className="text-2xl font-bold">Join as {roleConfig.label}</h2>
          <p className="text-white/80 text-sm mt-1">Enter your family's shared password</p>
        </div>
        <div className="p-6 space-y-4">
          {error && <div className="text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-2 rounded-xl">{error}</div>}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm text-slate-600">
            Ask your family admin (<strong>Father or Mother</strong>) for the shared family password to connect.
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-600 block mb-1">Family Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input type="password" value={familyPassword} onChange={e => setFamilyPassword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleConnect()}
                placeholder="Enter family password"
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-amber-300" />
            </div>
          </div>
          <button onClick={handleConnect} disabled={loading}
            className={`w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center text-white transition-all bg-gradient-to-r ${roleConfig.color} hover:opacity-90 disabled:opacity-60`}>
            {loading ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <ArrowRight className="w-4 h-4 mr-2" />}
            {loading ? 'Connecting...' : 'Connect to Family'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Success Screen shown after family setup ──────────────────────────────────
function FamilySetupSuccess({ roleConfig, familyPassword, onContinue }: {
  roleConfig: typeof ROLES[0];
  familyPassword: string;
  onContinue: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(familyPassword); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 text-center">
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.15, type: 'spring' }}>
          <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
        </motion.div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Family Created! 🎉</h2>
        <p className="text-slate-600 text-sm mb-6">Share this password with your family members so they can connect.</p>
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-6">
          <p className="text-xs text-slate-500 font-medium mb-2">Family Password</p>
          <div className="flex items-center justify-between bg-white rounded-xl px-4 py-3 border border-amber-200">
            <span className="text-xl font-bold tracking-widest text-slate-800">{familyPassword}</span>
            <button onClick={copy} className="ml-3 p-1.5 rounded-lg hover:bg-amber-100 transition-colors">
              {copied ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-amber-600" />}
            </button>
          </div>
        </div>
        <button onClick={onContinue}
          className={`w-full py-3 rounded-xl font-bold text-white bg-gradient-to-r ${roleConfig.color} flex items-center justify-center hover:opacity-90`}>
          Enter as {roleConfig.label} <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </motion.div>
    </motion.div>
  );
}

// ── Role Option Modal (shown on first click if no family) ────────────────────
function RoleOptionModal({ roleConfig, onClose, onSetup, onJoin }: {
  roleConfig: typeof ROLES[0];
  onClose: () => void;
  onSetup: () => void;
  onJoin: () => void;
}) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 20 }}
        className="w-full max-w-sm bg-white rounded-3xl shadow-2xl overflow-hidden">
        <div className={`bg-gradient-to-r ${roleConfig.color} p-6 text-white relative`}>
          <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30">
            <X className="w-4 h-4" />
          </button>
          <div className="text-4xl mb-2">{roleConfig.emoji}</div>
          <h2 className="text-xl font-bold">{roleConfig.label}</h2>
          <p className="text-white/80 text-xs mt-1">{roleConfig.desc}</p>
        </div>
        <div className="p-5 space-y-3">
          <p className="text-slate-600 text-sm font-medium text-center mb-4">How do you want to join?</p>

          {roleConfig.canSetup && (
            <button onClick={onSetup}
              className="w-full bg-slate-900 text-white py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-800 transition-colors">
              <Home className="w-4 h-4 mr-2" /> Set Up My Family Workspace
            </button>
          )}
          <button onClick={onJoin}
            className="w-full border-2 border-slate-200 text-slate-700 py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center hover:bg-slate-50 transition-colors">
            <Lock className="w-4 h-4 mr-2" /> Join with Family Password
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Main RoleSelect Page ─────────────────────────────────────────────────────
export default function RoleSelect() {
  const navigate = useNavigate();
  const { username, hasFamilySetup, logout, setFamilyConnected } = useAuthStore();

  const [activeCard, setActiveCard] = useState<typeof ROLES[0] | null>(null);
  const [modalMode, setModalMode] = useState<'option' | 'setup' | 'join' | null>(null);
  const [setupSuccessData, setSetupSuccessData] = useState<{ familyPassword: string; role: typeof ROLES[0] } | null>(null);

  const handleCardClick = (card: typeof ROLES[0]) => {
    setActiveCard(card);
    if (hasFamilySetup) {
      // Already connected — go directly to agent dashboard
      navigate(card.path);
    } else {
      setModalMode('option');
    }
  };

  const handleSetupSuccess = (newToken: string, familyId: string, role: string, _familyName: string, familyPw: string) => {
    setFamilyConnected(familyId, role, newToken);
    setModalMode(null);
    setSetupSuccessData({ familyPassword: familyPw, role: activeCard! });
  };

  const handleConnectSuccess = (newToken: string, familyId: string, role: string) => {
    setFamilyConnected(familyId, role, newToken);
    setModalMode(null);
    if (activeCard) navigate(activeCard.path);
  };

  const handleLogout = () => { logout(); navigate('/workspace'); };

  const gridVariants = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
  const cardVariants = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

  return (
    <div className="min-h-screen relative z-10 flex flex-col">
      {/* Top nav */}
      <div className="flex items-center justify-between px-8 py-5">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl flex items-center justify-center shadow-md">
            <span className="text-lg">🏠</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800">KinNest</h1>
            <p className="text-xs text-slate-500">{username || 'Family OS'}</p>
          </div>
        </div>
        <button onClick={handleLogout}
          className="flex items-center space-x-2 text-sm text-slate-500 hover:text-red-500 bg-white/60 border border-slate-200 px-4 py-2 rounded-xl transition-colors">
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h2 className="text-4xl font-bold text-slate-800 font-serif mb-3">
            Who are you in the family?
          </h2>
          <p className="text-slate-500 text-lg max-w-xl mx-auto">
            Choose your role to enter your personalized AI agent workspace.
            {!hasFamilySetup && <span className="text-amber-600 font-medium"> First time? Set up or join your family below.</span>}
          </p>
        </motion.div>

        {/* 6 Role Cards */}
        <motion.div
          variants={gridVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 w-full max-w-4xl"
        >
          {ROLES.map((card) => (
            <motion.button
              key={card.id}
              variants={cardVariants}
              whileHover={{ scale: 1.03, y: -4 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => handleCardClick(card)}
              className="group relative bg-white/80 backdrop-blur-sm border border-white/60 rounded-2xl p-6 shadow-lg shadow-slate-200/60 hover:shadow-xl hover:shadow-slate-300/60 transition-all text-left overflow-hidden"
            >
              {/* Gradient top bar */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${card.color}`} />

              {/* Content */}
              <div className="flex items-start space-x-4">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center text-2xl shadow-md flex-shrink-0`}>
                  {card.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-slate-800 mb-1">{card.label}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{card.desc}</p>
                </div>
              </div>

              <div className={`mt-4 flex items-center text-xs font-semibold ${card.accent} group-hover:translate-x-1 transition-transform`}>
                Enter workspace <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </div>

              {/* Connected badge */}
              {hasFamilySetup && (
                <div className="absolute top-3 right-3 w-2.5 h-2.5 bg-emerald-400 rounded-full ring-2 ring-white" />
              )}
            </motion.button>
          ))}
        </motion.div>
      </div>

      {/* Modals */}
      <AnimatePresence>
        {activeCard && modalMode === 'option' && (
          <RoleOptionModal
            roleConfig={activeCard}
            onClose={() => { setModalMode(null); setActiveCard(null); }}
            onSetup={() => setModalMode('setup')}
            onJoin={() => setModalMode('join')}
          />
        )}
        {activeCard && modalMode === 'setup' && (
          <SetupWizard
            roleConfig={activeCard}
            onClose={() => { setModalMode(null); setActiveCard(null); }}
            onSuccess={handleSetupSuccess}
          />
        )}
        {activeCard && modalMode === 'join' && (
          <JoinFamilyModal
            roleConfig={activeCard}
            onClose={() => { setModalMode(null); setActiveCard(null); }}
            onSuccess={handleConnectSuccess}
          />
        )}
        {setupSuccessData && (
          <FamilySetupSuccess
            roleConfig={setupSuccessData.role}
            familyPassword={setupSuccessData.familyPassword}
            onContinue={() => { setSetupSuccessData(null); navigate(setupSuccessData.role.path); }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
