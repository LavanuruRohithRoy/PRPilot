interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export function LoadingSpinner({ size = 'md', label }: LoadingSpinnerProps) {
  const sizeClass = size === 'sm' ? 'spinner--sm' : size === 'lg' ? 'spinner--lg' : '';

  if (label) {
    return (
      <div className="loading-center">
        <div className={`spinner ${sizeClass}`} />
        <span>{label}</span>
      </div>
    );
  }

  return <div className={`spinner ${sizeClass}`} />;
}
