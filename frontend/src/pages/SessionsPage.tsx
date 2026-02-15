import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { sessionsAPI } from '../services/api';
import { ResearchSession } from '../types';
import StatusBadge from '../components/StatusBadge';
import { FileText, ChevronRight, Search } from 'lucide-react';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    sessionsAPI.list()
      .then((res) => setSessions(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>;
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Research Sessions</h1>
          <p className="text-sm text-gray-500">{sessions.length} sessions total</p>
        </div>
        <Link to="/research/new" className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 w-full sm:w-auto">
          <Search className="h-4 w-4" /> New Research
        </Link>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No research sessions yet</p>
          <Link to="/research/new" className="text-primary-600 hover:underline text-sm mt-2 inline-block">Start your first research</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <Link
              key={session.id}
              to={`/sessions/${session.id}`}
              className="block bg-white rounded-xl border border-gray-200 p-3 sm:p-5 hover:border-primary-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0 mr-3">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <h3 className="text-xs sm:text-sm font-semibold text-gray-900 truncate max-w-[calc(100%-80px)]">
                      {session.title || session.research_objective}
                    </h3>
                    <StatusBadge status={session.status} />
                  </div>
                  {session.title && (
                    <p className="text-xs text-gray-500 truncate">{session.research_objective}</p>
                  )}
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-gray-500">
                    <span>{new Date(session.created_at).toLocaleDateString()}</span>
                    <span>Papers: {session.total_papers_discovered}</span>
                    <span>Evaluated: {session.total_papers_evaluated}</span>
                    {session.avg_agi_score != null && (
                      <span className="font-medium text-primary-600">
                        Avg: {session.avg_agi_score.toFixed(1)}
                      </span>
                    )}
                    {session.processing_time_seconds != null && (
                      <span>{session.processing_time_seconds.toFixed(0)}s</span>
                    )}
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400 shrink-0" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
