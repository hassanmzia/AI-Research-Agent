export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface ResearchSession {
  id: string;
  user: number;
  title: string;
  research_objective: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_phase: string;
  max_papers: number;
  days_lookback: number;
  custom_keywords: string[];
  search_categories: string[];
  execution_plan: Record<string, any> | null;
  final_report: string;
  synthesis_data: Record<string, any> | null;
  total_papers_discovered: number;
  total_papers_evaluated: number;
  avg_agi_score: number | null;
  processing_time_seconds: number | null;
  errors: any[];
  celery_task_id: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  papers_count?: number;
  evaluations_count?: number;
  papers?: Paper[];
  agent_logs?: AgentLog[];
}

export interface Paper {
  id: string;
  session: string;
  external_id: string;
  title: string;
  abstract: string;
  authors: Array<{ name: string; affiliation?: string } | string>;
  source: string;
  url: string;
  doi: string;
  categories: string[];
  published_date: string | null;
  journal_ref: string;
  is_bookmarked: boolean;
  user_notes: string;
  agi_score?: number | null;
  classification?: string | null;
  evaluation?: AGIEvaluation;
}

export interface AGIEvaluation {
  id: string;
  paper: string;
  session: string;
  agi_score: number;
  classification: 'high' | 'medium' | 'low';
  novel_problem_solving: number;
  few_shot_learning: number;
  task_transfer: number;
  abstract_reasoning: number;
  contextual_adaptation: number;
  multi_rule_integration: number;
  generalization_efficiency: number;
  meta_learning: number;
  world_modeling: number;
  autonomous_goal_setting: number;
  parameter_reasoning: Record<string, string>;
  overall_assessment: string;
  key_innovations: string[];
  limitations: string[];
  confidence_level: string;
  score_breakdown: Record<string, any>;
  created_at: string;
}

export interface AgentLog {
  id: string;
  session: string;
  agent_role: string;
  level: string;
  message: string;
  metadata: Record<string, any>;
  phase: string;
  duration_ms: number | null;
  created_at: string;
}

export interface DashboardStats {
  total_sessions: number;
  total_papers: number;
  total_evaluations: number;
  avg_agi_score: number;
  high_agi_count: number;
  medium_agi_count: number;
  low_agi_count: number;
  recent_sessions: ResearchSession[];
  top_papers: Paper[];
  score_distribution: Array<{ range: string; count: number }>;
  papers_by_source: Array<{ source: string; count: number }>;
  sessions_over_time: Array<{ date: string; count: number }>;
}

export interface ResearchCollection {
  id: string;
  name: string;
  description: string;
  papers_count: number;
  is_public: boolean;
  tags: string[];
  created_at: string;
  papers?: Array<{
    id: string;
    title: string;
    authors: Array<{ name: string; affiliation?: string } | string>;
    source: string;
    url: string;
    categories: string[];
    published_date: string | null;
    is_bookmarked: boolean;
    agi_score?: number | null;
    classification?: string | null;
  }>;
}

export interface ScheduledResearch {
  id: string;
  name: string;
  research_objective: string;
  frequency: string;
  max_papers: number;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  total_runs: number;
  created_at: string;
}
