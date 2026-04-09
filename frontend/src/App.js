import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DailyLog from './pages/DailyLog';
import Goals from './pages/Goals';
import WeeklyAnalytics from './pages/WeeklyAnalytics';
import MonthlyGrowth from './pages/MonthlyGrowth';
import UpgradeHistory from './pages/UpgradeHistory';
import ProgressionInsights from './pages/ProgressionInsights';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/log" element={<DailyLog />} />
          <Route path="/goals" element={<Goals />} />
          <Route path="/analytics/weekly" element={<WeeklyAnalytics />} />
          <Route path="/analytics/monthly" element={<MonthlyGrowth />} />
          <Route path="/upgrades" element={<UpgradeHistory />} />
          <Route path="/insights" element={<ProgressionInsights />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
