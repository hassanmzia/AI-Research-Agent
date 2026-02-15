import React from 'react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import { AGIEvaluation } from '../types';

const PARAM_LABELS: Record<string, string> = {
  novel_problem_solving: 'Problem Solving',
  few_shot_learning: 'Few-Shot',
  task_transfer: 'Task Transfer',
  abstract_reasoning: 'Reasoning',
  contextual_adaptation: 'Adaptation',
  multi_rule_integration: 'Multi-Rule',
  generalization_efficiency: 'Generalization',
  meta_learning: 'Meta-Learning',
  world_modeling: 'World Model',
  autonomous_goal_setting: 'Goal Setting',
};

interface Props {
  evaluation: AGIEvaluation;
}

export default function AGIRadarChart({ evaluation }: Props) {
  const data = Object.entries(PARAM_LABELS).map(([key, label]) => ({
    parameter: label,
    score: (evaluation as any)[key] || 0,
    fullMark: 10,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="65%">
        <PolarGrid stroke="#e2e8f0" />
        <PolarAngleAxis
          dataKey="parameter"
          tick={{ fontSize: 9, fill: '#64748b' }}
        />
        <PolarRadiusAxis angle={90} domain={[0, 10]} tick={{ fontSize: 8 }} />
        <Radar
          name="AGI Score"
          dataKey="score"
          stroke="#2563eb"
          fill="#3b82f6"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
}
