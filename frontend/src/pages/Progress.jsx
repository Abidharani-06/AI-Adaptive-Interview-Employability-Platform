import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  Award,
  Calendar,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Layers,
  FileQuestion,
  AlertCircle,
  Zap,
  Play
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';
import ProgressChart from '../components/ProgressChart';

export default function Progress() {
  const { user, assessment } = useAuth();
  const navigate = useNavigate();

  const history = user?.interviewHistory || assessment?.progress_tracking?.timeline || [];
  const candName = user?.name || user?.full_name || "Candidate";

  if (history.length === 0 && !assessment) {
    return (
      <div
        className="card"
        style={{
          padding: '60px 24px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          background: 'linear-gradient(135deg, #111827 0%, #1e293b 100%)',
          border: '1px solid #1e293b',
          borderRadius: '16px'
        }}
      >
        <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: 'rgba(14, 165, 233, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
          <FileQuestion size={32} color="#38bdf8" />
        </div>
        <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
          No Progress History Recorded Yet
        </h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', maxWidth: '460px', marginBottom: '24px', lineHeight: 1.5 }}>
          Your performance history, multi-attempt trend curves, and skill gap resolution tracking will record here automatically after completing your mock interviews.
        </p>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Button variant="outline" onClick={() => navigate('/aptitude')}>
            Take Round 1 Aptitude
          </Button>
          <Button variant="primary" icon={Sparkles} onClick={() => navigate('/interview-setup')}>
            Start First Mock Interview
          </Button>
        </div>
      </div>
    );
  }

  const tracking = assessment?.progress_tracking || {
    current_attempt: history.length || 1,
    total_attempts: history.length || 1,
    score_delta_previous: history.length > 1 ? Math.round((history[history.length - 1].score - history[history.length - 2].score) * 10) / 10 : 0,
    progress_narrative: history.length > 1 ? "Positive readiness progression tracked across practice iterations." : "Initial baseline assessment established.",
    improved_areas: ["Overall Placement Readiness", "Technical Accuracy", "Camera Gaze Stability"],
    persistent_gaps: assessment?.job_alignment?.missing_skills?.slice(0, 3) || ["Data Structures & Algorithms", "System Design Patterns"]
  };

  const lineChartData = history.map((item, idx) => ({
    attempt: `Attempt ${item.attempt || idx + 1}`,
    score: item.score || 72,
    technical: item.component_scores?.technical || item.componentScores?.technical || 68,
    hr: item.component_scores?.hr_nlp || item.componentScores?.hr_nlp || 76,
    speech: item.component_scores?.speech || item.componentScores?.speech || 80
  }));

  const delta = tracking.score_delta_previous;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 8 Longitudinal Progression Hub
            </span>
            <Badge variant="primary">{history.length} Session{history.length > 1 ? 's' : ''} Recorded</Badge>
          </div>
          <h2 className="page-title">Candidate Multi-Attempt Progress Hub</h2>
          <p className="page-subtitle">
            Historical trajectory across interview attempts for <strong>{candName}</strong>.
          </p>
        </div>

        <Button
          variant="primary"
          icon={ArrowRight}
          iconPosition="right"
          onClick={() => navigate('/interview-setup')}
        >
          Begin Next Practice Session
        </Button>
      </div>

      {/* Hero Delta Summary */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%)',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          padding: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px'
        }}
      >
        <div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '4px' }}>
            Trajectory Delta Since Previous Attempt
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '36px', fontWeight: 800, color: delta >= 0 ? '#34d399' : '#f43f5e', letterSpacing: '-0.03em' }}>
              {delta >= 0 ? `+${delta}%` : `${delta}%`}
            </span>
            <Badge variant={delta >= 0 ? 'success' : 'danger'} size="md">
              {delta >= 0 ? 'Positive Growth' : 'Decline Detected'}
            </Badge>
          </div>
          <p style={{ fontSize: '14px', color: '#cbd5e1', marginTop: '6px', margin: 0 }}>
            {tracking.progress_narrative}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '24px', borderLeft: '1px solid #334155', paddingLeft: '24px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Baseline Attempt</div>
            <div style={{ fontSize: '22px', fontWeight: 800, color: '#f8fafc', marginTop: '2px' }}>
              {history[0]?.score || assessment?.readiness?.score || 72}%
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Latest Attempt Score</div>
            <div style={{ fontSize: '22px', fontWeight: 800, color: 'var(--primary)', marginTop: '2px' }}>
              {history[history.length - 1]?.score || assessment?.readiness?.score || 72}%
            </div>
          </div>
        </div>
      </div>

      {/* Main Trend Line Chart */}
      <div className="card" style={{ padding: '24px', background: '#111827', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Multi-Attempt Score Progression
            </h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
              Tracking overall readiness, technical depth, and STAR behavioral quality across sessions.
            </p>
          </div>
          <Badge variant="primary">Historical Analytics</Badge>
        </div>

        {lineChartData.length > 1 ? (
          <div style={{ height: '320px', width: '100%' }}>
            <ProgressChart type="line" data={lineChartData} height={320} color="#06b6d4" />
          </div>
        ) : (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: '#94a3b8', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px', border: '1px dashed #334155' }}>
            <TrendingUp size={36} color="#38bdf8" style={{ marginBottom: '10px' }} />
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc' }}>
              1 Practice Session Recorded (Baseline Established)
            </div>
            <p style={{ fontSize: '13px', color: '#94a3b8', maxWidth: '420px', margin: '6px auto 16px auto' }}>
              Complete a second interview drill to view multi-point trajectory curves and dimension comparisons.
            </p>
            <Button
              variant="primary"
              size="sm"
              icon={Play}
              onClick={() => navigate('/interview-setup')}
            >
              Start Second Attempt
            </Button>
          </div>
        )}
      </div>

      {/* Two Column: Resolved Gaps vs Persistent Gaps */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        
        {/* Resolved Skill Gaps */}
        <div className="card" style={{ borderTop: '4px solid #10b981', padding: '24px', background: '#111827', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <CheckCircle2 size={20} color="#10b981" />
            <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Resolved Competencies & Gains
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {tracking.improved_areas?.map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#cbd5e1' }}>
                <span style={{ color: '#10b981', fontWeight: 700 }}>✓</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Persistent Gaps */}
        <div className="card" style={{ borderTop: '4px solid #f43f5e', padding: '24px', background: '#111827', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <AlertCircle size={20} color="#f43f5e" />
            <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Persistent Technical Gaps
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {tracking.persistent_gaps?.map((gap, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#cbd5e1' }}>
                <span style={{ color: '#f43f5e', fontWeight: 700 }}>•</span>
                <span style={{ textTransform: 'capitalize' }}>{gap}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
