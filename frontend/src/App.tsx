import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import FatherAgent from './pages/FatherAgent';
import MotherAgent from './pages/MotherAgent';
import ChildrenAgent from './pages/ChildrenAgent';
import GrandparentAgent from './pages/GrandparentAgent';
import BabyAgent from './pages/BabyAgent';
import PlannerAgent from './pages/PlannerAgent';
import Orchestrator from './pages/Orchestrator';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';
import WorkspaceFlow from './pages/WorkspaceFlow';
import Layout from './components/layout/Layout';
import BackgroundCanvas from './components/BackgroundCanvas';

function App() {
  return (
    <>
      <BackgroundCanvas />
      <Router>
        <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/workspace/*" element={<WorkspaceFlow />} />
        
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/father" element={<FatherAgent />} />
          <Route path="/mother" element={<MotherAgent />} />
          <Route path="/children" element={<ChildrenAgent />} />
          <Route path="/grandparent" element={<GrandparentAgent />} />
          <Route path="/baby" element={<BabyAgent />} />
          <Route path="/planner" element={<PlannerAgent />} />
          <Route path="/orchestrator" element={<Orchestrator />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
    </>
  );
}

export default App;
