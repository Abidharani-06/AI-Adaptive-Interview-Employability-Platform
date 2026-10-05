import React from 'react';

export default function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = ''
}) {
  const variantStyles = {
    primary: { background: '#eef2ff', color: '#4f46e5', border: '1px solid #c7d2fe' },
    success: { background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0' },
    warning: { background: '#fffbeb', color: '#92400e', border: '1px solid #fde68a' },
    danger: { background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca' },
    neutral: { background: '#f8fafc', color: '#475569', border: '1px solid #e2e8f0' },
    purple: { background: '#f5f3ff', color: '#6d28d9', border: '1px solid #ddd6fe' },
    cyan: { background: '#ecfeff', color: '#0e7490', border: '1px solid #a5f3fc' },
  };

  const readinessVariants = {
    'Highly Ready': 'success',
    'Ready': 'primary',
    'Developing': 'warning',
    'Needs Improvement': 'danger',
    'Early Stage': 'neutral',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'neutral'
  };

  const selectedVariant = readinessVariants[children] || variant;
  const currentVariant = variantStyles[selectedVariant] || variantStyles.neutral;

  const sizeStyles = {
    sm: { padding: '2px 8px', fontSize: '11px' },
    md: { padding: '4px 10px', fontSize: '12px' },
    lg: { padding: '6px 14px', fontSize: '13px' }
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        fontWeight: 600,
        borderRadius: '9999px',
        lineHeight: 1.2,
        ...sizeStyles[size],
        ...currentVariant
      }}
      className={`badge ${className}`}
    >
      {dot && (
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: 'currentColor'
          }}
        />
      )}
      {children}
    </span>
  );
}
