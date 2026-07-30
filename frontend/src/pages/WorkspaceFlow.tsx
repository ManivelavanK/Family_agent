import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion, AnimatePresence } from 'framer-motion';
import { authApi } from '../api/authApi';
import { Mail, Lock, ArrowRight, Eye, EyeOff } from 'lucide-react';

export default function WorkspaceFlow() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const login = useAuthStore(state => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
      if (mode === 'login') {
        const data = await authApi.login({ username: email, password });
        login({ name: data.username }, data.family_id, data.access_token, data.role, data.username);
        navigate('/roles');
      } else {
        const data = await authApi.register({ email, password });
        login({ name: data.username }, data.family_id, data.access_token, data.role, data.username);
        navigate('/roles');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 z-10">
      <motion.div
        initial={{ opacity: 0, scale: 0.97, y: 24 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md bg-white/70 backdrop-blur-xl border border-amber-100/50 shadow-2xl shadow-amber-900/10 rounded-3xl p-10 relative overflow-hidden"
      >
        {/* Glow blobs */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-amber-400/20 rounded-full blur-[50px] pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-emerald-400/20 rounded-full blur-[50px] pointer-events-none" />

        {/* Header */}
        <div className="text-center mb-8 relative z-10">
          <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-amber-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-amber-500/30">
            <span className="text-2xl">🏠</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-800 font-serif">KinNest</h1>
          <p className="text-slate-500 text-sm mt-1 font-medium">Family Operating System</p>

          {/* Mode Toggle */}
          <div className="flex mt-5 bg-slate-100 rounded-xl p-1">
            {(['login', 'register'] as const).map(m => (
              <button
                key={m}
                onClick={() => { setMode(m); setErrorMsg(''); }}
                className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                  mode === m
                    ? 'bg-white shadow-sm text-slate-800'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-4 text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-3 rounded-xl relative z-10"
            >
              {errorMsg}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4.5 w-4.5 text-amber-500/70" />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/60 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium text-sm"
                placeholder="you@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4.5 w-4.5 text-amber-500/70" />
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full pl-10 pr-10 py-3 bg-white/60 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium text-sm"
                placeholder={mode === 'register' ? 'Min. 6 characters' : '••••••••'}
                required
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {mode === 'login' && (
            <p className="text-xs text-slate-400 text-center">
              Demo: <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">mother</span> / <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">motherpass</span>
            </p>
          )}

          <motion.button
            whileHover={{ scale: isLoading ? 1 : 1.02 }}
            whileTap={{ scale: isLoading ? 1 : 0.97 }}
            type="submit"
            disabled={isLoading}
            className="w-full py-3.5 mt-2 rounded-xl font-bold shadow-[0_8px_20px_-6px_rgba(217,119,6,0.4)] hover:shadow-[0_10px_28px_-6px_rgba(217,119,6,0.55)] transition-all flex justify-center items-center group relative overflow-hidden disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-amber-400 via-amber-300 to-emerald-300" />
            <span className="relative flex items-center text-slate-800">
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                </>
              ) : (
                <>
                  {mode === 'login' ? 'Sign In' : 'Create Account'}
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </span>
          </motion.button>
        </form>

        <p className="text-xs text-slate-400 text-center mt-6 relative z-10">
          By continuing you agree to the KinNest Family Platform Terms
        </p>
      </motion.div>
    </div>
  );
}