import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { getDashboard } from '../services/api';
import { useApi } from '../hooks/useApi';
import { RiskBadge } from '../components/ui/RiskBadge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { ScoreBar } from '../components/ui/ScoreBar';
import { formatDateTime, timeAgo, truncate } from '../lib/utils';

const RISK_COLORS = ['#ef4444', '#f59e0b', '#22c55e'];

interface MetricCardProps {
  icon: string;
  value: number;
  label: string;
  accent?: string;
  sub?: string;
}

function MetricCard({ icon, value, label, accent, sub }: MetricCardProps) {
  return (
    <div
      className="metric-card"
      style={{ '--card-accent-color': accent } as React.CSSProperties}
    >
      <div className="metric-card-icon">{icon}</div>
      <div className="metric-card-value">{value.toLocaleString()}</div>
      <div className="metric-card-label">{label}</div>
      {sub && <div className="metric-card-sub">{sub}</div>}
    </div>
  );
}

export function DashboardPage() {
  const { data, loading, error, refetch } = useApi(getDashboard);

  if (loading) return <LoadingSpinner size="lg" label="Loading dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!data) return null;

  const riskData = [
    { name: 'High', value: data.high_risk },
    { name: 'Medium', value: data.medium_risk },
    { name: 'Low', value: data.low_risk },
  ];

  const total = data.high_risk + data.medium_risk + data.low_risk;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">System Overview</h1>
        <p className="page-subtitle">Real-time aggregation of PRPilot data from all tracked repositories</p>
      </div>

      {/* Metric Cards */}
      <div className="metric-grid">
        <MetricCard icon="◫" value={data.repositories} label="Repositories" accent="#6366f1" />
        <MetricCard icon="⌥" value={data.pull_requests} label="Pull Requests" accent="#8b5cf6" />
        <MetricCard icon="◈" value={data.analyses} label="Analyses Run" accent="#06b6d4" />
        <MetricCard icon="⚠" value={data.high_risk} label="High Risk" accent="#ef4444" sub="PRs flagged high risk" />
        <MetricCard icon="◆" value={data.medium_risk} label="Medium Risk" accent="#f59e0b" />
        <MetricCard icon="✓" value={data.low_risk} label="Low Risk" accent="#22c55e" />
      </div>

      {/* Charts + Recent Analyses */}
      <div className="two-col-grid">
        {/* Risk Distribution Donut */}
        <div className="card">
          <div className="section-header">
            <span className="section-title">Risk Distribution</span>
            <span className="text-muted text-sm">{total} analyses</span>
          </div>

          {total === 0 ? (
            <EmptyState icon="📊" title="No analyses yet" subtitle="Run analysis on pull requests to see risk distribution." />
          ) : (
            <div className="donut-chart-wrapper">
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={76}
                    paddingAngle={3}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {riskData.map((_, index) => (
                      <Cell key={index} fill={RISK_COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-card)',
                      borderRadius: 8,
                      fontSize: 12,
                      color: 'var(--text-primary)',
                    }}
                    formatter={(val) => [`${val ?? 0}`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>

              <div className="donut-legend">
                {riskData.map((d, i) => (
                  <div key={d.name} className="donut-legend-item">
                    <div className="donut-legend-dot" style={{ background: RISK_COLORS[i] }} />
                    <span className="donut-legend-label">{d.name} Risk</span>
                    <span className="donut-legend-count">{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="card">
          <div className="section-header">
            <span className="section-title">Quick Stats</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { label: 'Analysis Coverage', value: data.pull_requests > 0 ? Math.round((data.analyses / data.pull_requests) * 100) : 0, max: 100, unit: '%' },
              { label: 'High Risk Ratio', value: total > 0 ? Math.round((data.high_risk / total) * 100) : 0, max: 100, unit: '%' },
              { label: 'Active Repos', value: data.repositories, max: Math.max(data.repositories, 1), unit: '' },
            ].map(({ label, value, unit }) => (
              <div key={label}>
                <div className="flex-row-between mb-4">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{label}</span>
                  <span className="text-mono text-sm" style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                    {value}{unit}
                  </span>
                </div>
                <ScoreBar score={value} showLabel={false} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div style={{ marginTop: 24 }}>
        <div className="section-header mb-16">
          <span className="section-title">Recent Analyses</span>
          <span className="text-muted text-sm">{data.recent_analyses.length} shown</span>
        </div>

        {data.recent_analyses.length === 0 ? (
          <div className="card">
            <EmptyState
              icon="🔍"
              title="No analyses yet"
              subtitle="Sync repositories and trigger analysis runs to see results here."
            />
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Pull Request</th>
                  <th>Repository</th>
                  <th>Status</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Ran</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_analyses.map((analysis) => (
                  <tr key={analysis.id}>
                    <td>
                      <span className="td-primary">#{analysis.pr_number}</span>
                      <span className="text-muted" style={{ marginLeft: 8, fontSize: 12 }}>
                        {truncate(analysis.pr_title, 48)}
                      </span>
                    </td>
                    <td>
                      <code className="td-mono">{analysis.repository_name}</code>
                    </td>
                    <td><StatusBadge status={analysis.status} /></td>
                    <td><RiskBadge level={analysis.risk_level} /></td>
                    <td>
                      <div style={{ minWidth: 100 }}>
                        <ScoreBar score={analysis.risk_score} />
                      </div>
                    </td>
                    <td>
                      <span className="text-muted text-sm" title={formatDateTime(analysis.created_at)}>
                        {timeAgo(analysis.created_at)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
