import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { UserCircle, Users, Baby, Calendar, CheckCircle2, ShieldAlert, ChevronRight, Image as ImageIcon } from 'lucide-react';

const AgentCard = ({ agent }: { agent: any }) => {
  const Icon = agent.icon;

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 40 },
        visible: { opacity: 1, y: 0 }
      }}
      whileHover={{ 
        rotateX: 2, 
        rotateY: -2, 
        scale: 1.02,
        boxShadow: "0 25px 50px -12px rgba(217, 119, 6, 0.15)",
        borderColor: "rgba(252, 211, 77, 0.8)"
      }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className="glass-panel-light p-7 flex flex-col h-full cursor-pointer group"
      style={{ transformPerspective: 1000 }}
    >
      <div className="flex items-center mb-5">
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${agent.bgColor} mr-4 shadow-sm`}>
          <Icon className={`w-6 h-6 ${agent.iconColor}`} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-800">{agent.name}</h3>
          <p className="text-sm text-slate-500 font-medium">{agent.role}</p>
        </div>
      </div>
      
      <div className="flex-1">
        {/* Status Pill */}
        <div className="inline-flex items-center px-3 py-1.5 rounded-full bg-slate-100/80 border border-slate-200/60 text-xs font-semibold text-slate-600 mb-4 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
          {agent.status}
        </div>
        
        {/* Interactive Preview Content */}
        <div className="bg-white/50 rounded-xl p-4 border border-white/60 shadow-inner h-28 flex flex-col justify-center">
          {agent.previewContent}
        </div>
      </div>
    </motion.div>
  );
};

export default function Landing() {
  const containerRef = useRef(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [buttonPulse, setButtonPulse] = useState(false);
  const navigate = useNavigate();

  const handleLaunch = () => {
    setButtonPulse(true);
    setTimeout(() => {
      setIsNavigating(true);
      setTimeout(() => {
        navigate('/workspace');
      }, 1200); // Wait for transition animation
    }, 300); // Wait for button pulse
  };

  const agents = [
    { 
      id: 'father', 
      name: 'Father Agent', 
      role: 'Finances & Security',
      icon: UserCircle, 
      bgColor: 'bg-blue-50', 
      iconColor: 'text-blue-600',
      status: 'Tax records synced',
      previewContent: (
        <div className="w-full">
          <div className="flex justify-between text-xs text-slate-600 mb-1 font-medium">
            <span>Monthly Budget</span>
            <span>$4,200 / $5,000</span>
          </div>
          <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }} 
              whileInView={{ width: '84%' }} 
              transition={{ duration: 1.5, delay: 0.5 }}
              className="h-full bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"
            />
          </div>
        </div>
      )
    },
    { 
      id: 'mother', 
      name: 'Mother Agent', 
      role: 'Household & Wellness',
      icon: UserCircle, 
      bgColor: 'bg-pink-50', 
      iconColor: 'text-pink-600',
      status: 'Meal plan & groceries ready',
      previewContent: (
        <div className="space-y-2">
          <div className="flex items-center text-sm text-slate-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-500 mr-2" />
            <span className="line-through text-slate-400">Order organic milk</span>
          </div>
          <div className="flex items-center text-sm text-slate-700">
            <div className="w-4 h-4 border-2 border-slate-300 rounded-full mr-2"></div>
            <span>Schedule dentist for kids</span>
          </div>
        </div>
      )
    },
    { 
      id: 'children', 
      name: 'Children Agent', 
      role: 'Education & Growth',
      icon: Users, 
      bgColor: 'bg-amber-50', 
      iconColor: 'text-amber-600',
      status: 'Math assignment reminder set',
      previewContent: (
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Active Milestone</p>
            <p className="text-sm font-bold text-slate-800">Reading Level 4</p>
          </div>
          <div className="w-12 h-12 rounded-full border-4 border-amber-100 flex items-center justify-center border-t-amber-500 relative rotate-45">
            <span className="absolute -rotate-45 text-xs font-bold text-amber-600">80%</span>
          </div>
        </div>
      )
    },
    { 
      id: 'grandparent', 
      name: 'Grandparent Agent', 
      role: 'Care & Health Routines',
      icon: UserCircle, 
      bgColor: 'bg-emerald-50', 
      iconColor: 'text-emerald-600',
      status: 'Medication track on time',
      previewContent: (
        <div className="flex items-center justify-center space-x-4">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex flex-col items-center justify-center bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl py-2 px-4 border border-rose-100 transition-colors w-full"
          >
            <ShieldAlert className="w-6 h-6 mb-1" />
            <span className="text-xs font-bold">Emergency Ping</span>
          </motion.button>
        </div>
      )
    },
    { 
      id: 'baby', 
      name: 'Baby Care Agent', 
      role: 'Sleep & Feed Tracker',
      icon: Baby, 
      bgColor: 'bg-violet-50', 
      iconColor: 'text-violet-600',
      status: 'Next feeding in 1h 20m',
      previewContent: (
        <div className="w-full flex items-end justify-between h-12 px-2">
          {[40, 70, 30, 90, 60, 100, 50].map((height, i) => (
            <motion.div 
              key={i}
              initial={{ height: 0 }}
              whileInView={{ height: `${height}%` }}
              transition={{ duration: 0.8, delay: 0.5 + (i * 0.1) }}
              className="w-3 bg-violet-400 rounded-t-sm opacity-80 hover:opacity-100"
            />
          ))}
        </div>
      )
    },
    { 
      id: 'planner', 
      name: 'Life Planner Agent', 
      role: 'Events & Memories',
      icon: Calendar, 
      bgColor: 'bg-indigo-50', 
      iconColor: 'text-indigo-600',
      status: 'Weekend trip itinerary drafted',
      previewContent: (
        <div className="flex space-x-2 overflow-hidden">
          <div className="w-16 h-16 rounded-lg bg-slate-200 bg-[url('https://images.unsplash.com/photo-1506869640319-fe1a24fd07dc?w=150&q=80')] bg-cover"></div>
          <div className="w-16 h-16 rounded-lg bg-slate-200 bg-[url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=150&q=80')] bg-cover"></div>
          <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center border border-slate-200">
            <ImageIcon className="w-6 h-6 text-slate-400" />
          </div>
        </div>
      )
    },
  ];

  return (
    <div ref={containerRef} className="min-h-screen relative flex flex-col items-center justify-start pb-32">
      <AnimatePresence>
        {isNavigating && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none bg-amber-950/20 backdrop-blur-2xl overflow-hidden"
            transition={{ duration: 0.5 }}
          >
            {/* Drifting Motes */}
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2, duration: 1 }}
              className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(251,191,36,0.15)_0%,_transparent_70%)]"
            >
              {Array.from({ length: 20 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ 
                    x: `${Math.random() * 100}vw`, 
                    y: `${Math.random() * 100}vh`, 
                    opacity: 0, 
                    scale: Math.random() * 0.5 + 0.5 
                  }}
                  animate={{ 
                    y: [`${Math.random() * 100}vh`, `${Math.random() * 100 - 20}vh`],
                    opacity: [0, 0.6, 0]
                  }}
                  transition={{ 
                    duration: Math.random() * 3 + 2, 
                    repeat: Infinity, 
                    delay: Math.random() * 2,
                    ease: "linear" 
                  }}
                  className="absolute w-2 h-2 rounded-full bg-amber-200 blur-[2px]"
                />
              ))}
            </motion.div>

            {/* Peripheral Ripples */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: [0.8, 1.5, 2], opacity: [0, 0.3, 0] }}
              transition={{ delay: 0.7, duration: 2, ease: "easeOut" }}
              className="absolute w-[80vw] h-[80vw] rounded-full border border-teal-500/20 mix-blend-screen"
            />
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: [0.8, 1.2, 1.8], opacity: [0, 0.4, 0] }}
              transition={{ delay: 0.9, duration: 2, ease: "easeOut" }}
              className="absolute w-[60vw] h-[60vw] rounded-full border border-amber-500/20 mix-blend-screen"
            />

            {/* SVG Converging Light-Hands (The Kinship Handshake) */}
            <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="xMidYMid slice">
              <defs>
                <linearGradient id="goldGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="transparent" />
                  <stop offset="60%" stopColor="#fde047" />
                  <stop offset="100%" stopColor="#fffbeb" />
                </linearGradient>
                <linearGradient id="sageGlow" x1="100%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="transparent" />
                  <stop offset="60%" stopColor="#6ee7b7" />
                  <stop offset="100%" stopColor="#ecfdf5" />
                </linearGradient>
                <linearGradient id="goldGlowBottom" x1="100%" y1="100%" x2="0%" y2="0%">
                  <stop offset="0%" stopColor="transparent" />
                  <stop offset="60%" stopColor="#fde047" />
                  <stop offset="100%" stopColor="#fffbeb" />
                </linearGradient>
                <linearGradient id="sageGlowBottom" x1="0%" y1="100%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="transparent" />
                  <stop offset="60%" stopColor="#6ee7b7" />
                  <stop offset="100%" stopColor="#ecfdf5" />
                </linearGradient>
                <filter id="etherealGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="4" result="blur1" />
                  <feGaussianBlur stdDeviation="12" result="blur2" />
                  <feMerge>
                    <feMergeNode in="blur2" />
                    <feMergeNode in="blur1" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <g filter="url(#etherealGlow)">
                {/* TOP LEFT HAND (Gold) */}
                <motion.g 
                  initial={{ x: -100, y: -100, opacity: 0 }}
                  animate={{ x: 0, y: 0, opacity: 1 }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                >
                  <path d="M 20%,10% Q 35%,30% 45%,42% Q 48%,46% 50%,47%" fill="none" stroke="url(#goldGlow)" strokeWidth="3" strokeLinecap="round" />
                  <path d="M 15%,15% Q 30%,35% 42%,45% Q 46%,48% 49%,49%" fill="none" stroke="url(#goldGlow)" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
                  <path d="M 25%,5%  Q 40%,25% 47%,40% Q 49%,45% 51%,46%" fill="none" stroke="url(#goldGlow)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
                  {/* Fingers */}
                  <path d="M 45%,42% Q 48%,46% 50%,47% Q 51%,47% 52%,49%" fill="none" stroke="url(#goldGlow)" strokeWidth="2" strokeLinecap="round" />
                  <path d="M 42%,45% Q 46%,48% 49%,49% Q 51%,50% 51%,52%" fill="none" stroke="url(#goldGlow)" strokeWidth="1.5" strokeLinecap="round" />
                </motion.g>

                {/* BOTTOM RIGHT HAND (Gold) */}
                <motion.g 
                  initial={{ x: 100, y: 100, opacity: 0 }}
                  animate={{ x: 0, y: 0, opacity: 1 }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                >
                  <path d="M 80%,90% Q 65%,70% 55%,58% Q 52%,54% 50%,53%" fill="none" stroke="url(#goldGlowBottom)" strokeWidth="3" strokeLinecap="round" />
                  <path d="M 85%,85% Q 70%,65% 58%,55% Q 54%,52% 51%,51%" fill="none" stroke="url(#goldGlowBottom)" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
                  <path d="M 75%,95% Q 60%,75% 53%,60% Q 51%,55% 49%,54%" fill="none" stroke="url(#goldGlowBottom)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
                  {/* Fingers */}
                  <path d="M 55%,58% Q 52%,54% 50%,53% Q 49%,53% 48%,51%" fill="none" stroke="url(#goldGlowBottom)" strokeWidth="2" strokeLinecap="round" />
                  <path d="M 58%,55% Q 54%,52% 51%,51% Q 49%,50% 49%,48%" fill="none" stroke="url(#goldGlowBottom)" strokeWidth="1.5" strokeLinecap="round" />
                </motion.g>

                {/* TOP RIGHT HAND (Sage) */}
                <motion.g 
                  initial={{ x: 100, y: -100, opacity: 0 }}
                  animate={{ x: 0, y: 0, opacity: 1 }}
                  transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
                >
                  <path d="M 80%,10% Q 65%,30% 55%,42% Q 52%,46% 50%,47%" fill="none" stroke="url(#sageGlow)" strokeWidth="3" strokeLinecap="round" />
                  <path d="M 85%,15% Q 70%,35% 58%,45% Q 54%,48% 51%,49%" fill="none" stroke="url(#sageGlow)" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
                  <path d="M 75%,5%  Q 60%,25% 53%,40% Q 51%,45% 49%,46%" fill="none" stroke="url(#sageGlow)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
                  {/* Fingers */}
                  <path d="M 55%,42% Q 52%,46% 50%,47% Q 49%,47% 48%,49%" fill="none" stroke="url(#sageGlow)" strokeWidth="2" strokeLinecap="round" />
                  <path d="M 58%,45% Q 54%,48% 51%,49% Q 49%,50% 49%,52%" fill="none" stroke="url(#sageGlow)" strokeWidth="1.5" strokeLinecap="round" />
                </motion.g>

                {/* BOTTOM LEFT HAND (Sage) */}
                <motion.g 
                  initial={{ x: -100, y: 100, opacity: 0 }}
                  animate={{ x: 0, y: 0, opacity: 1 }}
                  transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
                >
                  <path d="M 20%,90% Q 35%,70% 45%,58% Q 48%,54% 50%,53%" fill="none" stroke="url(#sageGlowBottom)" strokeWidth="3" strokeLinecap="round" />
                  <path d="M 15%,85% Q 30%,65% 42%,55% Q 46%,52% 49%,51%" fill="none" stroke="url(#sageGlowBottom)" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
                  <path d="M 25%,95% Q 40%,75% 47%,60% Q 49%,55% 51%,54%" fill="none" stroke="url(#sageGlowBottom)" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
                  {/* Fingers */}
                  <path d="M 45%,58% Q 48%,54% 50%,53% Q 51%,53% 52%,51%" fill="none" stroke="url(#sageGlowBottom)" strokeWidth="2" strokeLinecap="round" />
                  <path d="M 42%,55% Q 46%,52% 49%,51% Q 51%,50% 51%,48%" fill="none" stroke="url(#sageGlowBottom)" strokeWidth="1.5" strokeLinecap="round" />
                </motion.g>
              </g>

              {/* Relationship Motes and Nest Embrace */}
              <g>
                <motion.circle cx="50%" cy="50%" r="55" fill="none" stroke="#fde047" strokeWidth="2" strokeDasharray="1 10" strokeLinecap="round"
                  initial={{ scale: 0.5, opacity: 0, rotate: -45 }}
                  animate={{ scale: 1, opacity: 0.8, rotate: 135 }}
                  transition={{ delay: 0.7, duration: 1.5, ease: "backOut" }}
                />
                <motion.circle cx="50%" cy="50%" r="75" fill="none" stroke="#6ee7b7" strokeWidth="1.5" strokeDasharray="3 15" strokeLinecap="round"
                  initial={{ scale: 0.5, opacity: 0, rotate: 45 }}
                  animate={{ scale: 1, opacity: 0.5, rotate: -90 }}
                  transition={{ delay: 0.8, duration: 1.5, ease: "backOut" }}
                />
                
                {/* The "Nest" Embrace Rings */}
                <motion.ellipse cx="50%" cy="50%" rx="90" ry="110" fill="none" stroke="url(#goldGlow)" strokeWidth="1" opacity="0.4"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 0.4 }}
                  transition={{ delay: 0.9, duration: 1 }}
                />
                <motion.ellipse cx="50%" cy="50%" rx="110" ry="90" fill="none" stroke="url(#sageGlow)" strokeWidth="1" opacity="0.4"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 0.4 }}
                  transition={{ delay: 1.0, duration: 1 }}
                />
              </g>
            </svg>
            
            {/* The Clasp Burst */}
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ 
                scale: [0, 2.5, 1.5], 
                opacity: [0, 1, 0]
              }}
              transition={{ delay: 0.7, duration: 0.8, ease: "easeOut" }}
              className="absolute w-32 h-32 flex items-center justify-center pointer-events-none"
            >
              {/* Brilliant Central Core */}
              <div className="w-10 h-10 bg-white rounded-full shadow-[0_0_80px_40px_rgba(253,224,71,1)] mix-blend-screen"></div>
              {/* Diffuse aura */}
              <div className="absolute inset-0 bg-gradient-to-tr from-amber-200/50 to-emerald-200/50 rounded-full blur-2xl"></div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero Section - Perfectly Centered Full Viewport Height block */}
      <div className="relative z-20 flex flex-col items-center justify-center min-h-[90vh] text-center px-6 max-w-5xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="flex flex-col items-center justify-center"
        >
          {/* 'Introducing' Badge */}
          <div className="inline-flex items-center px-5 py-2 rounded-full bg-white/50 backdrop-blur-md border border-amber-300 shadow-[0_0_15px_rgba(251,191,36,0.3)] text-sm font-semibold text-amber-800 mb-8">
            ✨ Introducing the Future of Family Management
          </div>
          
          {/* Main Title with Stylized Nest Integration */}
          <div className="relative flex items-center justify-center mb-2">
            <h1 className="text-6xl md:text-[5.5rem] font-bold tracking-tight text-slate-800 font-serif text-glow-gold">
              <span className="relative inline-block">
                {/* Stylized Golden Nest SVG wrapping K and i */}
                <svg className="absolute -inset-4 w-[140%] h-[140%] -z-10 opacity-80" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
                  <motion.path 
                    d="M10,60 Q30,80 50,75 T90,50 Q70,90 40,95 T10,60" 
                    fill="none" stroke="url(#goldGradient)" strokeWidth="3" strokeLinecap="round" 
                    initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, ease: "easeInOut" }}
                  />
                  <motion.path 
                    d="M20,50 Q40,30 60,40 T80,70 Q50,30 20,50" 
                    fill="none" stroke="url(#goldGradient)" strokeWidth="2" strokeLinecap="round" opacity="0.6"
                    initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 0.5, ease: "easeInOut" }}
                  />
                  <defs>
                    <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#f59e0b" />
                      <stop offset="50%" stopColor="#fbbf24" />
                      <stop offset="100%" stopColor="#d97706" />
                    </linearGradient>
                  </defs>
                </svg>
                <span className="text-amber-500 font-extrabold italic" style={{ WebkitTextStroke: '1px #d97706' }}>Ki</span>
              </span>
              nNest
            </h1>
          </div>

          {/* Catchy Sub-title */}
          <h2 className="text-3xl md:text-5xl font-semibold mb-6 tracking-tight text-slate-700 font-serif leading-tight">
            The Private Digital Hearth <br className="hidden md:block"/> 
            <span className="text-amber-700 drop-shadow-[0_2px_10px_rgba(180,83,9,0.3)]">for Your Home</span>
          </h2>
          
          {/* Description */}
          <p className="text-lg md:text-xl text-slate-700 font-medium max-w-3xl mx-auto mb-10 leading-relaxed font-sans">
            Where specialized family agents coordinate schedules, health, finances, and overarching family goals.
          </p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6"
        >
          <div onClick={handleLaunch}>
            <motion.button 
              animate={buttonPulse ? { scale: [1, 0.95, 1.05, 1] } : {}}
              transition={{ duration: 0.3 }}
              whileHover={!buttonPulse ? { scale: 1.03 } : {}}
              whileTap={!buttonPulse ? { scale: 0.97 } : {}}
              className="group relative px-8 py-4 bg-white/80 backdrop-blur-xl text-slate-800 rounded-full font-bold transition-all shadow-[0_10px_40px_-10px_rgba(217,119,6,0.3)] hover:shadow-[0_10px_50px_-10px_rgba(217,119,6,0.5)] flex items-center"
            >
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-emerald-200 to-amber-200 opacity-0 group-hover:opacity-100 transition-opacity -z-10 blur-md"></div>
              <div className="absolute inset-0 rounded-full border border-transparent bg-gradient-to-r from-emerald-400 to-amber-400 opacity-50 [mask-composite:exclude] [mask-image:linear-gradient(#fff_0_0),linear-gradient(#fff_0_0)] p-[1.5px] -z-10"></div>
              Launch Family Hub
              <ChevronRight className="w-5 h-5 ml-2 text-amber-600 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </div>
          <motion.button 
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="px-8 py-4 bg-white/40 backdrop-blur-sm text-slate-700 rounded-full font-bold transition-all border border-slate-300 hover:border-amber-400 hover:bg-white/80"
          >
            Explore Agents
          </motion.button>
        </motion.div>
      </div>

      {/* Animated Agent Grid */}
      <motion.div 
        variants={{
          hidden: { opacity: 0 },
          visible: { 
            opacity: 1,
            transition: { staggerChildren: 0.12 }
          }
        }}
        initial="hidden"
        animate="visible"
        className="relative z-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-6 max-w-6xl mx-auto w-full mb-32"
      >
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </motion.div>

      {/* Live Collaboration Stream Marquee */}
      <div className="fixed bottom-0 left-0 right-0 h-14 bg-white/80 backdrop-blur-xl border-t border-amber-100/50 flex items-center z-30 shadow-[0_-10px_30px_rgba(0,0,0,0.02)]">
        <div className="absolute left-0 w-24 h-full bg-gradient-to-r from-white to-transparent z-10"></div>
        <div className="absolute right-0 w-24 h-full bg-gradient-to-l from-white to-transparent z-10"></div>
        
        <motion.div 
          animate={{ x: [0, -1000] }}
          transition={{ ease: "linear", duration: 25, repeat: Infinity }}
          className="flex whitespace-nowrap items-center text-sm font-semibold text-slate-700"
        >
          {Array(4).fill(null).map((_, i) => (
            <div key={i} className="flex items-center">
              <span className="mx-8 flex items-center"><span className="text-pink-500 mr-2">✨</span> Mother Agent added organic milk to shopping list</span>
              <span className="mx-8 text-amber-300">•</span>
              <span className="mx-8 flex items-center"><span className="text-indigo-500 mr-2">🗓️</span> Life Planner Agent reserved dinner for 4</span>
              <span className="mx-8 text-amber-300">•</span>
              <span className="mx-8 flex items-center"><span className="text-emerald-500 mr-2">👴</span> Grandparent Agent completed morning walk goal</span>
              <span className="mx-8 text-amber-300">•</span>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}