import { listPullRequests } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { formatDate, timeAgo, truncate } from '../lib/utils';
import type { PullRequestStatus } from '../types/api';
import { prStatusBgClass } from '../lib/utils';

function PRStatusBadge({ status }: { status: PullRequestStatus }) {
  const icons: Record<PullRequestStatus, string> = {
    OPEN: '●',
    MERGED: '⤷',
    CLOSED: '✗',
  };
  return (
    <span className={`pr-status ${prStatusBgClass(status)}`}>
      <span>{icons[status]}</span>
      {status.charAt(0) + status.slice(1).toLowerCase()}
    </span>
  );
}

export function PullRequestsPage() {
  const { data, loading, error, refetch } = useApi(listPullRequests);

  if (loading) return <LoadingSpinner size="lg" label="Loading pull requests…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Pull Requests</h1>
        <p className="page-subtitle">All pull requests synced from registered repositories</p>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState
          icon="⌥"
          title="No pull requests found"
          subtitle="Configure GitHub webhooks and push events to start syncing pull requests."
        />
      ) : (
        <>
          <div style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: 13 }}>
            {data.length} pull request{data.length !== 1 ? 's' : ''} tracked
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Status</th>
                  <th>Opened</th>
                  <th>Closed</th>
                </tr>
              </thead>
              <tbody>
                {data.map((pr) => (
                  <tr key={pr.id}>
                    <td>
                      <span className="td-primary td-mono">#{pr.pr_number}</span>
                    </td>
                    <td>
                      <span className="td-primary" title={pr.title}>
                        {truncate(pr.title, 60)}
                      </span>
                    </td>
                    <td>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6,
                          fontSize: 13,
                          color: 'var(--text-secondary)',
                        }}
                      >
                        <span
                          style={{
                            width: 22,
                            height: 22,
                            borderRadius: '50%',
                            background: 'var(--accent-primary)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 10,
                            fontWeight: 700,
                            color: '#fff',
                            flexShrink: 0,
                          }}
                        >
                          {pr.author.charAt(0).toUpperCase()}
                        </span>
                        {pr.author}
                      </span>
                    </td>
                    <td><PRStatusBadge status={pr.status} /></td>
                    <td>
                      <span className="text-sm text-muted" title={new Date(pr.opened_at).toLocaleString()}>
                        {formatDate(pr.opened_at)}
                      </span>
                    </td>
                    <td>
                      {pr.closed_at ? (
                        <span className="text-sm text-muted">
                          {timeAgo(pr.closed_at)}
                        </span>
                      ) : (
                        <span className="text-muted text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
