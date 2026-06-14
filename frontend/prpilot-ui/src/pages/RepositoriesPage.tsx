import { listRepositories } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { formatDate } from '../lib/utils';

export function RepositoriesPage() {
  const { data, loading, error, refetch } = useApi(listRepositories);

  if (loading) return <LoadingSpinner size="lg" label="Loading repositories…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Repositories</h1>
        <p className="page-subtitle">
          All GitHub repositories registered with PRPilot for analysis tracking
        </p>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState
          icon="◫"
          title="No repositories registered"
          subtitle="Use the GitHub webhook integration to register repositories and start tracking pull requests."
        />
      ) : (
        <>
          <div style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: 13 }}>
            {data.length} repository{data.length !== 1 ? 'ies' : 'y'} registered
          </div>
          <div className="repo-grid">
            {data.map((repo) => (
              <div key={repo.id} className="repo-card">
                <div className="repo-card-header">
                  <div>
                    <div className="repo-card-name">{repo.name}</div>
                    <div className="repo-card-owner">@{repo.owner}</div>
                  </div>
                  <div className="repo-card-icon">◫</div>
                </div>

                <div
                  style={{
                    fontSize: 12,
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    padding: '8px 10px',
                    background: 'var(--bg-surface)',
                    borderRadius: 6,
                    marginBottom: 12,
                    wordBreak: 'break-all',
                  }}
                >
                  {repo.full_name}
                </div>

                <div className="flex-row-between" style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  <span>
                    {repo.is_active ? (
                      <span>
                        <span className="repo-active-dot" />
                        Active
                      </span>
                    ) : (
                      <span style={{ color: 'var(--color-risk-high)' }}>● Inactive</span>
                    )}
                  </span>
                  <span>Added {formatDate(repo.created_at)}</span>
                </div>

                <div
                  style={{
                    marginTop: 12,
                    paddingTop: 12,
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: 11,
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  ID: {repo.id.slice(0, 8)}…
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
