import React, { useEffect, useState } from 'react';
import { getConfig, updateConfig, exportData } from '../api';

export default function Settings() {
  const [config, setConfig] = useState(null);
  const [form, setForm] = useState({
    provider: '', model: '', openai_api_key: '', anthropic_api_key: '',
    google_api_key: '', ollama_base_url: 'http://localhost:11434',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    getConfig()
      .then(data => {
        setConfig(data);
        setForm({
          provider: data?.provider || '',
          model: data?.model || '',
          openai_api_key: '', // Don't prefill keys
          anthropic_api_key: '',
          google_api_key: '',
          ollama_base_url: data?.ollama_base_url || 'http://localhost:11434',
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      // Only send non-empty fields
      const data = { provider: form.provider, model: form.model, ollama_base_url: form.ollama_base_url };
      if (form.openai_api_key) data.openai_api_key = form.openai_api_key;
      if (form.anthropic_api_key) data.anthropic_api_key = form.anthropic_api_key;
      if (form.google_api_key) data.google_api_key = form.google_api_key;

      const updated = await updateConfig(data);
      setConfig(updated);
      setMessage('Settings saved successfully!');
      setForm(prev => ({ ...prev, openai_api_key: '', anthropic_api_key: '', google_api_key: '' }));
    } catch (err) {
      setMessage('Error: ' + err.message);
    }
    setSaving(false);
  };

  const providers = [
    { value: '', label: 'None (Rule-based only)' },
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'google', label: 'Google Gemini' },
    { value: 'ollama', label: 'Ollama (Local)' },
  ];

  const modelSuggestions = {
    openai: ['gpt-4', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
    google: ['gemini-pro'],
    ollama: ['llama2', 'mistral', 'codellama'],
  };

  if (loading) return <div className="text-center py-12 text-gray-500">Loading settings...</div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* LLM Configuration */}
      <form onSubmit={handleSave} className="card space-y-4">
        <h2 className="text-lg font-semibold">🤖 LLM Configuration</h2>

        {message && (
          <div className={`p-3 rounded-lg text-sm ${message.startsWith('Error') ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300' : 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'}`}>
            {message}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">Provider</label>
          <select className="select-field" value={form.provider} onChange={e => setForm({...form, provider: e.target.value, model: ''})}>
            {providers.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>

        {form.provider && (
          <div>
            <label className="block text-sm font-medium mb-1">Model</label>
            <input className="input-field" value={form.model} onChange={e => setForm({...form, model: e.target.value})} placeholder="Enter model name" />
            {modelSuggestions[form.provider] && (
              <div className="mt-1 flex gap-1 flex-wrap">
                {modelSuggestions[form.provider].map(m => (
                  <button key={m} type="button" onClick={() => setForm({...form, model: m})} className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-indigo-100 dark:hover:bg-indigo-900 transition-colors">
                    {m}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {form.provider === 'openai' && (
          <div>
            <label className="block text-sm font-medium mb-1">OpenAI API Key</label>
            <input type="password" className="input-field" value={form.openai_api_key} onChange={e => setForm({...form, openai_api_key: e.target.value})} placeholder={config?.openai_api_key || 'sk-...'} />
          </div>
        )}

        {form.provider === 'anthropic' && (
          <div>
            <label className="block text-sm font-medium mb-1">Anthropic API Key</label>
            <input type="password" className="input-field" value={form.anthropic_api_key} onChange={e => setForm({...form, anthropic_api_key: e.target.value})} placeholder={config?.anthropic_api_key || 'sk-ant-...'} />
          </div>
        )}

        {form.provider === 'google' && (
          <div>
            <label className="block text-sm font-medium mb-1">Google API Key</label>
            <input type="password" className="input-field" value={form.google_api_key} onChange={e => setForm({...form, google_api_key: e.target.value})} placeholder={config?.google_api_key || 'Enter key'} />
          </div>
        )}

        {form.provider === 'ollama' && (
          <div>
            <label className="block text-sm font-medium mb-1">Ollama Base URL</label>
            <input className="input-field" value={form.ollama_base_url} onChange={e => setForm({...form, ollama_base_url: e.target.value})} />
          </div>
        )}

        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </form>

      {/* Data Export */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">📤 Data Export</h2>
        <p className="text-sm text-gray-500">Export all your data including goals, daily logs, and upgrade history.</p>
        <div className="flex gap-3">
          <a href={exportData('json')} download className="btn-primary inline-block">Export JSON</a>
          <a href={exportData('csv')} download className="btn-secondary inline-block">Export CSV</a>
        </div>
      </div>

      {/* Theme Info */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-2">🎨 Theme</h2>
        <p className="text-sm text-gray-500">Use the moon/sun icon in the header to toggle between dark and light themes. Your preference is saved automatically.</p>
      </div>
    </div>
  );
}
