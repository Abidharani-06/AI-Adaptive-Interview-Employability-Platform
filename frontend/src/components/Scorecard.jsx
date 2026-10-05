import React from 'react';

export default function Scorecard({
  title,
  value,
  score,
  unit = '%',
  subtitle,
  icon: Icon,
  trend,
  trendText,
  color = '#06b6d4',
  progress,
  className = '',
  onClick
}) {
  const displayVal = value !== undefined ? value : score;
  const isPositive = trend > 0;
  const isNegative = trend < 0;

  return (
    <div
      onClick={onClick}
      className={`card ${onClick ? 'card-interactive' : ''} ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
        <div>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {title}
          </span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', marginTop: '6px' }}>
            <span style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.03em' }}>
              {displayVal !== undefined ? displayVal : '--'}
            </span>
            {unit && typeof displayVal === 'number' && (
              <span style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-muted)' }}>
                {unit}
              </span>
            )}
          </div>

        </div>
        {Icon && (
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              backgroundColor: `${color}14`,
              color: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <Icon size={20} />
          </div>
        )}
      </div>

      {progress !== undefined && (
        <div style={{ marginBottom: '12px' }}>
          <div className="progress-track" style={{ height: '6px' }}>
            <div
              className="progress-fill"
              style={{
                width: `${Math.min(100, Math.max(0, progress))}%`,
                backgroundColor: color
              }}
            />
          </div>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
        {subtitle && (
          <span style={{ color: 'var(--text-secondary)' }}>
            {subtitle}
          </span>
        )}
        {trend !== undefined && (
          <span
            style={{
              fontWeight: 600,
              color: isPositive ? '#059669' : isNegative ? '#dc2626' : '#64748b',
              backgroundColor: isPositive ? '#ecfdf5' : isNegative ? '#fef2f2' : '#f1f5f9',
              padding: '2px 6px',
              borderRadius: '6px'
            }}
          >
            {isPositive ? `+${trend}%` : `${trend}%`} {trendText || ''}
          </span>
        )}
      </div>
    </div>
  );
}
