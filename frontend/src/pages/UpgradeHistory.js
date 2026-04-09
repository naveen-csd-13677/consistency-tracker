import React, { useEffect, useState } from 'react';
import { getUpgrades } from '../api';

export default function UpgradeHistory() {
  const [upgrades, setUpgrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUpgrades()
      .then(data => setUpgrades(data || []))
      .catch(() => setUpgrades([]))
      .finally(() => setLoading(false));
  }, []);

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

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : upgrades.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">No upgrades yet. Keep building consistency!</div>
      ) : (
        <>
          {/* Timeline */}
          <div className="relative">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />
            <div className="space-y-6">
              {upgrades.map((u) => (
                <div key={u.id} className="relative flex gap-4">
                  <div className="relative z-10 flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 font-bold text-sm">
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
                      <span className={`badge ${statusBadgeClass(u.status)}`}>
                        {statusDisplay(u.status)}
                      </span>
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
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 italic">📝 {u.notes}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Table View */}
          <div className="card overflow-x-auto">
            <h2 className="text-lg font-semibold mb-4">All Upgrades</h2>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b dark:border-gray-600">
                  <th className="text-left py-2 px-2">#</th>
                  <th className="text-left py-2 px-2">Date</th>
                  <th className="text-left py-2 px-2">Previous Duty</th>
                  <th className="text-left py-2 px-2">New Duty</th>
                  <th className="text-left py-2 px-2">Difficulty</th>
                  <th className="text-right py-2 px-2">Before %</th>
                  <th className="text-right py-2 px-2">After %</th>
                  <th className="text-center py-2 px-2">Status</th>
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
