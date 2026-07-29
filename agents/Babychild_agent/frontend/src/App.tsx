import { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import BabyProfile from './pages/BabyProfile';
import Feeding from './pages/Feeding';
import Sleep from './pages/Sleep';
import Diapers from './pages/Diapers';
import Growth from './pages/Growth';
import Vaccinations from './pages/Vaccinations';
import HealthLogs from './pages/HealthLogs';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import './App.css';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = (pathname: string) => {
    switch (pathname) {
      case '/':            return 'Dashboard';
      case '/ai':          return 'AI Assistant';
      case '/profile':     return 'Baby Profile';
      case '/feeding':     return 'Feeding';
      case '/sleep':       return 'Sleep';
      case '/diapers':     return 'Diapers';
      case '/growth':      return 'Growth';
      case '/vaccinations':return 'Vaccinations';
      case '/health-logs': return 'Health Logs';
      case '/alerts':      return 'Alerts';
      case '/settings':    return 'Settings';
      default:             return 'KinNest';
    }
  };

  // AI Assistant page needs full-height, no padding
  const isAI = location.pathname === '/ai';

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          title={getPageTitle(location.pathname)}
        />

        <main className={`flex-1 overflow-y-auto ${isAI ? '' : 'px-6 py-6 md:px-8'}`}>
          <div className={isAI ? 'h-full' : 'mx-auto max-w-7xl'}>
            <Routes>
              <Route path="/"            element={<Dashboard />}    />
              <Route path="/ai"          element={<AIAssistant />}  />
              <Route path="/profile"     element={<BabyProfile />}  />
              <Route path="/feeding"     element={<Feeding />}      />
              <Route path="/sleep"       element={<Sleep />}        />
              <Route path="/diapers"     element={<Diapers />}      />
              <Route path="/growth"      element={<Growth />}       />
              <Route path="/vaccinations" element={<Vaccinations />} />
              <Route path="/health-logs" element={<HealthLogs />}   />
              <Route path="/alerts"      element={<Alerts />}       />
              <Route path="/settings"    element={<Settings />}     />
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
    </BrowserRouter>
  );
}
