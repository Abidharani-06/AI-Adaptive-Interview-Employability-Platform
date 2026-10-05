import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, Menu, Sparkles, CheckCircle2, Shield, User, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Badge from './Badge';

export default function Navbar({ onMobileMenuToggle }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, assessment, isDemo } = useAuth();

  const routeTitles = {
    '/dashboard': 'Candidate Career Intelligence Dashboard',
    '/resume': 'Resume & Job Description Analysis',
    '/interview-setup': 'Interview Configuration & Modalities',
    '/aptitude': 'Round 1: Cognitive Aptitude Assessment',
    '/aptitude/results': 'Round 1 Aptitude Evaluation & Diagnostics',
    '/interview': 'Round 2: Live AI HR & Multimodal Interview',
    '/results': 'Final Multimodal Employability Assessment',
    '/skill-gaps': 'Target Role Skill Gap Analysis',
    '/roadmap': 'Personalized 5-Week Learning Roadmap',
    '/feedback': 'Actionable Multimodal AI Feedback',
    '/progress': 'Longitudinal Performance & Progress',
    '/profile': 'Candidate Profile & Academic Portfolio',
    '/settings': 'Platform & Privacy Preferences'
  };

  const currentTitle = routeTitles[location.pathname] || 'Employability Assessment Suite';
  const targetRole = user?.targetRole || assessment?.job_alignment?.target_role || "Not selected";

  return (
    <header
      style={{
        height: 'var(--navbar-height)',
        backgroundColor: '#0f172a',
        borderBottom: '1px solid #1e293b',
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.25)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onMobileMenuToggle}
          style={{
            display: 'none',
            padding: '6px',
            borderRadius: '6px',
            color: '#94a3b8'
          }}
          className="mobile-toggle-btn"
        >
          <Menu size={22} />
        </button>

        <div>
          <h1 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em', margin: 0 }}>
            {currentTitle}
          </h1>
          <div style={{ fontSize: '11.5px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
            <span>Target Role:</span>
            <strong style={{ color: targetRole === "Not selected" ? '#f59e0b' : '#38bdf8' }}>
              {targetRole}
            </strong>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Verification Status Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: user?.isVerified ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)',
            border: user?.isVerified ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(99, 102, 241, 0.3)',
            color: user?.isVerified ? '#34d399' : '#818cf8',
            padding: '4px 10px',
            borderRadius: '20px',
            fontSize: '11.5px',
            fontWeight: 600
          }}
          title={user?.isVerified ? "Verified Candidate Profile" : "Authenticated Session"}
        >
          <CheckCircle2 size={13} />
          <span className="hidden-mobile">{user?.isVerified ? "Verified Profile" : "Candidate Active"}</span>
        </div>

        {/* Readiness Badge */}
        {assessment?.readiness ? (
          <div
            style={{
              padding: '4px 12px',
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              border: '1px solid rgba(99, 102, 241, 0.4)',
              borderRadius: '20px',
              color: '#a5b4fc',
              fontSize: '12px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#818cf8' }} />
            <span>{assessment.readiness.level} ({assessment.readiness.score}%)</span>
          </div>
        ) : (
          <div
            style={{
              padding: '4px 12px',
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '20px',
              color: '#94a3b8',
              fontSize: '12px',
              fontWeight: 600
            }}
          >
            No Assessment Completed
          </div>
        )}

        {/* Profile Avatar Quick Link */}
        <div
          onClick={() => navigate('/profile')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 8px',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'background 0.15s ease'
          }}
        >
          <img
            src={user?.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${user?.name || "Candidate"}`}
            alt={user?.name || "Candidate"}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              objectFit: 'cover',
              border: '1.5px solid #374151'
            }}
          />
        </div>
      </div>
    </header>
  );
}
