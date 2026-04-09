import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMonthlyAnalytics } from '../api';

function getCurrentMonth() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

export default function MonthlyGrowth() {
  const [month, setMonth] = useState(getCurrentMonth());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getMonthlyAnalytics({ month })
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [month]);

  const changeMonth = (delta) => {
    const [y, m] = month.split('-').map(Number);
    const d = new Date(y, m - 1 + delta, 1);
    setMonth(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Monthly Growth</h1>

      <div className="flex items-center gap-4">
        <button onClick={() => changeMonth(-1)} className="btn-secondary">← Prev</button>
        <input type="month" className="input-field max-w-xs" value={month} onChange={e => setMonth(e.target.value)} />
        <button onClick={() => changeMonth(1)} className="btn-secondary">Next →</button>
        <button onClick={() => setMonth(getCurrentMonth())} className="btn-secondary">This Month</button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : !data || !data.goals?.length ? (
        <div className="card text-center py-8 text-gray-500">No data for this month</div>
      ) : (
        <>
          {/* Chart */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Monthly Consistency by Goal</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.goals}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="goal_name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="current_consistency_pct" fill="#22c55e" radius={[4, 4, 0, 0]} name="Consistency %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Goal Cards */}
          <div className="space-y-3">
            {data.goals.map(g => (
              <div key={g.goal_id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{g.goal_name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Current: {g.previous_duty}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold font-mono">{g.current_consistency_pct}%</div>
                    <div className="text-sm text-gray-500">{g.weeks_at_95_pct} weeks at ≥95%</div>
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-3">
                  {g.ready_for_upgrade ? (
                    <span className="badge badge-green text-sm">🚀 Ready for Upgrade!</span>
                  ) : (
                    <span className="badge badge-gray text-sm">Needs {4 - g.weeks_at_95_pct} more weeks at ≥95%</span>
                  )}
                </div>

                {g.proposed_new_duty && (
                  <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="text-sm font-medium text-green-700 dark:text-green-300">Proposed New Duty</div>
                    <p className="text-sm mt-1">{g.proposed_new_duty}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
