import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { DashboardStats } from '../types';
import StatusBadge from '../components/StatusBadge';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';
import {
  FileText, BookOpen, TrendingUp, Award, Search, ArrowRight,
} from 'lucide-react';

const PIE_COLORS = ['#22c55e', '#eab308', '#ef4444'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.stats()
      .then((res) => setStats(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>;
  }

  if (!stats) {
    return (
      <div className="text-center py-20">
        <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-700">Welcome to AI Research Agent</h2>
        <p className="text-gray-500 mt-2 mb-6">Start your first research session to see analytics here.</p>
        <Link to="/research/new" className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
          <Search className="h-5 w-5" /> Start Research <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  const pieData = [
    { name: 'High AGI', value: stats.high_agi_count },
    { name: 'Medium AGI', value: stats.medium_agi_count },
    { name: 'Low AGI', value: stats.low_agi_count },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Overview of your AI research activity</p>
        </div>
        <Link to="/research/new" className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 w-full sm:w-auto">
          <Search className="h-4 w-4" /> New Research
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[
          { label: 'Sessions', value: stats.total_sessions, icon: FileText, color: 'text-blue-600 bg-blue-50' },
          { label: 'Papers', value: stats.total_papers, icon: BookOpen, color: 'text-green-600 bg-green-50' },
          { label: 'Evaluations', value: stats.total_evaluations, icon: TrendingUp, color: 'text-purple-600 bg-purple-50' },
          { label: 'Avg AGI Score', value: stats.avg_agi_score, icon: Award, color: 'text-amber-600 bg-amber-50' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className={`p-1.5 sm:p-2 rounded-lg ${color}`}><Icon className="h-4 w-4 sm:h-5 sm:w-5" /></div>
              <div className="min-w-0">
                <p className="text-xs sm:text-sm text-gray-500 truncate">{label}</p>
                <p className="text-lg sm:text-2xl font-bold text-gray-900">{typeof value === 'number' ? value.toLocaleString() : value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Score Distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 sm:mb-4">AGI Score Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stats.score_distribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="range" fontSize={10} tick={{ fontSize: 10 }} />
              <YAxis fontSize={10} tick={{ fontSize: 10 }} width={30} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Classification Pie */}
        <div className="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 sm:mb-4">AGI Classification Breakdown</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={{ fontSize: 11 }}>
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-16">No evaluations yet</p>
          )}
        </div>
      </div>

      {/* Sessions Over Time */}
      {stats.sessions_over_time.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Research Activity (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={stats.sessions_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Papers */}
      {stats.top_papers.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 sm:mb-4">Top Papers by AGI Score</h3>
          <div className="space-y-2 sm:space-y-3">
            {stats.top_papers.slice(0, 5).map((paper) => (
              <Link key={paper.id} to={`/papers/${paper.id}`} className="flex items-center justify-between p-2 sm:p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex-1 min-w-0 mr-3">
                  <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{paper.title}</p>
                  <p className="text-xs text-gray-500">{paper.source}</p>
                </div>
                <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                  {paper.agi_score != null && (
                    <span className={`text-xs sm:text-sm font-bold ${paper.agi_score >= 70 ? 'text-green-600' : paper.agi_score >= 40 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {paper.agi_score.toFixed(1)}
                    </span>
                  )}
                  <span className="hidden sm:inline-flex">{paper.classification && <StatusBadge status={paper.classification} />}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Recent Sessions */}
      {stats.recent_sessions.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-700">Recent Sessions</h3>
            <Link to="/sessions" className="text-sm text-primary-600 hover:underline">View All</Link>
          </div>
          <div className="space-y-3">
            {stats.recent_sessions.map((session) => (
              <Link key={session.id} to={`/sessions/${session.id}`} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex-1 min-w-0 mr-4">
                  <p className="text-sm font-medium text-gray-900 truncate">{session.title || session.research_objective}</p>
                  <p className="text-xs text-gray-500">{new Date(session.created_at).toLocaleDateString()}</p>
                </div>
                <StatusBadge status={session.status} />
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
