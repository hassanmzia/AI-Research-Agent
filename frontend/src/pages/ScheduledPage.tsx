import React, { useEffect, useState } from 'react';
import { scheduledAPI } from '../services/api';
import { ScheduledResearch } from '../types';
import { Clock, Plus, Power, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ScheduledPage() {
  const [jobs, setJobs] = useState<ScheduledResearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: '', research_objective: '', frequency: 'weekly', max_papers: 10,
  });

  useEffect(() => {
    scheduledAPI.list()
      .then((res) => setJobs(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await scheduledAPI.create(form);
      setJobs([res.data, ...jobs]);
      setShowForm(false);
      setForm({ name: '', research_objective: '', frequency: 'weekly', max_papers: 10 });
      toast.success('Scheduled research created');
    } catch {
      toast.error('Failed to create');
    }
  };

  const toggleJob = async (id: string) => {
    try {
      const res = await scheduledAPI.toggle(id);
      setJobs((prev) => prev.map((j) => (j.id === id ? { ...j, is_active: res.data.is_active } : j)));
    } catch {
      toast.error('Failed to toggle');
    }
  };

  const deleteJob = async (id: string) => {
    try {
      await scheduledAPI.delete(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
      toast.success('Deleted');
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Scheduled Research</h1>
          <p className="text-sm text-gray-500">Automated recurring research jobs</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 w-full sm:w-auto"
        >
          <Plus className="h-4 w-4" /> Schedule New
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 space-y-3">
          <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Job name" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
          <textarea required value={form.research_objective} onChange={(e) => setForm({ ...form, research_objective: e.target.value })}
            placeholder="Research objective" rows={2} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}
              className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="biweekly">Bi-Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
            <input type="number" min={1} max={50} value={form.max_papers} onChange={(e) => setForm({ ...form, max_papers: Number(e.target.value) })}
              placeholder="Max papers"
              className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
          </div>
          <button type="submit" className="w-full sm:w-auto px-4 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">Create</button>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No scheduled research jobs yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-gray-900 text-sm sm:text-base">{job.name}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${job.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {job.is_active ? 'Active' : 'Paused'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{job.research_objective}</p>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-gray-500">
                    <span>{job.frequency}</span>
                    <span>Max: {job.max_papers}</span>
                    <span>Runs: {job.total_runs}</span>
                    {job.last_run_at && <span>Last: {new Date(job.last_run_at).toLocaleDateString()}</span>}
                    {job.next_run_at && <span>Next: {new Date(job.next_run_at).toLocaleDateString()}</span>}
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button onClick={() => toggleJob(job.id)} className="p-2.5 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <Power className={`h-4 w-4 ${job.is_active ? 'text-green-600' : 'text-gray-400'}`} />
                  </button>
                  <button onClick={() => deleteJob(job.id)} className="p-2.5 border border-gray-300 rounded-lg hover:bg-red-50">
                    <Trash2 className="h-4 w-4 text-red-400" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
