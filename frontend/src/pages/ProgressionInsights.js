import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getInsights } from '../api';

export default function ProgressionInsights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getInsights()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading insights">
        <div className="text-lg text-gray-500">
          <span className="animate-pulse" aria-hidden="true">💡 </span>Loading progression insights...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-8" role="alert">
        <p className="text-red-600 dark:text-red-400">Failed to load insights: {error}</p>
        <button onClick={() => window.location.reload()} className="btn-primary mt-4">Retry</button>
      </div>
    );
  }

  if (!data) return null;

  const { upgrade_performance_matrix, difficulty_progression_paths, upgrade_safety_indicators, compounding_effect_analysis, next_upgrade_recommendations } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Progression Insights</h1>

      {/* Upgrade Performance Matrix */}
      <section className="card" aria-labelledby="perf-matrix-heading">
        <h2 id="perf-matrix-heading" className="text-lg font-semibold mb-4">
          <span aria-hidden="true">📊 </span>Upgrade Performance Matrix
        </h2>
        {upgrade_performance_matrix.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={upgrade_performance_matrix}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="goal_name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="success_rate" fill="#22c55e" radius={[4, 4, 0, 0]} name="Success Rate %" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm" aria-label="Upgrade performance details">
                <thead>
                  <tr className="border-b dark:border-gray-600">
                    <th scope="col" className="text-left py-2 px-2">Goal</th>
                    <th scope="col" className="text-center py-2 px-2">Total</th>
                    <th scope="col" className="text-center py-2 px-2">Good</th>
                    <th scope="col" className="text-center py-2 px-2">Watch</th>
                    <th scope="col" className="text-center py-2 px-2">Failed</th>
                    <th scope="col" className="text-right py-2 px-2">Success %</th>
                    <th scope="col" className="text-right py-2 px-2">Avg Drop</th>
                  </tr>
                </thead>
                <tbody>
                  {upgrade_performance_matrix.map(d => (
                    <tr key={d.goal_id} className="border-b dark:border-gray-700">
                      <td className="py-2 px-2 font-medium">{d.goal_name}</td>
                      <td className="py-2 px-2 text-center">{d.total_upgrades}</td>
                      <td className="py-2 px-2 text-center text-green-600">{d.good}</td>
                      <td className="py-2 px-2 text-center text-yellow-600">{d.watch}</td>
                      <td className="py-2 px-2 text-center text-red-600">{d.failed}</td>
                      <td className="py-2 px-2 text-right font-bold">{d.success_rate}%</td>
                      <td className="py-2 px-2 text-right">{d.avg_consistency_drop}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p className="text-gray-500 text-center py-4">No upgrade data yet. Complete some upgrades to see performance metrics.</p>
        )}
      </section>

      {/* Difficulty Progression Paths */}
      <section className="card" aria-labelledby="diff-paths-heading">
        <h2 id="diff-paths-heading" className="text-lg font-semibold mb-4">
          <span aria-hidden="true">🛤️ </span>Difficulty Progression Paths
        </h2>
        {difficulty_progression_paths.length > 0 ? (
          <div className="space-y-3">
            {difficulty_progression_paths.map(item => (
              <div key={item.goal_id} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-sm font-medium mb-2">{item.goal_name}</div>
                <div className="flex items-center gap-2 flex-wrap" role="list" aria-label={`Difficulty path for ${item.goal_name}`}>
                  {item.path.map((level, i) => (
                    <React.Fragment key={i}>
                      {i > 0 && <span className="text-gray-400" aria-hidden="true">→</span>}
                      <span role="listitem" className={`badge ${i === item.path.length - 1 ? 'badge-blue' : 'badge-gray'}`}>
                        {level}
                      </span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No progression data yet</p>
        )}
      </section>

      {/* Upgrade Safety Indicators */}
      <section className="card" aria-labelledby="safety-heading">
        <h2 id="safety-heading" className="text-lg font-semibold mb-4">
          <span aria-hidden="true">🛡️ </span>Upgrade Safety Indicators
        </h2>
        {upgrade_safety_indicators.length > 0 ? (
          <div className="space-y-3">
            {upgrade_safety_indicators.map(r => (
              <div key={r.goal_id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <div className="font-medium">{r.goal_name}</div>
                  <div className="text-sm text-gray-500">{r.current_difficulty}</div>
                </div>
                <div className="text-right">
                  <div className="font-mono">{r.weekly_consistency_pct}% this week</div>
                  <div className="text-sm">{r.consecutive_weeks_at_95} weeks at ≥95%</div>
                  <span className={`badge mt-1 ${
                    r.risk_level === 'low' ? 'badge-green' :
                    r.risk_level === 'medium' ? 'badge-yellow' : 'badge-red'
                  }`}>
                    Risk: {r.risk_level} {r.past_failure_rate > 0 ? `(${r.past_failure_rate}% past failures)` : ''}
                  </span>
                  <div className="text-xs text-gray-500 mt-1">{r.recommendation}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No active goals</p>
        )}
      </section>

      {/* Compounding Effect Analysis */}
      <section className="card" aria-labelledby="compound-heading">
        <h2 id="compound-heading" className="text-lg font-semibold mb-4">
          <span aria-hidden="true">📈 </span>Compounding Effect Analysis
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {compounding_effect_analysis.total_upgrades_completed}
            </div>
            <div className="text-sm text-gray-500">Total Upgrades</div>
          </div>
          <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {compounding_effect_analysis.goals_with_upgrades}
            </div>
            <div className="text-sm text-gray-500">Goals Upgraded</div>
          </div>
          <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {compounding_effect_analysis.highest_difficulty_achieved}
            </div>
            <div className="text-sm text-gray-500">Highest Difficulty</div>
          </div>
        </div>
        <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            {compounding_effect_analysis.narrative}
          </p>
        </div>
      </section>

      {/* Next Upgrade Recommendations */}
      <section className="card" aria-labelledby="reco-heading">
        <h2 id="reco-heading" className="text-lg font-semibold mb-4">
          <span aria-hidden="true">🎯 </span>Next Upgrade Recommendations
        </h2>
        {next_upgrade_recommendations.length > 0 ? (
          <div className="space-y-3">
            {next_upgrade_recommendations.map(r => (
              <div key={r.goal_id} className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{r.goal_name}</span>
                  <span className={`badge ${
                    r.priority === 'high' ? 'badge-green' :
                    r.priority === 'medium' ? 'badge-yellow' : 'badge-gray'
                  }`}>
                    {r.priority} priority
                  </span>
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {r.current_duty} ({r.current_difficulty}) — {r.consecutive_weeks_at_95} weeks at ≥95%
                </div>
                {r.ready_for_upgrade && (
                  <div className="mt-2 text-sm font-medium text-green-700 dark:text-green-300">
                    <span aria-hidden="true">🚀 </span>Ready for upgrade!
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No recommendations available yet</p>
        )}
      </section>
    </div>
  );
}
