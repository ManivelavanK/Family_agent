import { useEffect } from 'react';
import { motion, useTransform, useSpring } from 'framer-motion';

export default function BackgroundCanvas() {
  const mouseX = useSpring(0, { stiffness: 50, damping: 20 });
  const mouseY = useSpring(0, { stiffness: 50, damping: 20 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) - 0.5;
      const y = (e.clientY / window.innerHeight) - 0.5;
      mouseX.set(x * 100);
      mouseY.set(y * 100);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Blurred Photo Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-20 mix-blend-overlay blur-sm"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=2000&q=80')" }}
      />
      {/* Ethereal Glow Orbs */}
      <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-amber-400/20 rounded-full blur-[100px] mix-blend-multiply animate-pulse" style={{ animationDuration: '8s' }}></div>
      <div className="absolute top-1/2 right-1/4 translate-x-1/2 -translate-y-1/2 w-[30rem] h-[30rem] bg-emerald-400/10 rounded-full blur-[120px] mix-blend-multiply animate-pulse" style={{ animationDuration: '12s' }}></div>
      <div className="absolute bottom-1/4 left-1/2 -translate-x-1/2 w-80 h-80 bg-amber-500/15 rounded-full blur-[100px] mix-blend-multiply"></div>
      
      {/* Kinship Particle Network */}
      <motion.svg 
        className="absolute inset-0 w-full h-full opacity-60" 
        style={{ x: useTransform(mouseX, v => v * 0.2), y: useTransform(mouseY, v => v * 0.2) }}
      >
        {/* Subtle Connective Lines (Deep Ochre) */}
        <g stroke="#92400e" strokeWidth="0.75" opacity="0.3" strokeLinecap="round" strokeLinejoin="round">
          <motion.polyline points="10%,20% 30%,35% 20%,60% 40%,80% 60%,65% 50%,40% 70%,25% 85%,45% 75%,75%" fill="none" animate={{ opacity: [0.1, 0.4, 0.1] }} transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }} />
          <motion.line x1="30%" y1="35%" x2="50%" y2="40%" fill="none" animate={{ opacity: [0.1, 0.5, 0.1] }} transition={{ duration: 12, repeat: Infinity, delay: 2, ease: "easeInOut" }} />
          <motion.line x1="60%" y1="65%" x2="85%" y2="45%" fill="none" animate={{ opacity: [0.1, 0.5, 0.1] }} transition={{ duration: 14, repeat: Infinity, delay: 5, ease: "easeInOut" }} />
          <motion.line x1="20%" y1="60%" x2="50%" y2="40%" fill="none" animate={{ opacity: [0.1, 0.5, 0.1] }} transition={{ duration: 13, repeat: Infinity, delay: 1, ease: "easeInOut" }} />
        </g>
        
        {/* Soft-Glowing Nodes */}
        <g>
          {/* Amber Nodes */}
          <circle cx="10%" cy="20%" r="2" fill="#fbbf24" opacity="0.7" className="animate-pulse" />
          <circle cx="30%" cy="35%" r="3.5" fill="#fbbf24" opacity="0.9" className="animate-pulse" style={{ animationDelay: '1s', filter: 'drop-shadow(0 0 4px rgba(251,191,36,0.6))' }} />
          <circle cx="60%" cy="65%" r="2.5" fill="#fbbf24" opacity="0.6" className="animate-pulse" style={{ animationDelay: '3s' }} />
          <circle cx="85%" cy="45%" r="2" fill="#fbbf24" opacity="0.8" className="animate-pulse" style={{ animationDelay: '2s' }} />
          
          {/* Light Green Nodes */}
          <circle cx="20%" cy="60%" r="2.5" fill="#a7f3d0" opacity="0.7" className="animate-pulse" style={{ animationDelay: '0.5s' }} />
          <circle cx="40%" cy="80%" r="2" fill="#a7f3d0" opacity="0.6" className="animate-pulse" style={{ animationDelay: '1.5s' }} />
          <circle cx="50%" cy="40%" r="3.5" fill="#a7f3d0" opacity="0.9" className="animate-pulse" style={{ animationDelay: '2.5s', filter: 'drop-shadow(0 0 4px rgba(167,243,208,0.6))' }} />
          <circle cx="70%" cy="25%" r="2" fill="#a7f3d0" opacity="0.7" className="animate-pulse" style={{ animationDelay: '4s' }} />
          <circle cx="75%" cy="75%" r="2.5" fill="#a7f3d0" opacity="0.8" className="animate-pulse" style={{ animationDelay: '0.8s' }} />
        </g>
      </motion.svg>
    </div>
  );
}
