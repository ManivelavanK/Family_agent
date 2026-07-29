import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { Mail, Lock, UserPlus, Users, ArrowRight } from 'lucide-react';

export default function WorkspaceFlow() {
  const [mode, setMode] = useState<'login' | 'create' | 'join'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [familyName, setFamilyName] = useState('');
  const [houseAddress, setHouseAddress] = useState('');
  const [role, setRole] = useState('Father');
  const [workspaceCode, setWorkspaceCode] = useState('');
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
        const res = await fetch('http://localhost:8000/orchestrator/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: email, password })
        });
        if (!res.ok) throw new Error('Login failed');
        const data = await res.json();
        login({ name: email }, data.family_id || 'KIN-29431', data.access_token);
        navigate('/dashboard');
      } else {
        // For create/join
        const res = await fetch('http://localhost:8000/orchestrator/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            username: mode === 'create' ? familyName : email, // Or whatever the backend expects, usually username/email
            password: mode === 'create' ? 'default_pass' : password, // using placeholders if they are not in the form
            role, 
            family_id: mode === 'join' ? workspaceCode : 'NEW_FAMILY' 
          })
        });
        if (!res.ok) throw new Error('Registration failed');
        const data = await res.json();
        login({ name: email || familyName }, data.family_id, data.access_token);
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 z-10">
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.98, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md bg-white/70 backdrop-blur-xl border border-amber-100/50 shadow-2xl shadow-amber-900/10 rounded-3xl p-10 relative overflow-hidden"
      >
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-amber-400/20 rounded-full blur-[40px] pointer-events-none"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-emerald-400/20 rounded-full blur-[40px] pointer-events-none"></div>

        <div className="text-center mb-8 relative z-10">
          <h2 className="text-4xl font-bold text-slate-800 mb-2 font-serif text-glow-gold">
            {mode === 'login' ? 'Welcome Back' : mode === 'create' ? 'Create Workspace' : 'Join Workspace'}
          </h2>
          <p className="text-slate-600 font-medium">KinNest Family Operating System</p>
          {errorMsg && <p className="text-red-500 mt-2 text-sm bg-red-50/80 px-3 py-1 rounded-md inline-block">{errorMsg}</p>}
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
          {mode === 'create' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Family Name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Users className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input type="text" value={familyName} onChange={e => setFamilyName(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="e.g. The Smiths" required />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">House Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserPlus className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input type="text" value={houseAddress} onChange={e => setHouseAddress(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="Home address" required />
                </div>
              </div>
            </>
          )}

          {mode === 'join' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Role</label>
                <select value={role} onChange={e => setRole(e.target.value)} className="w-full px-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all text-slate-700 font-medium appearance-none" required>
                  <option value="Father">Father</option>
                  <option value="Mother">Mother</option>
                  <option value="Child">Child</option>
                  <option value="Grandparent">Grandparent</option>
                  <option value="Baby Caregiver">Baby Caregiver</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Workspace Code</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input type="text" value={workspaceCode} onChange={e => setWorkspaceCode(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="Enter join code" required />
                </div>
              </div>
            </>
          )}

          {mode === 'login' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Email</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="hello@family.com" required />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="••••••••" required />
                </div>
              </div>
            </>
          )}

          <motion.button
            whileHover={{ scale: isLoading ? 1 : 1.02 }}
            whileTap={{ scale: isLoading ? 1 : 0.98 }}
            type="submit"
            disabled={isLoading}
            className="w-full py-3.5 mt-2 rounded-xl text-slate-800 font-bold shadow-[0_8px_20px_-6px_rgba(217,119,6,0.3)] hover:shadow-[0_10px_25px_-6px_rgba(217,119,6,0.5)] transition-all flex justify-center items-center group relative overflow-hidden disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-amber-300 via-amber-200 to-emerald-200"></div>
            <span className="relative flex items-center">
              {isLoading ? 'Loading...' : mode === 'login' ? 'Enter KinNest' : 'Continue'}
              {!isLoading && <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />}
            </span>
          </motion.button>
        </form>

        <div className="mt-8 text-center space-y-3 relative z-10">
          {mode !== 'login' && (
            <button
              onClick={() => setMode('login')}
              className="text-sm font-medium text-slate-500 hover:text-amber-700 transition-colors block w-full relative after:content-[''] after:absolute after:-bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-0 after:h-0.5 after:bg-amber-400 after:transition-all hover:after:w-8"
            >
              Back to Login
            </button>
          )}
          {mode === 'login' && (
            <>
              <button
                onClick={() => setMode('create')}
                className="text-sm font-medium text-slate-600 hover:text-amber-700 transition-colors block w-full relative group"
              >
                Create a new Family Workspace
                <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-amber-400 transition-all duration-300 group-hover:w-16"></span>
              </button>
              <button
                onClick={() => setMode('join')}
                className="text-sm font-medium text-slate-600 hover:text-emerald-700 transition-colors block w-full relative group"
              >
                Join an existing Family Workspace
                <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-emerald-400 transition-all duration-300 group-hover:w-16"></span>
              </button>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}