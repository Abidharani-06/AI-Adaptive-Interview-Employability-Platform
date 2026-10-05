import React from 'react';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontWeight: 600,
    borderRadius: '10px',
    transition: 'all 0.18s ease-in-out',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled || loading ? 0.65 : 1,
    border: 'none',
    outline: 'none',
  };

  const sizes = {
    sm: { padding: '6px 12px', fontSize: '13px' },
    md: { padding: '9px 18px', fontSize: '14px' },
    lg: { padding: '12px 24px', fontSize: '15px' },
  };

  const variants = {
    primary: {
      background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
      color: '#ffffff',
      boxShadow: '0 2px 4px rgba(79, 70, 229, 0.25)',
    },
    secondary: {
      background: '#f1f5f9',
      color: '#1e293b',
      border: '1px solid #e2e8f0',
    },
    outline: {
      background: 'transparent',
      color: '#4f46e5',
      border: '1.5px solid #4f46e5',
    },
    ghost: {
      background: 'transparent',
      color: '#475569',
    },
    danger: {
      background: '#ef4444',
      color: '#ffffff',
    },
    success: {
      background: '#10b981',
      color: '#ffffff',
    },
  };

  const currentStyle = {
    ...baseStyles,
    ...sizes[size],
    ...variants[variant],
  };

  return (
    <button
      type={type}
      style={currentStyle}
      disabled={disabled || loading}
      onClick={onClick}
      className={`btn ${className}`}
      {...props}
    >
      {loading ? (
        <span style={{ display: 'inline-block', width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.4)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon size={size === 'sm' ? 14 : 18} />}
          {children}
          {Icon && iconPosition === 'right' && <Icon size={size === 'sm' ? 14 : 18} />}
        </>
      )}
    </button>
  );
}
