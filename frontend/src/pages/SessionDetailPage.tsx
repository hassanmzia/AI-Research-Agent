import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { sessionsAPI } from '../services/api';
import { ResearchSession, AgentLog } from '../types';
import StatusBadge from '../components/StatusBadge';
import wsService from '../services/websocket';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import {
  FileText, Download, XCircle, RefreshCw, Clock, BookOpen,
  Activity, ChevronDown, ChevronUp,
} from 'lucide-react';

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReport, setShowReport] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const fetchSession = () => {
    if (!id) return;
    sessionsAPI.get(id)
      .then((res) => setSession(res.data))
      .finally(() => setLoading(false));
    sessionsAPI.logs(id)
      .then((res) => setLogs(res.data.results || res.data))
      .catch(() => {});
  };

  useEffect(() => {
    fetchSession();

    // Subscribe to real-time updates
    if (id) {
      wsService.subscribeSession(id);
      const unsub = wsService.on('session_update', (data) => {
        if (data.session_id === id) {
          fetchSession();
        }
      });
      return () => {
        wsService.unsubscribeSession(id!);
        unsub();
      };
    }
  }, [id]);

  const handleCancel = async () => {
    if (!id) return;
    try {
      await sessionsAPI.cancel(id);
      toast.success('Session cancelled');
      fetchSession();
    } catch {
      toast.error('Failed to cancel');
    }
  };

  const handleExport = async (format: string) => {
    if (!id) return;
    try {
      const res = await sessionsAPI.export(id, format);
      // Create download
      const blob = new Blob([res.data.file_content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = res.data.file_name;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch {
      toast.error('Export failed');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>;
  }

  if (!session) {
    return <p className="text-gray-500">Session not found</p>;
  }

  const isRunning = session.status === 'running';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{session.title || 'Research Session'}</h1>
          <p className="text-gray-500 mt-1">{session.research_objective}</p>
          <div className="flex items-center gap-3 mt-2">
            <StatusBadge status={session.status} />
            <span className="text-xs text-gray-500">Phase: {session.current_phase}</span>
            <span className="text-xs text-gray-500">{new Date(session.created_at).toLocaleString()}</span>
          </div>
        </div>
        <div className="flex gap-2">
          {isRunning && (
            <>
              <button onClick={fetchSession} className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <RefreshCw className="h-4 w-4" />
              </button>
              <button onClick={handleCancel} className="flex items-center gap-1 px-3 py-2 bg-red-50 text-red-600 rounded-lg text-sm hover:bg-red-100">
                <XCircle className="h-4 w-4" /> Cancel
              </button>
            </>
          )}
          {session.status === 'completed' && (
            <div className="flex gap-1">
              {['markdown', 'json', 'csv'].map((fmt) => (
                <button key={fmt} onClick={() => handleExport(fmt)} className="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                  <Download className="h-3 w-3" /> {fmt.toUpperCase()}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar for Running */}
      {isRunning && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600" />
            <span className="text-sm font-medium text-gray-700">Pipeline Running - {session.current_phase}</span>
          </div>
          <div className="flex gap-1">
            {['initialization', 'planning', 'discovery', 'evaluation', 'synthesis', 'completion'].map((phase) => {
              const phases = ['initialization', 'planning', 'discovery', 'evaluation', 'synthesis', 'completion'];
              const currentIdx = phases.indexOf(session.current_phase);
              const phaseIdx = phases.indexOf(phase);
              const isDone = phaseIdx < currentIdx;
              const isCurrent = phaseIdx === currentIdx;
              return (
                <div key={phase} className={`flex-1 h-2 rounded-full ${isDone ? 'bg-green-400' : isCurrent ? 'bg-primary-400 animate-pulse' : 'bg-gray-200'}`} />
              );
            })}
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 mb-1"><BookOpen className="h-4 w-4" /><span className="text-xs">Papers Found</span></div>
          <p className="text-2xl font-bold">{session.total_papers_discovered}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 mb-1"><Activity className="h-4 w-4" /><span className="text-xs">Evaluated</span></div>
          <p className="text-2xl font-bold">{session.total_papers_evaluated}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 mb-1"><FileText className="h-4 w-4" /><span className="text-xs">Avg AGI Score</span></div>
          <p className="text-2xl font-bold">{session.avg_agi_score?.toFixed(1) ?? '--'}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-gray-500 mb-1"><Clock className="h-4 w-4" /><span className="text-xs">Duration</span></div>
          <p className="text-2xl font-bold">{session.processing_time_seconds ? `${session.processing_time_seconds.toFixed(0)}s` : '--'}</p>
        </div>
      </div>

      {/* Papers List */}
      {session.papers && session.papers.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Discovered Papers</h3>
          <div className="space-y-2">
            {session.papers.map((paper) => (
              <Link key={paper.id} to={`/papers/${paper.id}`} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                <div className="flex-1 min-w-0 mr-4">
                  <p className="text-sm font-medium text-gray-900 truncate">{paper.title}</p>
                  <p className="text-xs text-gray-500">{paper.source}</p>
                </div>
                <div className="flex items-center gap-2">
                  {paper.agi_score != null && (
                    <span className={`text-sm font-bold ${paper.agi_score >= 70 ? 'text-green-600' : paper.agi_score >= 40 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {paper.agi_score.toFixed(1)}
                    </span>
                  )}
                  {paper.classification && <StatusBadge status={paper.classification} />}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Final Report */}
      {session.final_report && (
        <div className="bg-white rounded-xl border border-gray-200">
          <button
            onClick={() => setShowReport(!showReport)}
            className="w-full flex items-center justify-between p-5"
          >
            <h3 className="text-sm font-semibold text-gray-700">Final Report</h3>
            {showReport ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
          </button>
          {showReport && (
            <div className="px-5 pb-5 prose prose-sm max-w-none">
              <ReactMarkdown>{session.final_report}</ReactMarkdown>
            </div>
          )}
        </div>
      )}

      {/* Agent Logs */}
      {logs.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="w-full flex items-center justify-between p-5"
          >
            <h3 className="text-sm font-semibold text-gray-700">Agent Activity Logs ({logs.length})</h3>
            {showLogs ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
          </button>
          {showLogs && (
            <div className="px-5 pb-5 max-h-96 overflow-y-auto space-y-1">
              {logs.map((log) => (
                <div key={log.id} className="flex items-start gap-3 text-xs py-1.5 border-b border-gray-100">
                  <span className="text-gray-400 w-20 shrink-0">{new Date(log.created_at).toLocaleTimeString()}</span>
                  <StatusBadge status={log.level} />
                  <span className="font-mono text-gray-600">[{log.agent_role}]</span>
                  <span className="text-gray-800">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
