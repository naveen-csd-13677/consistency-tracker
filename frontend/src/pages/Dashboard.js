import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getDashboard } from '../api';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="text-lg text-gray-500">Loading dashboard...</div></div>;
  if (!data) return <div className="text-center py-12 text-gray-500">No data available. Start by adding goals!</div>;

  const statusData = [
    { name: 'Completed', value: data.goals_performance?.filter(g => g.weekly_consistency_pct >= 90).length || 0 },
    { name: 'Needs Attention', value: data.goals_performance?.filter(g => g.weekly_consistency_pct >= 70 && g.weekly_consistency_pct < 90).length || 0 },
    { name: 'Struggling', value: data.goals_performance?.filter(g => g.weekly_consistency_pct < 70).length || 0 },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Motivation */}
      {data.motivation && (
        <div className="card bg-gradient-to-r from-indigo-500 to-purple-600 text-white border-0">
          <p className="text-lg font-medium">💬 {data.motivation}</p>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{data.overall_consistency_pct}%</div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Overall Consistency</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 dark:text-green-400">{data.perfect_days}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Perfect Days</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">{data.goals_performance?.length || 0}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Active Goals</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Last 4 Weeks Trend */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">📈 Last 4 Weeks Trend</h2>
          {data.weekly_trend?.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data.weekly_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="week" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="consistency_pct" stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} name="Consistency %" />
              </LineChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-500 text-center py-8">No trend data yet</p>}
        </div>

        {/* Goal Status Distribution */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">📊 Goal Status Distribution</h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-500 text-center py-8">No goals yet</p>}
        </div>
      </div>

      {/* Goals Performance */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">🎯 Current Goals Performance</h2>
        {data.goals_performance?.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b dark:border-gray-600">
                    <th className="text-left py-2 px-3">Goal</th>
                    <th className="text-left py-2 px-3">Duty</th>
                    <th className="text-right py-2 px-3">Weekly %</th>
                    <th className="text-center py-2 px-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.goals_performance.map(g => (
                    <tr key={g.goal_id} className="border-b dark:border-gray-700">
                      <td className="py-2 px-3 font-medium">{g.goal_name}</td>
                      <td className="py-2 px-3 text-gray-600 dark:text-gray-400">{g.current_duty}</td>
                      <td className="py-2 px-3 text-right font-mono">{g.weekly_consistency_pct}%</td>
                      <td className="py-2 px-3 text-center">
                        {g.weekly_consistency_pct >= 90 ? '✅' : g.weekly_consistency_pct >= 70 ? '⚠️' : '❌'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data.goals_performance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="goal_name" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="weekly_consistency_pct" fill="#6366f1" radius={[4, 4, 0, 0]} name="Weekly %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : <p className="text-gray-500 text-center py-4">No active goals yet</p>}
      </div>

      {/* Upgrade Readiness */}
      {data.upgrade_readiness?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">⬆️ Upgrade Readiness</h2>
          <ul className="space-y-2">
            {data.upgrade_readiness.map(r => (
              <li key={r.goal_id} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <span className="font-medium">{r.goal_name}</span>
                <span className="text-sm text-green-700 dark:text-green-300">
                  {r.consecutive_weeks_at_95} weeks at ≥95% {r.ready_for_upgrade ? '— Ready! 🚀' : ''}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Progression Journey */}
      {data.progression_journey?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">🛤️ Progression Journey</h2>
          <div className="space-y-3">
            {data.progression_journey.map((u, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl">⬆️</div>
                <div>
                  <div className="text-sm text-gray-500">{u.date}</div>
                  <div className="font-medium">{u.previous_duty} → {u.new_duty}</div>
                  <div className="text-xs text-gray-500">{u.previous_difficulty} → {u.new_difficulty}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
