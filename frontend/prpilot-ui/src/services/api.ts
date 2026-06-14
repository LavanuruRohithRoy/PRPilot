import type {
  Analysis,
  DashboardSummary,
  GroundedQueryResponse,
  IngestResponse,
  PullRequest,
  Repository,
} from '../types/api';

// ─── Base URL ─────────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail ?? detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${BASE_URL}/health`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export async function getDashboard(): Promise<DashboardSummary> {
  return get<DashboardSummary>('/dashboard');
}

// ─── Repositories ─────────────────────────────────────────────────────────────

export async function listRepositories(): Promise<Repository[]> {
  return get<Repository[]>('/repositories');
}

export async function getRepositoryPullRequests(
  repoId: string,
): Promise<PullRequest[]> {
  return get<PullRequest[]>(`/repositories/${repoId}/pull-requests`);
}

// ─── Pull Requests ────────────────────────────────────────────────────────────

export async function listPullRequests(): Promise<PullRequest[]> {
  return get<PullRequest[]>('/pull-requests');
}

// ─── Analyses ─────────────────────────────────────────────────────────────────

export async function listAnalyses(): Promise<Analysis[]> {
  return get<Analysis[]>('/analyses');
}

export async function runAnalysis(prId: string): Promise<Analysis> {
  return post<Analysis>(`/analyses/run/${prId}`);
}

export async function getAnalysis(analysisId: string): Promise<Analysis> {
  return get<Analysis>(`/analyses/${analysisId}`);
}

// ─── Intelligence ─────────────────────────────────────────────────────────────

export async function ingestDatabase(): Promise<IngestResponse> {
  return post<IngestResponse>('/intelligence/ingest');
}

export async function queryIntelligence(
  query: string,
): Promise<GroundedQueryResponse> {
  const params = new URLSearchParams({ query });
  return get<GroundedQueryResponse>(`/intelligence/query?${params.toString()}`);
}
