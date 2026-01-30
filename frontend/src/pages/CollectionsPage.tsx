import React, { useEffect, useState } from 'react';
import { collectionsAPI } from '../services/api';
import { ResearchCollection } from '../types';
import { FolderOpen, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CollectionsPage() {
  const [collections, setCollections] = useState<ResearchCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    collectionsAPI.list()
      .then((res) => setCollections(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await collectionsAPI.create({ name, description });
      setCollections([res.data, ...collections]);
      setName('');
      setDescription('');
      setShowForm(false);
      toast.success('Collection created');
    } catch {
      toast.error('Failed to create collection');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Collections</h1>
          <p className="text-gray-500">Organize your favorite papers into curated collections</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" /> New Collection
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
          <input
            type="text" required value={name} onChange={(e) => setName(e.target.value)}
            placeholder="Collection name"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          />
          <textarea
            value={description} onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional)" rows={2}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
          />
          <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
            Create
          </button>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>
      ) : collections.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <FolderOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No collections yet. Create one to start organizing papers.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {collections.map((col) => (
            <div key={col.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-primary-300 transition-colors">
              <h3 className="font-semibold text-gray-900">{col.name}</h3>
              {col.description && <p className="text-sm text-gray-500 mt-1">{col.description}</p>}
              <div className="flex items-center gap-3 mt-3 text-xs text-gray-500">
                <span>{col.papers_count} papers</span>
                <span>{col.is_public ? 'Public' : 'Private'}</span>
                <span>{new Date(col.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
