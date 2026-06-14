import type { RiskLevel } from '../../types/api';
import { riskBgClass } from '../../lib/utils';

interface RiskBadgeProps {
  level: RiskLevel | null | undefined;
}

const icons: Record<RiskLevel, string> = {
  HIGH: '⚠',
  MEDIUM: '◆',
  LOW: '✓',
};

export function RiskBadge({ level }: RiskBadgeProps) {
  if (!level) {
    return <span className="risk-badge risk-badge--none">—</span>;
  }

  return (
    <span className={`risk-badge ${riskBgClass(level)}`}>
      <span>{icons[level]}</span>
      {level}
    </span>
  );
}
