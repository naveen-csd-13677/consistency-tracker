import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getMonthlyAnalytics, createUpgrade } from '../api';

function getCurrentMonth() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

export default function MonthlyGrowth() {
  const [month, setMonth] = useState(getCurrentMonth());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgradeModal, setUpgradeModal] = useState(null);
  const [upgradeForm, setUpgradeForm] = useState({ new_duty: '', new_difficulty: '' });
  const [upgrading, setUpgrading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      setData(await getMonthlyAnalytics({ month }));
    } catch {
      setData(null);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, [month]);

  const changeMonth = (delta) => {
    const [y, m] = month.split('-').map(Number);
    const d = new Date(y, m - 1 + delta, 1);
    setMonth(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  const openUpgradeModal = (goal) => {
    setUpgradeModal(goal);
    setUpgradeForm({
      new_duty: goal.proposed_new_duty || '',
      new_difficulty: '', // Will be determined by backend
    });
  };

  const handleUpgrade = async () => {
    if (!upgradeModal || !upgradeForm.new_duty.trim()) return;
    setUpgrading(true);
    try {
      const difficulties = ['Easy', 'Medium', 'Hard', 'Hard+', 'Elite'];
      const currentIdx = difficulties.indexOf(upgradeModal.previous_duty ? 'Easy' : 'Easy');
      const nextDifficulty = upgradeForm.new_difficulty ||
        (difficulties[Math.min(currentIdx + 1, difficulties.length - 1)]);

      await createUpgrade({
        goal_id: upgradeModal.goal_id,
        previous_duty: upgradeModal.previous_duty,
        new_duty: upgradeForm.new_duty,
        previous_difficulty: 'Easy', // Will be overridden from backend context
        new_difficulty: nextDifficulty,
        consistency_before: upgradeModal.current_consistency_pct,
        notes: 'Upgraded via Monthly Growth view',
      });
      setUpgradeModal(null);
      await loadData();
    } catch (e) {
      alert('Upgrade failed: ' + e.message);
    }
    setUpgrading(false);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Monthly Growth</h1>

      <div className="flex items-center gap-4" role="navigation" aria-label="Month navigation">
        <button onClick={() => changeMonth(-1)} className="btn-secondary" aria-label="Previous month">← Prev</button>
        <label htmlFor="month-select" className="sr-only">Select month</label>
        <input id="month-select" type="month" className="input-field max-w-xs" value={month} onChange={e => setMonth(e.target.value)} />
        <button onClick={() => changeMonth(1)} className="btn-secondary" aria-label="Next month">Next →</button>
        <button onClick={() => setMonth(getCurrentMonth())} className="btn-secondary">This Month</button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500" role="status">Loading monthly data...</div>
      ) : !data || !data.goals?.length ? (
        <div className="card text-center py-8 text-gray-500">No data for this month</div>
      ) : (
        <>
          {/* Chart */}
          <section className="card" aria-labelledby="monthly-chart-heading">
            <h2 id="monthly-chart-heading" className="text-lg font-semibold mb-4">Monthly Consistency by Goal</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.goals}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="goal_name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="current_consistency_pct" fill="#22c55e" radius={[4, 4, 0, 0]} name="Consistency %" />
              </BarChart>
            </ResponsiveContainer>
          </section>

          {/* Goal Cards */}
          <div className="space-y-3">
            {data.goals.map(g => (
              <div key={g.goal_id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{g.goal_name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Duty: {g.previous_duty}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold font-mono">{g.current_consistency_pct}%</div>
                    <div className="text-sm text-gray-500">{g.weeks_at_95_pct} weeks at ≥95%</div>
                  </div>
                </div>

                <div className="mt-3 flex items-center gap-3">
                  {g.ready_for_upgrade ? (
                    <span className="badge badge-green text-sm">
                      <span aria-hidden="true">🚀 </span>Ready for Upgrade!
                    </span>
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

                {g.ready_for_upgrade && (
                  <div className="mt-3">
                    <button
                      onClick={() => openUpgradeModal(g)}
                      className="btn-primary text-sm"
                      aria-label={`Confirm upgrade for ${g.goal_name}`}
                    >
                      <span aria-hidden="true">⬆️ </span>Confirm Upgrade
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {/* Upgrade Confirmation Modal */}
      {upgradeModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="upgrade-modal-title">
          <div className="card max-w-md w-full">
            <h2 id="upgrade-modal-title" className="text-lg font-semibold mb-4">
              Confirm Upgrade: {upgradeModal.goal_name}
            </h2>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-500">Current Duty</div>
                <div className="font-medium">{upgradeModal.previous_duty}</div>
              </div>
              <div>
                <label htmlFor="new-duty-input" className="block text-sm font-medium mb-1">New Duty *</label>
                <input
                  id="new-duty-input"
                  className="input-field"
                  value={upgradeForm.new_duty}
                  onChange={e => setUpgradeForm({ ...upgradeForm, new_duty: e.target.value })}
                  placeholder="Enter new duty description"
                  required
                />
              </div>
              <div>
                <label htmlFor="new-difficulty-select" className="block text-sm font-medium mb-1">New Difficulty</label>
                <select
                  id="new-difficulty-select"
                  className="select-field"
                  value={upgradeForm.new_difficulty}
                  onChange={e => setUpgradeForm({ ...upgradeForm, new_difficulty: e.target.value })}
                >
                  <option value="">Auto (next level)</option>
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                  <option value="Hard+">Hard+</option>
                  <option value="Elite">Elite</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleUpgrade}
                  disabled={upgrading || !upgradeForm.new_duty.trim()}
                  className="btn-primary"
                >
                  {upgrading ? 'Upgrading...' : 'Confirm Upgrade'}
                </button>
                <button onClick={() => setUpgradeModal(null)} className="btn-secondary">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
