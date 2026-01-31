import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { collectionsAPI } from '../services/api';
import { ResearchCollection } from '../types';
import StatusBadge from '../components/StatusBadge';
import { FolderOpen, Plus, ChevronDown, ChevronRight, Trash2, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CollectionsPage() {
  const [collections, setCollections] = useState<ResearchCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedCollection, setExpandedCollection] = useState<ResearchCollection | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

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

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this collection? Papers will not be deleted.')) return;
    try {
      await collectionsAPI.delete(id);
      setCollections(collections.filter((c) => c.id !== id));
      if (expandedId === id) {
        setExpandedId(null);
        setExpandedCollection(null);
      }
      toast.success('Collection deleted');
    } catch {
      toast.error('Failed to delete collection');
    }
  };

  const toggleExpand = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
      setExpandedCollection(null);
      return;
    }
    setExpandedId(id);
    setLoadingDetail(true);
    try {
      const res = await collectionsAPI.get(id);
      setExpandedCollection(res.data);
    } catch {
      toast.error('Failed to load collection details');
    } finally {
      setLoadingDetail(false);
    }
  };

  const removePaper = async (collectionId: string, paperId: string) => {
    try {
      await collectionsAPI.removePaper(collectionId, paperId);
      // Refresh the expanded collection
      const res = await collectionsAPI.get(collectionId);
      setExpandedCollection(res.data);
      // Update paper count in list
      setCollections((prev) =>
        prev.map((c) =>
          c.id === collectionId ? { ...c, papers_count: (c.papers_count || 1) - 1 } : c
        )
      );
      toast.success('Paper removed from collection');
    } catch {
      toast.error('Failed to remove paper');
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
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
              Create
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>
      ) : collections.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <FolderOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No collections yet. Create one to start organizing papers.</p>
          <p className="text-sm text-gray-400 mt-1">Then add papers from the paper detail page.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {collections.map((col) => (
            <div key={col.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {/* Collection header */}
              <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                onClick={() => toggleExpand(col.id)}
              >
                <div className="flex items-center gap-3">
                  {expandedId === col.id ? (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  )}
                  <div>
                    <h3 className="font-semibold text-gray-900">{col.name}</h3>
                    {col.description && <p className="text-sm text-gray-500 mt-0.5">{col.description}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500">{col.papers_count} papers</span>
                  <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-600">
                    {col.is_public ? 'Public' : 'Private'}
                  </span>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(col.id); }}
                    className="p-1 hover:bg-red-50 rounded text-gray-400 hover:text-red-500"
                    title="Delete collection"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Expanded paper list */}
              {expandedId === col.id && (
                <div className="border-t border-gray-100">
                  {loadingDetail ? (
                    <div className="flex justify-center py-6">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600" />
                    </div>
                  ) : expandedCollection?.papers && expandedCollection.papers.length > 0 ? (
                    <div className="divide-y divide-gray-50">
                      {expandedCollection.papers.map((paper) => (
                        <div key={paper.id} className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
                          <Link to={`/papers/${paper.id}`} className="flex-1 min-w-0 mr-4">
                            <p className="text-sm font-medium text-gray-900 hover:text-primary-600 truncate">{paper.title}</p>
                            <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500">
                              <span>{paper.source}</span>
                              {paper.published_date && <span>{new Date(paper.published_date).toLocaleDateString()}</span>}
                            </div>
                          </Link>
                          <div className="flex items-center gap-2 shrink-0">
                            {paper.agi_score != null && (
                              <span className={`text-sm font-bold ${paper.agi_score >= 70 ? 'text-green-600' : paper.agi_score >= 40 ? 'text-yellow-600' : 'text-red-600'}`}>
                                {paper.agi_score.toFixed(1)}
                              </span>
                            )}
                            {paper.classification && <StatusBadge status={paper.classification} />}
                            <button
                              onClick={() => removePaper(col.id, paper.id)}
                              className="p-1 hover:bg-red-50 rounded text-gray-400 hover:text-red-500"
                              title="Remove from collection"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="px-4 py-6 text-sm text-gray-500 text-center">
                      No papers in this collection yet. Go to a paper detail page and click the folder icon to add papers.
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
