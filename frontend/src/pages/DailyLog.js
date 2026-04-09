import React, { useEffect, useState, useCallback } from 'react';
import { getGoals, getLogs, upsertLog } from '../api';

function formatDate(d) {
  return d.toISOString().split('T')[0];
}

export default function DailyLog() {
  const [date, setDate] = useState(formatDate(new Date()));
  const [goals, setGoals] = useState([]);
  const [logs, setLogs] = useState([]);
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [goalsData, logsData] = await Promise.all([
        getGoals('Active'),
        getLogs({ date }),
      ]);
      setGoals(goalsData || []);
      setLogs(logsData || []);
      const noteMap = {};
      (logsData || []).forEach(l => { if (l.notes) noteMap[l.goal_id] = l.notes; });
      setNotes(noteMap);
    } catch {
      setGoals([]);
      setLogs([]);
    }
    setLoading(false);
  }, [date]);

  useEffect(() => { loadData(); }, [loadData]);

  const getLogForGoal = (goalId) => logs.find(l => l.goal_id === goalId);

  const toggleCompletion = async (goalId, completed) => {
    setSaving(prev => ({ ...prev, [goalId]: true }));
    try {
      await upsertLog({ goal_id: goalId, date, completed, notes: notes[goalId] || null });
      await loadData();
    } catch (e) {
      alert('Failed to save: ' + e.message);
    }
    setSaving(prev => ({ ...prev, [goalId]: false }));
  };

  const saveNote = async (goalId) => {
    const existing = getLogForGoal(goalId);
    await upsertLog({
      goal_id: goalId,
      date,
      completed: existing?.completed || false,
      notes: notes[goalId] || null,
    });
    await loadData();
  };

  const completedCount = goals.filter(g => getLogForGoal(g.id)?.completed).length;
  const totalGoals = goals.length;
  const overallPct = totalGoals > 0 ? Math.round((completedCount / totalGoals) * 100) : 0;

  const changeDate = (delta) => {
    const d = new Date(date);
    d.setDate(d.getDate() + delta);
    setDate(formatDate(d));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Daily Log</h1>

      {/* Date Navigation */}
      <div className="flex items-center gap-4" role="navigation" aria-label="Date navigation">
        <button onClick={() => changeDate(-1)} className="btn-secondary" aria-label="Previous day">← Prev</button>
        <label htmlFor="log-date-input" className="sr-only">Select date</label>
        <input
          id="log-date-input"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="input-field max-w-xs"
        />
        <button onClick={() => changeDate(1)} className="btn-secondary" aria-label="Next day">Next →</button>
        <button onClick={() => setDate(formatDate(new Date()))} className="btn-secondary">Today</button>
      </div>

      {/* Overall Stats */}
      <div className="card" role="status" aria-label={`Daily consistency: ${overallPct}%, ${completedCount} of ${totalGoals} goals completed`}>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-lg font-semibold">Overall: </span>
            <span className={`text-2xl font-bold ${overallPct === 100 ? 'text-green-600' : overallPct >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
              {overallPct}%
            </span>
          </div>
          <div className="text-gray-500">{completedCount}/{totalGoals} goals completed</div>
        </div>
        <div className="mt-2 bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${overallPct === 100 ? 'bg-green-500' : overallPct >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${overallPct}%` }}
          />
        </div>
      </div>

      {/* Goals Checklist */}
      {loading ? (
        <div className="text-center py-8 text-gray-500" role="status">Loading...</div>
      ) : goals.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">
          No active goals. <a href="/goals" className="text-indigo-600 hover:underline">Create some goals first!</a>
        </div>
      ) : (
        <div className="space-y-3" role="list" aria-label="Goals checklist">
          {goals.map(goal => {
            const log = getLogForGoal(goal.id);
            const completed = log?.completed || false;
            const isSaving = saving[goal.id];

            return (
              <div key={goal.id} className="card" role="listitem">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => toggleCompletion(goal.id, !completed)}
                    disabled={isSaving}
                    aria-label={`Mark ${goal.name} as ${completed ? 'not done' : 'done'}`}
                    aria-pressed={completed}
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-xl transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      completed
                        ? 'bg-green-500 text-white shadow-lg shadow-green-200 dark:shadow-green-900'
                        : 'bg-gray-200 dark:bg-gray-600 text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-500'
                    }`}
                  >
                    {isSaving ? '...' : completed ? '✓' : '✗'}
                  </button>
                  <div className="flex-1">
                    <div className="font-medium">{goal.name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{goal.current_duty}</div>
                    <div className="flex gap-2 mt-1">
                      <span className="badge badge-blue">{goal.difficulty}</span>
                      <span className="badge badge-gray">{goal.priority}</span>
                    </div>
                  </div>
                </div>
                {/* Notes */}
                <div className="mt-3">
                  <label htmlFor={`note-${goal.id}`} className="sr-only">Note for {goal.name}</label>
                  <input
                    id={`note-${goal.id}`}
                    type="text"
                    placeholder="Add a note..."
                    value={notes[goal.id] || ''}
                    onChange={(e) => setNotes({ ...notes, [goal.id]: e.target.value })}
                    onBlur={() => saveNote(goal.id)}
                    className="input-field text-sm"
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
