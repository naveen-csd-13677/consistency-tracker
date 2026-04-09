import React, { useEffect, useState } from 'react';
import { getGoals, createGoal, updateGoal, deleteGoal } from '../api';

const DIFFICULTIES = ['Easy', 'Medium', 'Hard', 'Hard+', 'Elite'];
const PRIORITIES = ['High', 'Medium', 'Low'];
const STATUSES = ['Active', 'Paused', 'Completed'];

const emptyForm = { name: '', purpose: '', current_duty: '', difficulty: 'Easy', priority: 'Medium', status: 'Active' };

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  const loadGoals = async () => {
    setLoading(true);
    try { setGoals(await getGoals() || []); } catch { setGoals([]); }
    setLoading(false);
  };

  useEffect(() => { loadGoals(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateGoal(editingId, form);
      } else {
        await createGoal(form);
      }
      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
      await loadGoals();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const startEdit = (goal) => {
    setForm({
      name: goal.name, purpose: goal.purpose || '', current_duty: goal.current_duty,
      difficulty: goal.difficulty, priority: goal.priority, status: goal.status,
    });
    setEditingId(goal.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this goal and all its data?')) return;
    try { await deleteGoal(id); await loadGoals(); } catch (err) { alert('Error: ' + err.message); }
  };

  const statusBadge = (status) => {
    const classes = { Active: 'badge-green', Paused: 'badge-yellow', Completed: 'badge-blue' };
    return <span className={`badge ${classes[status] || 'badge-gray'}`}>{status}</span>;
  };

  const diffBadge = (diff) => {
    const classes = { Easy: 'badge-green', Medium: 'badge-yellow', Hard: 'badge-red', 'Hard+': 'badge-red', Elite: 'badge-blue' };
    return <span className={`badge ${classes[diff] || 'badge-gray'}`}>{diff}</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Goals Management</h1>
        <button onClick={() => { setForm(emptyForm); setEditingId(null); setShowForm(!showForm); }} className="btn-primary">
          {showForm ? 'Cancel' : '+ New Goal'}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <h2 className="text-lg font-semibold">{editingId ? 'Edit Goal' : 'Create New Goal'}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name *</label>
              <input required className="input-field" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g., Get Fit" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Current Duty *</label>
              <input required className="input-field" value={form.current_duty} onChange={e => setForm({...form, current_duty: e.target.value})} placeholder="e.g., Run 5 km" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">Purpose / Why</label>
              <textarea className="input-field" rows={2} value={form.purpose} onChange={e => setForm({...form, purpose: e.target.value})} placeholder="Why is this goal important to you?" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Difficulty</label>
              <select className="select-field" value={form.difficulty} onChange={e => setForm({...form, difficulty: e.target.value})}>
                {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select className="select-field" value={form.priority} onChange={e => setForm({...form, priority: e.target.value})}>
                {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select className="select-field" value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
                {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">{editingId ? 'Update' : 'Create'} Goal</button>
            <button type="button" onClick={() => { setShowForm(false); setEditingId(null); }} className="btn-secondary">Cancel</button>
          </div>
        </form>
      )}

      {/* Goals List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading goals...</div>
      ) : goals.length === 0 ? (
        <div className="card text-center py-8 text-gray-500">No goals yet. Create your first goal above!</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {goals.map(goal => (
            <div key={goal.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{goal.name}</h3>
                  {goal.purpose && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{goal.purpose}</p>}
                </div>
                <div className="flex gap-1">
                  <button onClick={() => startEdit(goal)} className="p-1 text-gray-400 hover:text-blue-500" title="Edit">✏️</button>
                  <button onClick={() => handleDelete(goal.id)} className="p-1 text-gray-400 hover:text-red-500" title="Delete">🗑️</button>
                </div>
              </div>
              <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-sm text-gray-500 dark:text-gray-400">Current Duty</div>
                <div className="font-medium">{goal.current_duty}</div>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {diffBadge(goal.difficulty)}
                <span className={`badge ${goal.priority === 'High' ? 'badge-red' : goal.priority === 'Low' ? 'badge-gray' : 'badge-yellow'}`}>
                  {goal.priority} Priority
                </span>
                {statusBadge(goal.status)}
              </div>
              {goal.created_at && (
                <div className="mt-2 text-xs text-gray-400">Created: {new Date(goal.created_at).toLocaleDateString()}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
