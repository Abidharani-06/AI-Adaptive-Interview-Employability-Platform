import React from 'react';
import { ArrowRight, Clock, HelpCircle, Sparkles } from 'lucide-react';
import Badge from './Badge';

export default function InterviewCard({
  title,
  subtitle,
  category,
  questionCount = 5,
  duration = '15 mins',
  difficulty = 'Adaptive',
  icon: Icon,
  color = '#4f46e5',
  onSelect,
  selected = false
}) {
  return (
    <div
      onClick={onSelect}
      className={`card card-interactive`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        cursor: 'pointer',
        border: selected ? `2px solid ${color}` : '1px solid var(--border-light)',
        backgroundColor: selected ? `${color}06` : 'var(--bg-surface)',
        position: 'relative'
      }}
    >
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: `${color}18`,
              color: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {Icon ? <Icon size={24} /> : <Sparkles size={24} />}
          </div>
          <Badge variant="neutral">{category || 'AI Round'}</Badge>
        </div>

        <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
          {title}
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '20px' }}>
          {subtitle}
        </p>
      </div>

      <div>
        <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-muted)', borderTop: '1px solid var(--border-light)', paddingTop: '14px', marginBottom: '14px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <HelpCircle size={14} /> {questionCount} Questions
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={14} /> ~{duration}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600, color: color }}>
            {difficulty}
          </span>
        </div>

        <button
          style={{
            width: '100%',
            padding: '9px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            backgroundColor: selected ? color : 'var(--bg-surface-alt)',
            color: selected ? '#ffffff' : 'var(--text-main)',
            border: selected ? 'none' : '1px solid var(--border-light)',
            transition: 'all 0.15s ease'
          }}
        >
          {selected ? 'Selected Mode' : 'Select Interview'}
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
