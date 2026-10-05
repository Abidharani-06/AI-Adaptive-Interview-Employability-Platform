import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Code2,
  MessageSquare,
  Mic,
  Camera,
  FileCheck,
  Sparkles,
  FileQuestion,
  Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';

export default function Feedback() {
  const { user, assessment } = useAuth();
  const navigate = useNavigate();

  const candName = assessment?.candidate?.name || user?.name || user?.full_name || "Candidate";
  const strengths = assessment?.strengths || [
    "Clear, structured algorithmic reasoning and step-by-step logic breakdown.",
    "Consistent eye contact and stable camera-facing orientation throughout responses.",
    "Well-articulated project contributions adhering to the STAR framework."
  ];
  const weaknesses = assessment?.improvement_areas || [
    "State computational time and space trade-offs before implementing recursive solutions.",
    "Quantify metrics and business outcomes more explicitly in behavioral questions.",
    "Incorporate brief silent pauses instead of filler words when transitioning thoughts."
  ];
  const recommendations = assessment?.recommendations || [
    "Practice timed LeetCode Medium dynamic programming and graph traversal drills.",
    "Record 2-minute STAR behavioral responses focusing 60% of duration on Actions taken.",
    "Review quantitative aptitude speed formulas for percentages and time-speed-distance."
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 8 Multimodal Coaching
            </span>
            <Badge variant="primary">AI Career Intelligence</Badge>
          </div>
          <h2 className="page-title">Personalized AI Performance Coaching</h2>
          <p className="page-subtitle">
            Multimodal strengths, priority growth areas, and actionable recommendations for <strong>{candName}</strong>.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button
            variant="outline"
            icon={Zap}
            onClick={() => navigate('/aptitude')}
          >
            Round 1 Drill
          </Button>
          <Button
            variant="primary"
            icon={ArrowRight}
            iconPosition="right"
            onClick={() => navigate('/interview-setup')}
          >
            Retake Interview Drill
          </Button>
        </div>
      </div>

      {/* Two Column: Strengths vs Improvement Areas */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        
        {/* Verified Strengths */}
        <div className="card" style={{ borderTop: '4px solid #10b981', padding: '24px', background: '#111827', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle2 size={20} color="#10b981" />
            </div>
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                Demonstrated Strengths
              </h3>
              <span style={{ fontSize: '12px', color: '#94a3b8' }}>Validated across technical & HR rounds</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {strengths.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '13px', color: '#cbd5e1', lineHeight: 1.5 }}>
                <span style={{ color: '#10b981', fontWeight: 700 }}>✓</span>
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Areas for Improvement */}
        <div className="card" style={{ borderTop: '4px solid #f59e0b', padding: '24px', background: '#111827', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AlertTriangle size={20} color="#f59e0b" />
            </div>
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                High-Leverage Growth Areas
              </h3>
              <span style={{ fontSize: '12px', color: '#94a3b8' }}>Targeted refinement opportunities</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {weaknesses.map((w, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '13px', color: '#cbd5e1', lineHeight: 1.5 }}>
                <span style={{ color: '#f59e0b', fontWeight: 700 }}>•</span>
                <span>{w}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Multimodal Dimension Coaching Grid */}
      <div>
        <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
          Dimension-Specific Coaching Guidance
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
          
          {/* Round 1: Aptitude */}
          <div className="card" style={{ padding: '20px', background: '#111827', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Zap size={18} color="#10b981" />
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>Round 1: Aptitude</h4>
            </div>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>
              Pace yourself to allocate ~60-75 seconds per question. In Quantitative sections, prioritize ratio and percentage approximation shortcuts before computing decimal steps.
            </p>
          </div>

          {/* Technical */}
          <div className="card" style={{ padding: '20px', background: '#111827', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Code2 size={18} color="#6366f1" />
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>Technical Problem Solving</h4>
            </div>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>
              Practice dry-running algorithms out loud before coding. State time and space trade-offs clearly before writing implementation logic.
            </p>
          </div>

          {/* HR / Behavioral */}
          <div className="card" style={{ padding: '20px', background: '#111827', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <MessageSquare size={18} color="#8b5cf6" />
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>STAR Behavioral Delivery</h4>
            </div>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>
              Structure project answers tightly: limit the initial Situation context to 20 seconds, dedicate 60% of your time to specific personal Actions taken.
            </p>
          </div>

          {/* Speech */}
          <div className="card" style={{ padding: '20px', background: '#111827', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Mic size={18} color="#f59e0b" />
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>Speech Cadence & Articulation</h4>
            </div>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>
              Maintain conversational pacing between 130 and 150 WPM. When transitioning between ideas, substitute verbal filler sounds ("uh", "um") with deliberate silent micro-pauses.
            </p>
          </div>

        </div>
      </div>

      {/* Priority Action Plan Banner */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(17, 24, 39, 0.95) 100%)',
          border: '1px solid #312e81',
          borderRadius: '16px',
          color: '#ffffff',
          padding: '28px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <Lightbulb size={22} color="#facc15" />
          <h3 style={{ fontSize: '18px', fontWeight: 800, margin: 0, color: '#f8fafc' }}>
            Action Plan for Upcoming Campus Placement Drive
          </h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {recommendations.map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '13.5px', color: '#cbd5e1', lineHeight: 1.5 }}>
              <span style={{ color: '#38bdf8', fontWeight: 700 }}>#{i + 1}</span>
              <span>{r}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
