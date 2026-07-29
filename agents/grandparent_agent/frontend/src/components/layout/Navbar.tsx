import React, { useState, useEffect } from 'react';
import { Menu, Bell, AlertTriangle } from 'lucide-react';
import { emergencyService } from '../../services/emergencyService';
import toast from 'react-hot-toast';

interface NavbarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  title: string;
}

export const Navbar: React.FC<NavbarProps> = ({ sidebarOpen, setSidebarOpen, title }) => {
  const [triggering, setTriggering] = useState(false);

  const handleSOS = async () => {
    setTriggering(true);
    try {
      const res = await emergencyService.triggerSOS();
      toast.error(`ALERT SENT! Emergency SOS has been sent to: ${res.contact_notified}`, {
        duration: 8000,
        position: 'top-center',
        style: {
          border: '2px solid #e11d48',
          padding: '16px',
          color: '#9f1239',
          fontSize: '18px',
          fontWeight: 'bold',
          background: '#fff1f2'
        }
      });
    } catch (e) {
      toast.error("Failed to trigger SOS online, activating offline emergency trigger.");
    } finally {
      setTriggering(false);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-20 w-full items-center justify-between border-b border-sky-100 bg-white/90 px-6 backdrop-blur-md">
      {/* Left title and toggle */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="rounded-xl p-2 hover:bg-slate-50 text-slate-600 md:hidden border border-slate-200 transition-colors"
          aria-label="Toggle Navigation"
        >
          <Menu className="h-6 w-6" />
        </button>
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 tracking-tight">{title}</h2>
        </div>
      </div>

      {/* Right side controls */}
      <div className="flex items-center gap-4">
        {/* Large SOS Emergency Alert Button */}
        <button
          onClick={handleSOS}
          disabled={triggering}
          className="flex items-center gap-2 rounded-2xl bg-rose-600 hover:bg-rose-700 active:scale-95 text-white px-5 py-2.5 font-bold text-base shadow-lg shadow-rose-200 transition-all border border-rose-500 animate-pulse"
        >
          <AlertTriangle className="h-5 w-5" />
          <span>{triggering ? 'Sending...' : 'EMERGENCY SOS'}</span>
        </button>

        {/* Notifications Bell */}
        <button className="relative rounded-xl p-2.5 hover:bg-slate-50 border border-slate-100 text-slate-500 hover:text-slate-800 transition-colors">
          <Bell className="h-6 w-6" />
          <span className="absolute top-1.5 right-1.5 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white animate-pulse" />
        </button>
      </div>
    </header>
  );
};
export default Navbar;
