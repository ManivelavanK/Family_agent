import { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import Inventory from './pages/Inventory';
import ShoppingList from './pages/ShoppingList';
import MealPlanner from './pages/MealPlanner';
import Purchases from './pages/Purchases';
import Insights from './pages/Insights';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import './App.css';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Helper to map route path to friendly title
  const getPageTitle = (pathname: string) => {
    switch (pathname) {
      case '/': return 'Dashboard';
      case '/ai': return 'AI Assistant';
      case '/inventory': return 'Inventory & Pantry';
      case '/shopping': return 'Smart Shopping List';
      case '/meal': return 'Meal Planner';
      case '/purchases': return 'Purchase History';
      case '/insights': return 'Insights & Spending';
      case '/alerts': return 'Proactive Alerts';
      case '/settings': return 'Settings';
      default: return 'KinNest';
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      {/* Sidebar navigation */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      {/* Main content wrapper */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Navbar */}
        <Navbar 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen} 
          title={getPageTitle(location.pathname)} 
        />

        {/* Scrollable page body */}
        <main className="flex-1 overflow-y-auto px-6 py-6 md:px-8">
          <div className="mx-auto max-w-7xl">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/ai" element={<AIAssistant />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/shopping" element={<ShoppingList />} />
              <Route path="/meal" element={<MealPlanner />} />
              <Route path="/purchases" element={<Purchases />} />
              <Route path="/insights" element={<Insights />} />
              <Route path="/alerts" element={<Alerts />} />
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
    </BrowserRouter>
  );
}
