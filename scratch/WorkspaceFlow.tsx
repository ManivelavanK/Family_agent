import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { Mail, Lock, UserPlus, Users, ArrowRight } from 'lucide-react';

export default function WorkspaceFlow() {
  const [mode, setMode] = useState<'login' | 'create' | 'join'>('login');
  
  // Form input states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Parent');
  const [familyId, setFamilyId] = useState('default_family');
  const [familyName, setFamilyName] = useState('');
  
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const login = useAuthStore(state => state.login);

  // Decoder helper to extract claims from base64 JWT payload
  const decodeTokenClaims = (token: string) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        window.atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    
    // Normalize email/username (stripping domains if they entered an email address)
    const username = email.split('@')[0];
    
    try {
      if (mode === 'login') {
        const response = await fetch('http://localhost:8000/orchestrator/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || 'Login failed.');
        }
        
        const data = await response.json();
        const claims = decodeTokenClaims(data.access_token);
        login(
          { username: claims?.sub || username, role: claims?.role || 'Parent' }, 
          claims?.family_id || 'default_family', 
          data.access_token
        );
        navigate('/dashboard');
        
      } else {
        // Register (create or join)
        const targetFamilyId = mode === 'create' ? familyName.toLowerCase().replace(/\s+/g, '_') : familyId;
        
        const response = await fetch('http://localhost:8000/orchestrator/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username,
            password,
            role: mode === 'create' ? 'Parent' : role, // workspace creator is Parent admin by default
            family_id: targetFamilyId
          }),
        });
        
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || 'Registration failed.');
        }
        
        const data = await response.json();
        const claims = decodeTokenClaims(data.access_token);
        login(
          { username: claims?.sub || username, role: claims?.role || 'Parent' }, 
          claims?.family_id || targetFamilyId, 
          data.access_token
        );
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An unexpected authentication error occurred.');
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 z-10">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
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
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 text-sm font-semibold rounded-xl text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Username / Email</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-amber-500/70" />
              </div>
              <input 
                type="text" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" 
                placeholder="mother or mother@family.com" 
                required 
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-amber-500/70" />
              </div>
              <input 
                type="password" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" 
                placeholder="••••••••" 
                required 
              />
            </div>
          </div>

          {mode === 'create' && (
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Family Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Users className="h-5 w-5 text-amber-500/70" />
                </div>
                <input 
                  type="text" 
                  value={familyName}
                  onChange={e => setFamilyName(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" 
                  placeholder="e.g. Smiths" 
                  required 
                />
              </div>
            </div>
          )}

          {mode === 'join' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Role</label>
                <select 
                  value={role}
                  onChange={e => setRole(e.target.value)}
                  className="w-full px-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all text-slate-700 font-medium" 
                  required
                >
                  <option value="Parent">Parent</option>
                  <option value="Grandparent">Grandparent</option>
                  <option value="Child">Child</option>
                  <option value="Baby">Baby</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Family Workspace ID</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-amber-500/70" />
                  </div>
                  <input 
                    type="text" 
                    value={familyId}
                    onChange={e => setFamilyId(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" 
                    placeholder="default_family" 
                    required 
                  />
                </div>
              </div>
            </>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="w-full py-3.5 mt-2 rounded-xl text-slate-800 font-bold shadow-[0_8px_20px_-6px_rgba(217,119,6,0.3)] hover:shadow-[0_10px_25px_-6px_rgba(217,119,6,0.5)] transition-all flex justify-center items-center group relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-amber-300 via-amber-200 to-emerald-200"></div>
            <span className="relative flex items-center">
              {mode === 'login' ? 'Enter KinNest' : 'Continue'}
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
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
