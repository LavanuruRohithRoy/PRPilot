import { scoreToGradient } from '../../lib/utils';

interface ScoreBarProps {
  score: number | null | undefined;
  showLabel?: boolean;
}

export function ScoreBar({ score, showLabel = true }: ScoreBarProps) {
  if (score === null || score === undefined) {
    return <span className="text-muted text-xs">—</span>;
  }

  const color = scoreToGradient(score);

  return (
    <div className="score-bar-wrap">
      <div className="score-bar">
        <div
          className="score-bar-fill"
          style={{ width: `${score}%`, background: color }}
        />
      </div>
      {showLabel && <span className="score-label" style={{ color }}>{score}</span>}
    </div>
  );
}
