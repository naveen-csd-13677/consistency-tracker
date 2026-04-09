const API_BASE = process.env.REACT_APP_API_URL || '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (res.status === 204) return null;
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return res.json();
}

// Goals
export const getGoals = (status) => request(`/goals/${status ? `?status=${status}` : ''}`);
export const createGoal = (data) => request('/goals/', { method: 'POST', body: JSON.stringify(data) });
export const getGoal = (id) => request(`/goals/${id}`);
export const updateGoal = (id, data) => request(`/goals/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteGoal = (id) => request(`/goals/${id}`, { method: 'DELETE' });

// Duties
export const getDuties = (goalId) => request(`/duties/${goalId ? `?goal_id=${goalId}` : ''}`);
export const createDuty = (data) => request('/duties/', { method: 'POST', body: JSON.stringify(data) });
export const updateDuty = (id, data) => request(`/duties/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteDuty = (id) => request(`/duties/${id}`, { method: 'DELETE' });

// Daily Logs
export const getLogs = (params) => {
  const query = new URLSearchParams();
  if (params?.date) query.set('date', params.date);
  if (params?.goal_id) query.set('goal_id', params.goal_id);
  const qs = query.toString();
  return request(`/logs/${qs ? `?${qs}` : ''}`);
};
export const upsertLog = (data) => request('/logs/', { method: 'POST', body: JSON.stringify(data) });
export const getDailyOverview = (date) => request(`/logs/overview?date=${date}`);

// Analytics
export const getWeeklyAnalytics = (params) => {
  const query = new URLSearchParams();
  if (params?.week) query.set('week', params.week);
  if (params?.goal_id) query.set('goal_id', params.goal_id);
  return request(`/analytics/weekly?${query.toString()}`);
};
export const getMonthlyAnalytics = (params) => {
  const query = new URLSearchParams();
  if (params?.month) query.set('month', params.month);
  if (params?.goal_id) query.set('goal_id', params.goal_id);
  return request(`/analytics/monthly?${query.toString()}`);
};

// Upgrades
export const getUpgrades = (goalId) => request(`/upgrades/${goalId ? `?goal_id=${goalId}` : ''}`);
export const createUpgrade = (data) => request('/upgrades/', { method: 'POST', body: JSON.stringify(data) });
export const getUpgradeReadiness = () => request('/upgrades/readiness');

// Suggestions
export const getSuggestions = () => request('/suggestions/');
export const getSuggestion = (goalId) => request(`/suggestions/${goalId}`);
export const generateSuggestions = () => request('/suggestions/generate', { method: 'POST' });

// Config
export const getConfig = () => request('/config/');
export const updateConfig = (data) => request('/config/', { method: 'PUT', body: JSON.stringify(data) });

// Dashboard
export const getDashboard = () => request('/dashboard/');

// Export
export const exportData = (format) => `${API_BASE}/export/?format=${format}`;
