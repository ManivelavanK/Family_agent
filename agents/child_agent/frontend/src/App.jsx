import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import MainLayout from './layouts/MainLayout';

// Pages
import Dashboard    from './pages/Dashboard';
import StudyHub     from './pages/StudyHub';
import AIPlanner    from './pages/AIPlanner';
import Assignments  from './pages/Assignments';
import Goals        from './pages/Goals';
import Exams        from './pages/Exams';
import Progress     from './pages/Progress';
import AITutor      from './pages/AITutor';
import AICompanion  from './pages/AICompanion';
import FocusHabits  from './pages/FocusHabits';
import LearningPath from './pages/LearningPath';
import Profile      from './pages/Profile';
import Notifications from './pages/Notifications';

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Routes>
          <Route element={<MainLayout />}>
            <Route index              element={<Dashboard    />} />
            <Route path="study-hub"   element={<StudyHub     />} />
            <Route path="ai-planner"  element={<AIPlanner    />} />
            <Route path="assignments" element={<Assignments  />} />
            <Route path="goals"       element={<Goals        />} />
            <Route path="exams"       element={<Exams        />} />
            <Route path="progress"    element={<Progress     />} />
            <Route path="ai-tutor"    element={<AITutor      />} />
            <Route path="ai-companion"element={<AICompanion  />} />
            <Route path="focus-habits"element={<FocusHabits  />} />
            <Route path="learning-path"element={<LearningPath/>} />
            <Route path="profile"     element={<Profile      />} />
            <Route path="notifications"element={<Notifications/>}/>
            <Route path="*"           element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
