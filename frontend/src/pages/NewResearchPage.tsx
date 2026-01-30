import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sessionsAPI } from '../services/api';
import { Search, Zap, Settings } from 'lucide-react';
import toast from 'react-hot-toast';

const PRESET_QUERIES = [
  'Find recent AGI papers on general intelligence and reasoning',
  'Discover papers on few-shot learning and meta-learning for AGI',
  'Search for multi-agent systems and collaborative AI research',
  'Find papers on world models and autonomous goal-setting AI',
  'Explore recent breakthroughs in task transfer and generalization',
];

export default function NewResearchPage() {
  const navigate = useNavigate();
  const [objective, setObjective] = useState('');
  const [title, setTitle] = useState('');
  const [maxPapers, setMaxPapers] = useState(10);
  const [daysLookback, setDaysLookback] = useState(14);
  const [keywords, setKeywords] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!objective.trim()) return;

    setLoading(true);
    try {
      const res = await sessionsAPI.create({
        research_objective: objective,
        title: title || undefined,
        max_papers: maxPapers,
        days_lookback: daysLookback,
        custom_keywords: keywords ? keywords.split(',').map((k) => k.trim()).filter(Boolean) : [],
      });
      toast.success('Research session started!');
      navigate(`/sessions/${res.data.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start research');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">New Research Session</h1>
        <p className="text-gray-500 mt-1">
          Define your research objective and the multi-agent system will autonomously discover, evaluate, and report on relevant papers.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Research Objective *</label>
          <textarea
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            rows={3}
            required
            placeholder="Describe what you want to research. E.g., 'Find recent papers on artificial general intelligence breakthroughs'"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Session Title (optional)</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Give this research session a name"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>

        {/* Quick Presets */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Quick Start Presets</label>
          <div className="flex flex-wrap gap-2">
            {PRESET_QUERIES.map((q, i) => (
              <button
                key={i} type="button"
                onClick={() => setObjective(q)}
                className="px-3 py-1.5 text-xs bg-primary-50 text-primary-700 rounded-full hover:bg-primary-100 transition-colors"
              >
                {q.slice(0, 50)}...
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Settings Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <Settings className="h-4 w-4" />
          {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
        </button>

        {showAdvanced && (
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Papers</label>
              <input
                type="number" min={1} max={50}
                value={maxPapers}
                onChange={(e) => setMaxPapers(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Days Lookback</label>
              <input
                type="number" min={1} max={365}
                value={daysLookback}
                onChange={(e) => setDaysLookback(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Custom Keywords (comma-separated)</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g., AGI, reasoning, meta-learning"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !objective.trim()}
          className="w-full flex items-center justify-center gap-2 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              Launching Agents...
            </>
          ) : (
            <>
              <Zap className="h-5 w-5" />
              Launch Research
            </>
          )}
        </button>
      </form>

      {/* Agent Pipeline Visualization */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Multi-Agent Pipeline</h3>
        <div className="flex items-center justify-between text-center">
          {['Lead Supervisor', 'Planner', 'Discovery Agent', 'Evaluation Agent', 'Report Synthesis'].map((step, i) => (
            <React.Fragment key={step}>
              <div className="flex flex-col items-center">
                <div className="h-10 w-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">
                  {i + 1}
                </div>
                <p className="text-xs text-gray-600 mt-2 max-w-[80px]">{step}</p>
              </div>
              {i < 4 && <div className="flex-1 h-px bg-gray-300 mx-2" />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
