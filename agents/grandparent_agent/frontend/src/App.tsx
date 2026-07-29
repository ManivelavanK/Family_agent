import { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';

// Page imports
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Vitals from './pages/Vitals';
import Medicine from './pages/Medicine';
import Activity from './pages/Activity';
import Nutrition from './pages/Nutrition';
import Appointments from './pages/Appointments';
import Insurance from './pages/Insurance';
import Memory from './pages/Memory';
import Recommendation from './pages/Recommendation';
import Reminder from './pages/Reminder';
import Forecast from './pages/Forecast';
import Emergency from './pages/Emergency';
import Voice from './pages/Voice';
import Notifications from './pages/Notifications';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = (pathname: string): string => {
    const titles: Record<string, string> = {
      '/': 'Health Dashboard',
      '/profile': 'Personal Profile',
      '/vitals': 'Health Vitals',
      '/medicine': 'Medicine Management',
      '/activity': 'Physical Activity',
      '/nutrition': 'Nutrition & Meals',
      '/appointments': 'Doctor Appointments',
      '/insurance': 'Health Insurance',
      '/memory': 'Memory Care',
      '/recommendations': 'AI Health Recommendations',
      '/reminders': 'Daily Reminders',
      '/forecast': 'Health Forecast',
      '/emergency': 'Emergency SOS',
      '/voice': 'Voice Assistant',
      '/whatsapp': 'WhatsApp Notifications',
      '/analytics': 'Health Analytics',
      '/settings': 'Settings',
    };
    return titles[pathname] || 'KinNest';
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Sticky Top Navbar */}
        <Navbar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          title={getPageTitle(location.pathname)}
        />

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto px-5 py-6 md:px-8">
          <div className="mx-auto max-w-7xl">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/vitals" element={<Vitals />} />
              <Route path="/medicine" element={<Medicine />} />
              <Route path="/activity" element={<Activity />} />
              <Route path="/nutrition" element={<Nutrition />} />
              <Route path="/appointments" element={<Appointments />} />
              <Route path="/insurance" element={<Insurance />} />
              <Route path="/memory" element={<Memory />} />
              <Route path="/recommendations" element={<Recommendation />} />
              <Route path="/reminders" element={<Reminder />} />
              <Route path="/forecast" element={<Forecast />} />
              <Route path="/emergency" element={<Emergency />} />
              <Route path="/voice" element={<Voice />} />
              <Route path="/whatsapp" element={<Notifications />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            fontFamily: 'Outfit, sans-serif',
            fontSize: '16px',
            fontWeight: '600',
            borderRadius: '14px',
            padding: '14px 18px',
          },
          success: {
            style: {
              border: '1px solid #bbf7d0',
              background: '#f0fdf4',
              color: '#166534',
            },
          },
          error: {
            style: {
              border: '1px solid #fecaca',
              background: '#fef2f2',
              color: '#991b1b',
            },
          },
        }}
      />
    </BrowserRouter>
  );
}
