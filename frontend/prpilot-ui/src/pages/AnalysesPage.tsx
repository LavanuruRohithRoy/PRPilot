import { useState } from 'react';
import { listAnalyses } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { RiskBadge } from '../components/ui/RiskBadge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ScoreBar } from '../components/ui/ScoreBar';
import { timeAgo, formatDateTime } from '../lib/utils';
import type { Analysis } from '../types/api';

function AnalysisDetailPanel({
  analysis,
  onClose,
}: {
  analysis: Analysis;
  onClose: () => void;
}) {
  return (
    <>
      <div className="panel-overlay" onClick={onClose} />
      <div className="analysis-detail-panel">
        <button className="panel-close" onClick={onClose} aria-label="Close panel">
          ✕
        </button>

        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
            Analysis ID
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
            {analysis.id}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <StatusBadge status={analysis.status} />
          <RiskBadge level={analysis.risk_level} />
        </div>

        {analysis.risk_score !== null && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Risk Score</div>
            <ScoreBar score={analysis.risk_score} />
          </div>
        )}

        {analysis.summary && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Summary</div>
            <div className="summary-text">{analysis.summary}</div>
          </div>
        )}

        {analysis.findings && analysis.findings.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
              Findings ({analysis.findings.length})
            </div>
            <div className="finding-list">
              {analysis.findings.map((finding, i) => (
                <div key={i} className="finding-item">
                  <span className="finding-item-bullet">◆</span>
                  <span>{finding}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 16 }}>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Created</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            {formatDateTime(analysis.created_at)}
          </div>
        </div>
      </div>
    </>
  );
}

export function AnalysesPage() {
  const { data, loading, error, refetch } = useApi(listAnalyses);
  const [selected, setSelected] = useState<Analysis | null>(null);

  if (loading) return <LoadingSpinner size="lg" label="Loading analyses…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Analysis History</h1>
        <p className="page-subtitle">
          Rule-based risk analysis results for all tracked pull requests
        </p>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState
          icon="◈"
          title="No analyses run yet"
          subtitle="Trigger analysis from the API using POST /api/v1/analyses/run/{pr_id}."
        />
      ) : (
        <>
          <div style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: 13 }}>
            {data.length} analysis record{data.length !== 1 ? 's' : ''}
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>PR ID</th>
                  <th>Status</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Findings</th>
                  <th>Ran</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.map((analysis) => (
                  <tr key={analysis.id} style={{ cursor: 'pointer' }} onClick={() => setSelected(analysis)}>
                    <td>
                      <code className="td-mono" style={{ fontSize: 11 }}>
                        {analysis.pull_request_id.slice(0, 8)}…
                      </code>
                    </td>
                    <td><StatusBadge status={analysis.status} /></td>
                    <td><RiskBadge level={analysis.risk_level} /></td>
                    <td>
                      <div style={{ minWidth: 100 }}>
                        <ScoreBar score={analysis.risk_score} />
                      </div>
                    </td>
                    <td>
                      <span
                        style={{
                          background: 'var(--bg-surface)',
                          borderRadius: 12,
                          padding: '2px 8px',
                          fontSize: 11,
                          fontFamily: 'var(--font-mono)',
                          color: 'var(--text-muted)',
                        }}
                      >
                        {analysis.findings?.length ?? 0}
                      </span>
                    </td>
                    <td>
                      <span className="text-muted text-sm" title={formatDateTime(analysis.created_at)}>
                        {timeAgo(analysis.created_at)}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelected(analysis);
                        }}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {selected && (
        <AnalysisDetailPanel analysis={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
