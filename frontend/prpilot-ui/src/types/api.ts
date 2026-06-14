// ─── Enums ────────────────────────────────────────────────────────────────────

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type AnalysisStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
export type PullRequestStatus = 'OPEN' | 'CLOSED' | 'MERGED';

// ─── Repository ───────────────────────────────────────────────────────────────

export interface Repository {
  id: string;
  owner: string;
  name: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ─── Pull Request ─────────────────────────────────────────────────────────────

export interface PullRequest {
  id: string;
  repository_id: string;
  pr_number: number;
  title: string;
  author: string;
  status: PullRequestStatus;
  opened_at: string;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
}

// ─── Analysis ─────────────────────────────────────────────────────────────────

export interface Analysis {
  id: string;
  pull_request_id: string;
  status: AnalysisStatus;
  summary: string | null;
  risk_score: number | null;
  risk_level: RiskLevel | null;
  findings: string[] | null;
  created_at: string;
  updated_at: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface DashboardRecentAnalysis {
  id: string;
  pull_request_id: string;
  pr_title: string;
  pr_number: number;
  repository_name: string;
  risk_score: number | null;
  risk_level: RiskLevel | null;
  status: AnalysisStatus;
  created_at: string;
}

export interface DashboardSummary {
  repositories: number;
  pull_requests: number;
  analyses: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  recent_analyses: DashboardRecentAnalysis[];
}

// ─── Intelligence ─────────────────────────────────────────────────────────────

export interface GroundedCitation {
  id: string;
  title: string;
  url: string | null;
  score: number | null;
  reference: string | null;
}

export interface GroundedQueryResponse {
  query: string;
  answer: string;
  citations: GroundedCitation[];
}

export interface IngestResponse {
  repositories: number;
  pull_requests: number;
  analyses: number;
  status: string;
}

// ─── API Error ────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
