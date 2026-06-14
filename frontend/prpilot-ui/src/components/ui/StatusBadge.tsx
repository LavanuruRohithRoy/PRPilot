import type { AnalysisStatus } from '../../types/api';
import { statusBgClass } from '../../lib/utils';

interface StatusBadgeProps {
  status: AnalysisStatus;
}

const icons: Record<AnalysisStatus, string> = {
  COMPLETED: '✓',
  RUNNING: '↻',
  PENDING: '◌',
  FAILED: '✗',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge ${statusBgClass(status)}`}>
      <span>{icons[status]}</span>
      {status.charAt(0) + status.slice(1).toLowerCase()}
    </span>
  );
}
