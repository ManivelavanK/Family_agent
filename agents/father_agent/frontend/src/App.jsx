import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { FamilyProvider } from './context/FamilyContext';

import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import Income from './pages/Income';
import Budget from './pages/Budget';
import Savings from './pages/Savings';
import Bills from './pages/Bills';
import Analytics from './pages/Analytics';
import Predictions from './pages/Predictions';
import Anomalies from './pages/Anomalies';
import SafeToSpend from './pages/SafeToSpend';
import DigitalTwin from './pages/DigitalTwin';
import AIAdvisor from './pages/AIAdvisor';
import EarlyWarnings from './pages/EarlyWarnings';
import Notifications from './pages/Notifications';
import FinancialMemory from './pages/FinancialMemory';
import FamilyIntelligence from './pages/FamilyIntelligence';
import Settings from './pages/Settings';

import AskBeforeSpend from './pages/AskBeforeSpend';
import DecisionCenter from './pages/DecisionCenter';
import AIVerification from './pages/AIVerification';

export function App() {
  return (
    <FamilyProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="expenses" element={<Expenses />} />
            <Route path="income" element={<Income />} />
            <Route path="budget" element={<Budget />} />
            <Route path="savings" element={<Savings />} />
            <Route path="bills" element={<Bills />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="predictions" element={<Predictions />} />
            <Route path="anomalies" element={<Anomalies />} />
            <Route path="safe-to-spend" element={<SafeToSpend />} />
            <Route path="digital-twin" element={<DigitalTwin />} />
            <Route path="ai-advisor" element={<AIAdvisor />} />
            <Route path="ask-before-spend" element={<AskBeforeSpend />} />
            <Route path="decision-center" element={<DecisionCenter />} />
            <Route path="ai-verification" element={<AIVerification />} />
            <Route path="early-warnings" element={<EarlyWarnings />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="memory" element={<FinancialMemory />} />
            <Route path="family-intelligence" element={<FamilyIntelligence />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </FamilyProvider>
  );
}

export default App;
