import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getWeeklyAnalytics } from '../api';

function getCurrentISOWeek() {
  const now = new Date();
  const d = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}

export default function WeeklyAnalytics() {
  const [week, setWeek] = useState(getCurrentISOWeek());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getWeeklyAnalytics({ week })
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [week]);

  const changeWeek = (delta) => {
    const match = week.match(/(\d{4})-W(\d+)/);
    if (!match) return;
    let y = parseInt(match[1]), w = parseInt(match[2]) + delta;
    if (w <= 0) { y--; w = 52; }
    if (w > 52) { y++; w = 1; }
    setWeek(`${y}-W${String(w).padStart(2, '0')}`);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Weekly Analytics</h1>

      <div className="flex items-center gap-4">
        <button onClick={() => changeWeek(-1)} className="btn-secondary">← Prev</button>
        <input className="input-field max-w-xs" value={week} onChange={e => setWeek(e.target.value)} placeholder="2026-W15" />
        <button onClick={() => changeWeek(1)} className="btn-secondary">Next →</button>
        <button onClick={() => setWeek(getCurrentISOWeek())} className="btn-secondary">This Week</button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading analytics...</div>
      ) : !data || !data.goals?.length ? (
        <div className="card text-center py-8 text-gray-500">No data for this week</div>
      ) : (
        <>
          {/* Overall */}
          <div className="card">
            <div className="text-center">
              <span className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{data.overall_consistency_pct}%</span>
              <div className="text-sm text-gray-500 mt-1">Overall Weekly Consistency</div>
            </div>
          </div>

          {/* Chart */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Per-Goal Consistency</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.goals}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="goal_name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="weekly_consistency_pct" fill="#6366f1" radius={[4, 4, 0, 0]} name="Consistency %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Goal Details */}
          <div className="space-y-3">
            {data.goals.map(g => (
              <div key={g.goal_id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{g.goal_name}</h3>
                    <div className="text-sm text-gray-500">{g.week}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold font-mono">{g.weekly_consistency_pct}%</span>
                    <span className="text-2xl">{g.status_indicator}</span>
                  </div>
                </div>
                {g.llm_suggestion && (
                  <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm">
                    <div className="font-medium text-blue-700 dark:text-blue-300 mb-1">💡 Suggestion</div>
                    <p>{g.llm_suggestion}</p>
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
