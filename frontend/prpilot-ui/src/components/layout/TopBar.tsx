import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { healthCheck } from '../../services/api';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/repositories': 'Repositories',
  '/pull-requests': 'Pull Requests',
  '/analyses': 'Analyses',
  '/intelligence': 'Intelligence',
};

type HealthStatus = 'checking' | 'online' | 'offline';

export function TopBar() {
  const location = useLocation();
  const [health, setHealth] = useState<HealthStatus>('checking');

  useEffect(() => {
    let cancelled = false;
    setHealth('checking');
    healthCheck()
      .then(() => { if (!cancelled) setHealth('online'); })
      .catch(() => { if (!cancelled) setHealth('offline'); });
    return () => { cancelled = true; };
  }, []);

  const title = pageTitles[location.pathname] ?? 'PRPilot';
  const statusLabel =
    health === 'checking' ? 'Connecting…' :
    health === 'online' ? 'Backend online' :
    'Backend offline';

  return (
    <header className="app-topbar">
      <span className="topbar-title">{title}</span>

      <div className="topbar-status">
        <div className={`status-dot status-dot--${health}`} />
        <span style={{ fontSize: 13 }}>{statusLabel}</span>
      </div>

      <div
        style={{
          fontSize: 12,
          color: 'var(--text-muted)',
          borderLeft: '1px solid var(--border-subtle)',
          paddingLeft: 16,
          fontFamily: 'var(--font-mono)',
        }}
      >
        {new Date().toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
        })}
      </div>
    </header>
  );
}
