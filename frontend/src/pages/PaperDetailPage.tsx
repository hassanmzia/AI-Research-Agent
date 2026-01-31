import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { papersAPI, collectionsAPI } from '../services/api';
import { Paper, ResearchCollection } from '../types';
import StatusBadge from '../components/StatusBadge';
import ScoreGauge from '../components/ScoreGauge';
import AGIRadarChart from '../components/AGIRadarChart';
import { ExternalLink, Bookmark, Save, FolderPlus, Check, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PaperDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [collections, setCollections] = useState<ResearchCollection[]>([]);
  const [showCollectionPicker, setShowCollectionPicker] = useState(false);
  const [addingTo, setAddingTo] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    papersAPI.get(id)
      .then((res) => {
        setPaper(res.data);
        setNotes(res.data.user_notes || '');
      })
      .finally(() => setLoading(false));
  }, [id]);

  const saveNotes = async () => {
    if (!id) return;
    try {
      await papersAPI.notes(id, notes);
      toast.success('Notes saved');
    } catch {
      toast.error('Failed to save notes');
    }
  };

  const toggleBookmark = async () => {
    if (!id || !paper) return;
    const res = await papersAPI.bookmark(id);
    setPaper({ ...paper, is_bookmarked: res.data.is_bookmarked });
  };

  const openCollectionPicker = async () => {
    try {
      const res = await collectionsAPI.list();
      setCollections(res.data.results || res.data);
      setShowCollectionPicker(true);
    } catch {
      toast.error('Failed to load collections');
    }
  };

  const addToCollection = async (collectionId: string) => {
    if (!id) return;
    setAddingTo(collectionId);
    try {
      await collectionsAPI.addPaper(collectionId, id);
      toast.success('Paper added to collection');
      setShowCollectionPicker(false);
    } catch {
      toast.error('Failed to add paper to collection');
    } finally {
      setAddingTo(null);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" /></div>;
  }

  if (!paper) return <p>Paper not found</p>;

  const evaluation = paper.evaluation;
  const authorNames = paper.authors.map((a) => (typeof a === 'string' ? a : a.name));

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <div className="flex items-start justify-between gap-4">
          <h1 className="text-xl font-bold text-gray-900">{paper.title}</h1>
          <div className="flex gap-2 shrink-0">
            <div className="relative">
              <button
                onClick={openCollectionPicker}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                title="Add to collection"
              >
                <FolderPlus className="h-5 w-5 text-gray-400" />
              </button>

              {/* Collection Picker Dropdown */}
              {showCollectionPicker && (
                <div className="absolute right-0 top-full mt-1 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="flex items-center justify-between px-3 py-2 border-b border-gray-100">
                    <span className="text-sm font-medium text-gray-700">Add to Collection</span>
                    <button onClick={() => setShowCollectionPicker(false)} className="p-0.5 hover:bg-gray-100 rounded">
                      <X className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                  <div className="max-h-48 overflow-y-auto">
                    {collections.length === 0 ? (
                      <p className="px-3 py-4 text-sm text-gray-500 text-center">No collections yet. Create one first.</p>
                    ) : (
                      collections.map((col) => (
                        <button
                          key={col.id}
                          onClick={() => addToCollection(col.id)}
                          disabled={addingTo === col.id}
                          className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center justify-between text-sm"
                        >
                          <div>
                            <p className="font-medium text-gray-900">{col.name}</p>
                            <p className="text-xs text-gray-500">{col.papers_count} papers</p>
                          </div>
                          {addingTo === col.id ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600" />
                          ) : (
                            <Check className="h-4 w-4 text-gray-300" />
                          )}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
            <button onClick={toggleBookmark} className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Bookmark className={`h-5 w-5 ${paper.is_bookmarked ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`} />
            </button>
            {paper.url && (
              <a href={paper.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                <ExternalLink className="h-4 w-4" /> View Paper
              </a>
            )}
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-2">{authorNames.join(', ')}</p>
        <div className="flex items-center gap-3 mt-2">
          <span className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">{paper.source}</span>
          {paper.published_date && (
            <span className="text-xs text-gray-500">{new Date(paper.published_date).toLocaleDateString()}</span>
          )}
          {paper.categories?.map((c) => (
            <span key={c} className="px-2 py-0.5 bg-blue-50 rounded text-xs text-blue-600">{c}</span>
          ))}
        </div>
      </div>

      {/* Abstract */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Abstract</h3>
        <p className="text-sm text-gray-700 leading-relaxed">{paper.abstract}</p>
      </div>

      {/* AGI Evaluation */}
      {evaluation && (
        <>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">AGI Evaluation</h3>
              <div className="flex items-center gap-3">
                <ScoreGauge score={evaluation.agi_score} size="lg" />
                <div>
                  <StatusBadge status={evaluation.classification} />
                  <p className="text-xs text-gray-500 mt-1">Confidence: {evaluation.confidence_level}</p>
                </div>
              </div>
            </div>

            {/* Radar Chart */}
            <AGIRadarChart evaluation={evaluation} />

            {/* Assessment */}
            {evaluation.overall_assessment && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-gray-600 mb-1">Overall Assessment</h4>
                <p className="text-sm text-gray-700">{evaluation.overall_assessment}</p>
              </div>
            )}

            {/* Innovations & Limitations */}
            <div className="grid grid-cols-2 gap-4 mt-4">
              {evaluation.key_innovations.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-green-700 mb-1">Key Innovations</h4>
                  <ul className="space-y-1">
                    {evaluation.key_innovations.map((i, idx) => (
                      <li key={idx} className="text-xs text-gray-600 flex items-start gap-1">
                        <span className="text-green-500 mt-0.5">+</span> {i}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {evaluation.limitations.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-red-700 mb-1">Limitations</h4>
                  <ul className="space-y-1">
                    {evaluation.limitations.map((l, idx) => (
                      <li key={idx} className="text-xs text-gray-600 flex items-start gap-1">
                        <span className="text-red-500 mt-0.5">-</span> {l}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Parameter Scores Table */}
            <div className="mt-4">
              <h4 className="text-xs font-medium text-gray-600 mb-2">Parameter Scores</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  ['Novel Problem Solving', evaluation.novel_problem_solving, '15%'],
                  ['Few-Shot Learning', evaluation.few_shot_learning, '15%'],
                  ['Task Transfer', evaluation.task_transfer, '15%'],
                  ['Abstract Reasoning', evaluation.abstract_reasoning, '12%'],
                  ['Contextual Adaptation', evaluation.contextual_adaptation, '10%'],
                  ['Multi-Rule Integration', evaluation.multi_rule_integration, '10%'],
                  ['Generalization Efficiency', evaluation.generalization_efficiency, '8%'],
                  ['Meta-Learning', evaluation.meta_learning, '8%'],
                  ['World Modeling', evaluation.world_modeling, '4%'],
                  ['Autonomous Goal Setting', evaluation.autonomous_goal_setting, '3%'],
                ].map(([label, score, weight]) => (
                  <div key={label as string} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-xs text-gray-600">{label} ({weight})</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${(score as number) >= 7 ? 'bg-green-400' : (score as number) >= 4 ? 'bg-yellow-400' : 'bg-red-400'}`}
                          style={{ width: `${(score as number) * 10}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold text-gray-700 w-4 text-right">{score as number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* User Notes */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Your Notes</h3>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
          placeholder="Add your notes about this paper..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none resize-none"
        />
        <button
          onClick={saveNotes}
          className="mt-2 flex items-center gap-1 px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700"
        >
          <Save className="h-3 w-3" /> Save Notes
        </button>
      </div>
    </div>
  );
}
