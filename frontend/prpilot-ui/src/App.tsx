import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { RepositoriesPage } from './pages/RepositoriesPage';
import { PullRequestsPage } from './pages/PullRequestsPage';
import { AnalysesPage } from './pages/AnalysesPage';
import { IntelligencePage } from './pages/IntelligencePage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="repositories" element={<RepositoriesPage />} />
          <Route path="pull-requests" element={<PullRequestsPage />} />
          <Route path="analyses" element={<AnalysesPage />} />
          <Route path="intelligence" element={<IntelligencePage />} />
          {/* Catch-all → dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
