import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getUpgrades, getUpgradeReadiness, generateSuggestions } from '../api';

export default function ProgressionInsights() {
  const [upgrades, setUpgrades] = useState([]);
  const [readiness, setReadiness] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getUpgrades(), getUpgradeReadiness(), generateSuggestions()])
      .then(([u, r, s]) => {
        setUpgrades(u || []);
        setReadiness(r || []);
        setSuggestions(s || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading insights...</div>;

  // Upgrade Performance Matrix - success rate per goal
  const goalUpgrades = {};
  upgrades.forEach(u => {
    const gid = u.goal_id;
    if (!goalUpgrades[gid]) goalUpgrades[gid] = { total: 0, good: 0, watch: 0, failed: 0 };
    goalUpgrades[gid].total++;
    if (u.status === 'Good') goalUpgrades[gid].good++;
    else if (u.status === 'Watch') goalUpgrades[gid].watch++;
    else if (u.status === 'Failed') goalUpgrades[gid].failed++;
  });

  const performanceData = Object.entries(goalUpgrades).map(([gid, data]) => ({
    goal_id: gid,
    success_rate: data.total > 0 ? Math.round((data.good / data.total) * 100) : 0,
    total: data.total,
    good: data.good,
    watch: data.watch,
    failed: data.failed,
  }));

  // Difficulty progression paths
  const diffPaths = {};
  upgrades.forEach(u => {
    const gid = u.goal_id;
    if (!diffPaths[gid]) diffPaths[gid] = [];
    diffPaths[gid].push({
      from: u.previous_difficulty,
      to: u.new_difficulty,
      date: u.date,
    });
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Progression Insights</h1>

      {/* Upgrade Performance Matrix */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">📊 Upgrade Performance Matrix</h2>
        {performanceData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="goal_id" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="success_rate" fill="#22c55e" radius={[4, 4, 0, 0]} name="Success Rate %" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b dark:border-gray-600">
                    <th className="text-left py-2 px-2">Goal</th>
                    <th className="text-center py-2 px-2">Total</th>
                    <th className="text-center py-2 px-2">✅ Good</th>
                    <th className="text-center py-2 px-2">⚠️ Watch</th>
                    <th className="text-center py-2 px-2">❌ Failed</th>
                    <th className="text-right py-2 px-2">Success %</th>
                  </tr>
                </thead>
                <tbody>
                  {performanceData.map(d => (
                    <tr key={d.goal_id} className="border-b dark:border-gray-700">
                      <td className="py-2 px-2 font-mono text-xs">{d.goal_id.slice(0, 8)}...</td>
                      <td className="py-2 px-2 text-center">{d.total}</td>
                      <td className="py-2 px-2 text-center text-green-600">{d.good}</td>
                      <td className="py-2 px-2 text-center text-yellow-600">{d.watch}</td>
                      <td className="py-2 px-2 text-center text-red-600">{d.failed}</td>
                      <td className="py-2 px-2 text-right font-bold">{d.success_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p className="text-gray-500 text-center py-4">No upgrade data yet</p>
        )}
      </div>

      {/* Difficulty Progression Paths */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">🛤️ Difficulty Progression Paths</h2>
        {Object.keys(diffPaths).length > 0 ? (
          <div className="space-y-3">
            {Object.entries(diffPaths).map(([gid, path]) => (
              <div key={gid} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-xs text-gray-500 mb-1">Goal: {gid.slice(0, 8)}...</div>
                <div className="flex items-center gap-2 flex-wrap">
                  {path.map((step, i) => (
                    <React.Fragment key={i}>
                      {i === 0 && <span className="badge badge-gray">{step.from}</span>}
                      <span className="text-gray-400">→</span>
                      <span className="badge badge-blue">{step.to}</span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No progression data yet</p>
        )}
      </div>

      {/* Upgrade Safety Indicators / Readiness */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">🛡️ Upgrade Safety Indicators</h2>
        {readiness.length > 0 ? (
          <div className="space-y-3">
            {readiness.map(r => (
              <div key={r.goal_id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <div className="font-medium">{r.goal_name}</div>
                  <div className="text-sm text-gray-500">{r.current_duty} ({r.current_difficulty})</div>
                </div>
                <div className="text-right">
                  <div className="font-mono">{r.weekly_consistency_pct}% this week</div>
                  <div className="text-sm">{r.consecutive_weeks_at_95} weeks at ≥95%</div>
                  {r.ready_for_upgrade ? (
                    <span className="badge badge-green mt-1">Safe to upgrade ✅</span>
                  ) : r.consecutive_weeks_at_95 >= 2 ? (
                    <span className="badge badge-yellow mt-1">Approaching ⚠️</span>
                  ) : (
                    <span className="badge badge-gray mt-1">Not ready</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No active goals</p>
        )}
      </div>

      {/* Next Upgrade Recommendations */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">🎯 Next Upgrade Recommendations</h2>
        {suggestions.length > 0 ? (
          <div className="space-y-3">
            {suggestions.map(s => (
              <div key={s.goal_id} className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{s.goal_name}</span>
                  <span className={`badge ${s.suggestion_type === 'upgrade' ? 'badge-green' : s.suggestion_type === 'modification' ? 'badge-red' : 'badge-yellow'}`}>
                    {s.suggestion_type}
                  </span>
                </div>
                <p className="text-sm mt-2">{s.suggestion}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No suggestions available</p>
        )}
      </div>

      {/* Compounding Effect */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">📈 Compounding Effect Analysis</h2>
        <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            {upgrades.length > 0
              ? `You've completed ${upgrades.length} upgrade${upgrades.length > 1 ? 's' : ''} across your goals. Each upgrade represents a meaningful step forward in your journey. Small, consistent improvements compound over time — keep building on your foundation!`
              : 'Start tracking your goals consistently to see how small improvements compound over time. Even 1% daily improvement leads to 37x growth over a year!'}
          </p>
        </div>
      </div>
    </div>
  );
}
