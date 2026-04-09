import React, { useEffect, useState } from 'react';
import { getUpgrades, rollbackUpgrade, evaluateUpgrades, getDowngradeSuggestions } from '../api';

export default function UpgradeHistory() {
  const [upgrades, setUpgrades] = useState([]);
  const [downgradeSuggestions, setDowngradeSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rollingBack, setRollingBack] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      // Evaluate pending upgrades on load
      await evaluateUpgrades().catch(() => {});
      const [u, ds] = await Promise.all([
        getUpgrades(),
        getDowngradeSuggestions().catch(() => []),
      ]);
      setUpgrades(u || []);
      setDowngradeSuggestions(ds || []);
    } catch {
      setUpgrades([]);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const handleRollback = async (upgradeId) => {
    if (!window.confirm('Are you sure you want to roll back this upgrade? The goal will revert to its previous duty and difficulty.')) return;
    setRollingBack(upgradeId);
    try {
      await rollbackUpgrade(upgradeId, { notes: 'Manual rollback by user' });
      await loadData();
    } catch (e) {
      alert('Rollback failed: ' + e.message);
    }
    setRollingBack(null);
  };

  const statusDisplay = (status) => {
    const map = { Good: '✅ Good', Watch: '⚠️ Watch', Failed: '❌ Failed' };
    return map[status] || status || '—';
  };

  const statusBadgeClass = (status) => {
    const map = { Good: 'badge-green', Watch: 'badge-yellow', Failed: 'badge-red' };
    return map[status] || 'badge-gray';
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Upgrade History</h1>

      {/* Downgrade Suggestions */}
      {downgradeSuggestions.length > 0 && (
        <section className="card border-red-300 dark:border-red-700" role="alert" aria-labelledby="downgrade-heading">
          <h2 id="downgrade-heading" className="text-lg font-semibold text-red-600 dark:text-red-400 mb-3">
            <span aria-hidden="true">⚠️ </span>Downgrade Suggestions
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            These goals have been struggling since their last upgrade. Consider rolling back.
          </p>
          {downgradeSuggestions.map(ds => (
            <div key={ds.upgrade_id} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg mb-2">
              <div className="font-medium">{ds.goal_name}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{ds.suggestion}</div>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => handleRollback(ds.upgrade_id)}
                  disabled={rollingBack === ds.upgrade_id}
                  className="btn-danger text-sm"
                  aria-label={`Roll back upgrade for ${ds.goal_name}`}
                >
                  {rollingBack === ds.upgrade_id ? 'Rolling back...' : 'Roll Back'}
                </button>
              </div>
            </div>
          ))}
        </section>
      )}

      {loading ? (
        <div className="text-center py-8 text-gray-500" role="status">Loading upgrade history...</div>
      ) : upgrades.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">No upgrades yet. Keep building consistency!</div>
      ) : (
        <>
          {/* Timeline */}
          <div className="relative" aria-label="Upgrade timeline">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" aria-hidden="true" />
            <div className="space-y-6">
              {upgrades.map((u) => (
                <div key={u.id} className="relative flex gap-4">
                  <div className="relative z-10 flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 font-bold text-sm" aria-hidden="true">
                    #{u.upgrade_number}
                  </div>
                  <div className="card flex-1">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div>
                        <div className="text-sm text-gray-500">
                          {u.date ? new Date(u.date).toLocaleDateString() : 'Unknown date'}
                        </div>
                        <h3 className="font-semibold">Upgrade #{u.upgrade_number}</h3>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`badge ${statusBadgeClass(u.status)}`}>
                          {statusDisplay(u.status)}
                        </span>
                        {u.status !== 'Failed' && (
                          <button
                            onClick={() => handleRollback(u.id)}
                            disabled={rollingBack === u.id}
                            className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-red-100 dark:hover:bg-red-900/30 text-gray-600 dark:text-gray-400 hover:text-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
                            aria-label={`Roll back upgrade #${u.upgrade_number}`}
                          >
                            {rollingBack === u.id ? '...' : 'Rollback'}
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <div className="text-xs text-red-600 dark:text-red-400 font-medium">Previous</div>
                        <div className="font-medium">{u.previous_duty}</div>
                        <div className="text-sm text-gray-500">{u.previous_difficulty}</div>
                      </div>
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="text-xs text-green-600 dark:text-green-400 font-medium">New</div>
                        <div className="font-medium">{u.new_duty}</div>
                        <div className="text-sm text-gray-500">{u.new_difficulty}</div>
                      </div>
                    </div>

                    <div className="mt-3 flex gap-4 text-sm text-gray-500">
                      <span>Before: {u.consistency_before != null ? `${u.consistency_before}%` : '—'}</span>
                      <span>After: {u.consistency_after != null ? `${u.consistency_after}%` : '—'}</span>
                    </div>

                    {u.notes && (
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 italic">
                        <span aria-hidden="true">📝 </span>{u.notes}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Table View */}
          <section className="card overflow-x-auto" aria-labelledby="all-upgrades-heading">
            <h2 id="all-upgrades-heading" className="text-lg font-semibold mb-4">All Upgrades</h2>
            <table className="w-full text-sm" aria-label="All upgrades table">
              <thead>
                <tr className="border-b dark:border-gray-600">
                  <th scope="col" className="text-left py-2 px-2">#</th>
                  <th scope="col" className="text-left py-2 px-2">Date</th>
                  <th scope="col" className="text-left py-2 px-2">Previous Duty</th>
                  <th scope="col" className="text-left py-2 px-2">New Duty</th>
                  <th scope="col" className="text-left py-2 px-2">Difficulty</th>
                  <th scope="col" className="text-right py-2 px-2">Before %</th>
                  <th scope="col" className="text-right py-2 px-2">After %</th>
                  <th scope="col" className="text-center py-2 px-2">Status</th>
                  <th scope="col" className="text-center py-2 px-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {upgrades.map(u => (
                  <tr key={u.id} className="border-b dark:border-gray-700">
                    <td className="py-2 px-2">{u.upgrade_number}</td>
                    <td className="py-2 px-2">{u.date ? new Date(u.date).toLocaleDateString() : '—'}</td>
                    <td className="py-2 px-2">{u.previous_duty}</td>
                    <td className="py-2 px-2">{u.new_duty}</td>
                    <td className="py-2 px-2">{u.previous_difficulty} → {u.new_difficulty}</td>
                    <td className="py-2 px-2 text-right">{u.consistency_before != null ? `${u.consistency_before}%` : '—'}</td>
                    <td className="py-2 px-2 text-right">{u.consistency_after != null ? `${u.consistency_after}%` : '—'}</td>
                    <td className="py-2 px-2 text-center">{statusDisplay(u.status)}</td>
                    <td className="py-2 px-2 text-center">
                      {u.status !== 'Failed' && (
                        <button
                          onClick={() => handleRollback(u.id)}
                          disabled={rollingBack === u.id}
                          className="text-xs text-red-600 hover:underline focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                          aria-label={`Roll back upgrade #${u.upgrade_number}`}
                        >
                          {rollingBack === u.id ? '...' : 'Rollback'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}
