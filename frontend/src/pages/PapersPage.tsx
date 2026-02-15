import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { papersAPI } from '../services/api';
import { Paper } from '../types';
import StatusBadge from '../components/StatusBadge';
import { BookOpen, Bookmark, Search } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'bookmarked'>('all');

  useEffect(() => {
    const params: Record<string, any> = {};
    if (search) params.search = search;
    if (filter === 'bookmarked') params.is_bookmarked = true;

    papersAPI.list(params)
      .then((res) => setPapers(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, [search, filter]);

  const toggleBookmark = async (paper: Paper) => {
    try {
      const res = await papersAPI.bookmark(paper.id);
      setPapers((prev) =>
        prev.map((p) => (p.id === paper.id ? { ...p, is_bookmarked: res.data.is_bookmarked } : p))
      );
    } catch {
      toast.error('Failed to toggle bookmark');
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Papers</h1>
        <p className="text-sm text-gray-500">All discovered research papers across sessions</p>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1 sm:max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search papers..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>
        <div className="flex gap-1">
          {(['all', 'bookmarked'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-2.5 rounded-lg text-sm ${filter === f ? 'bg-primary-50 text-primary-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              {f === 'all' ? 'All' : 'Bookmarked'}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>
      ) : papers.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No papers found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {papers.map((paper) => (
            <div key={paper.id} className="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 hover:border-primary-300 transition-colors">
              <div className="flex items-start justify-between gap-3">
                <Link to={`/papers/${paper.id}`} className="flex-1 min-w-0">
                  <h3 className="text-xs sm:text-sm font-semibold text-gray-900 hover:text-primary-600 line-clamp-2">{paper.title}</h3>
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-3 mt-1 text-xs text-gray-500">
                    <span>{paper.source}</span>
                    {paper.published_date && <span>{new Date(paper.published_date).toLocaleDateString()}</span>}
                    <span className="hidden sm:inline-flex gap-1.5">
                      {paper.categories?.slice(0, 3).map((c) => (
                        <span key={c} className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">{c}</span>
                      ))}
                    </span>
                  </div>
                </Link>
                <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                  {paper.agi_score != null && (
                    <span className={`text-xs sm:text-sm font-bold ${paper.agi_score >= 70 ? 'text-green-600' : paper.agi_score >= 40 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {paper.agi_score.toFixed(1)}
                    </span>
                  )}
                  <span className="hidden sm:inline-flex">{paper.classification && <StatusBadge status={paper.classification} />}</span>
                  <button onClick={() => toggleBookmark(paper)} className="p-1.5">
                    <Bookmark className={`h-4 w-4 ${paper.is_bookmarked ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`} />
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
