import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Code,
  MessageSquare,
  Sparkles,
  Camera,
  Mic,
  Sliders,
  CheckCircle2,
  ShieldAlert,
  ArrowRight,
  FolderGit2,
  Briefcase,
  AlertCircle,
  Brain,
  Layers,
  Award
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import interviewService from '../services/interviewService';
import Button from '../components/Button';
import Badge from '../components/Badge';

export default function InterviewSetup() {
  const { user, updateTargetRole } = useAuth();
  const navigate = useNavigate();

  const [selectedRound, setSelectedRound] = useState('full');
  const [questionCount, setQuestionCount] = useState(5);
  const [difficulty, setDifficulty] = useState('adaptive');
  const [enableCamera, setEnableCamera] = useState(true);
  const [enableMicrophone, setEnableMicrophone] = useState(true);
  const [selectedRole, setSelectedRole] = useState(user?.targetRole || "");
  const [customRoleInput, setCustomRoleInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const effectiveRole = selectedRole === "Other" 
    ? (customRoleInput.trim() || "Custom Role")
    : (selectedRole || user?.targetRole || "");

  // Real-World Interview Modes matching requirement 15
  const interviewModes = [
    {
      id: 'full',
      title: 'Full Employability Assessment',
      subtitle: 'Complete 4-round pipeline: Round 1 Aptitude (Quant, Logic, Verbal) → Round 2 AI HR → Round 3 Technical → Round 4 Multimodal Fusion.',
      category: 'Flagship Pipeline',
      badge: 'Recommended',
      startsAtAptitude: true,
      duration: '25-30 mins',
      difficulty: 'Adaptive',
      icon: Sparkles,
      color: '#6366f1'
    },
    {
      id: 'aptitude_hr',
      title: 'Aptitude + HR Interview',
      subtitle: 'Rapid screening track: Round 1 3-Tier Cognitive Aptitude followed directly by Round 2 AI HR STAR behavioral interview with speech-to-text.',
      category: 'Core Placement Track',
      badge: 'High Impact',
      startsAtAptitude: true,
      duration: '15-20 mins',
      difficulty: 'Adaptive',
      icon: Brain,
      color: '#38bdf8'
    },
    {
      id: 'technical',
      title: 'Technical Interview',
      subtitle: 'In-depth algorithmic problem solving, system design, and role-specific architecture with dynamic difficulty adaptation.',
      category: 'Technical Focus',
      badge: 'Code & Architecture',
      startsAtAptitude: false,
      duration: '12-15 mins',
      difficulty: 'Adaptive',
      icon: Code,
      color: '#0ea5e9'
    },
    {
      id: 'hr',
      title: 'HR & STAR Behavioral Interview',
      subtitle: 'Situational behavioral probing with real-time Speech-to-Text, STAR structure evaluation, and observable presentation cues.',
      category: 'Behavioral & Speech',
      badge: 'Voice & NLP',
      startsAtAptitude: false,
      duration: '10-12 mins',
      difficulty: 'STAR Evaluated',
      icon: MessageSquare,
      color: '#10b981'
    },
    {
      id: 'mock_placement',
      title: 'Mock Placement Interview',
      subtitle: 'Simulates a comprehensive campus placement drive with timed sections, strict evaluation, and recruiter scoring standards.',
      category: 'Campus Drive',
      badge: 'Recruiter Simulated',
      startsAtAptitude: true,
      duration: '20 mins',
      difficulty: 'Rigorous',
      icon: Award,
      color: '#f59e0b'
    },
    {
      id: 'role_specific',
      title: 'Role-Specific Deep Dive',
      subtitle: 'Tailored questions targeting candidate resume projects, hardware/software trade-offs, and JD-matched competencies.',
      category: 'Project Probing',
      badge: 'Resume-Aware',
      startsAtAptitude: false,
      duration: '12 mins',
      difficulty: 'Role Tailored',
      icon: FolderGit2,
      color: '#8b5cf6'
    }
  ];

  const handleLaunch = async () => {
    setErrorMsg("");
    if (!effectiveRole) {
      setErrorMsg("Please select or specify your Target Role before starting the interview.");
      return;
    }

    setLoading(true);
    try {
      if (effectiveRole !== user?.targetRole) {
        await updateTargetRole(effectiveRole);
      }

      const modeObj = interviewModes.find(m => m.id === selectedRound) || interviewModes[0];

      // If mode begins at Round 1 Aptitude
      if (modeObj.startsAtAptitude) {
        navigate('/aptitude', {
          state: {
            mode: modeObj.id,
            targetRole: effectiveRole,
            sessionConfig: {
              roundId: modeObj.id,
              roundType: modeObj.title,
              targetRole: effectiveRole,
              enableCamera,
              enableMicrophone,
              difficulty
            }
          }
        });
        return;
      }

      // Otherwise direct to specific round
      const qCount = selectedRound === 'hr' ? 4 : questionCount;
      const res = await interviewService.setupSession({
        roundId: selectedRound,
        roundType: modeObj.title,
        targetRole: effectiveRole,
        questionCount: qCount,
        difficulty,
        enableCamera,
        enableMicrophone
      });

      if (res.success && res.session) {
        navigate('/interview', {
          state: {
            session: res.session,
            sessionConfig: {
              roundId: selectedRound,
              roundType: modeObj.title,
              targetRole: effectiveRole,
              questionCount: qCount,
              difficulty,
              enableCamera,
              enableMicrophone
            }
          }
        });
      } else {
        setErrorMsg("Failed to initialize interview session. Please check backend connection.");
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to initialize interview session.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', maxWidth: '1100px', margin: '0 auto', width: '100%' }}>
      
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span style={{ fontSize: '12px', fontWeight: 800, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Assessment Configuration
          </span>
          <span style={{ fontSize: '12px', color: '#64748b' }}>•</span>
          <span style={{ fontSize: '13px', color: '#94a3b8' }}>Multi-Round Architecture</span>
        </div>
        <h2 style={{ fontSize: '26px', fontWeight: 800, color: '#f8fafc', margin: 0, letterSpacing: '-0.02em' }}>
          Configure Your Assessment Journey
        </h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginTop: '6px', lineHeight: 1.5 }}>
          Choose your interview mode, configure target role requirements, and initialize multimodal AI sensory tracking.
        </p>
      </div>

      {errorMsg && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 16px', backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '13.5px' }}>
          <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Professional Round Stepper Preview */}
      <div
        style={{
          backgroundColor: '#111827',
          borderRadius: '16px',
          border: '1px solid #1f2937',
          padding: '20px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#6366f1', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            1
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#a5b4fc' }}>ROUND 1</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Adaptive Aptitude</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#1e293b', border: '1px solid #374151', color: '#9ca3af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            2
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#f8fafc' }}>ROUND 2</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>AI HR & Voice STT</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#1e293b', border: '1px solid #374151', color: '#9ca3af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            3
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#f8fafc' }}>ROUND 3</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Adaptive Technical</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#1e293b', border: '1px solid #374151', color: '#9ca3af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            4
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#f8fafc' }}>ROUND 4</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Multimodal Fusion</div>
          </div>
        </div>
      </div>

      {/* Target Role Selector */}
      <div style={{ backgroundColor: '#111827', borderRadius: '16px', border: '1px solid #1f2937', padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Briefcase size={18} color="#818cf8" />
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
            Target Role Confirmation
          </h3>
        </div>
        <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
          All technical questions, difficulty adaptation, and competency rubrics will automatically align with this selected career track.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px' }}>
          {[
            "AI/ML Software Engineer",
            "VLSI Design Engineer",
            "Embedded Systems Engineer",
            "Cloud & DevOps Engineer",
            "Full Stack Web Developer",
            "Data Scientist",
            "Other"
          ].map(role => {
            const isSelected = selectedRole === role;
            return (
              <div
                key={role}
                onClick={() => setSelectedRole(role)}
                style={{
                  padding: '12px 14px',
                  borderRadius: '10px',
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : '#090d16',
                  border: isSelected ? '1.5px solid #6366f1' : '1px solid #1f2937',
                  color: isSelected ? '#a5b4fc' : '#e2e8f0',
                  fontWeight: isSelected ? 700 : 500,
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  transition: 'all 0.15s ease'
                }}
              >
                <span>{role}</span>
                {isSelected && <CheckCircle2 size={16} color="#818cf8" />}
              </div>
            );
          })}
        </div>

        {selectedRole === "Other" && (
          <div style={{ marginTop: '14px' }}>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
              Specify Custom Role
            </label>
            <input
              type="text"
              placeholder="e.g. Cybersecurity Analyst, Robotics Engineer..."
              value={customRoleInput}
              onChange={(e) => setCustomRoleInput(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                backgroundColor: '#090d16',
                border: '1px solid #6366f1',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '13.5px',
                outline: 'none'
              }}
            />
          </div>
        )}
      </div>

      {/* Real-World Interview Modes Grid */}
      <div>
        <div style={{ fontSize: '14px', fontWeight: 800, color: '#f8fafc', marginBottom: '14px' }}>
          Select Assessment Mode
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {interviewModes.map(mode => {
            const isSelected = selectedRound === mode.id;
            const Icon = mode.icon;

            return (
              <div
                key={mode.id}
                onClick={() => setSelectedRound(mode.id)}
                style={{
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.12)' : '#111827',
                  border: isSelected ? '2px solid #6366f1' : '1px solid #1f2937',
                  borderRadius: '16px',
                  padding: '22px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '14px',
                  transition: 'all 0.15s ease',
                  boxShadow: isSelected ? '0 8px 24px rgba(99, 102, 241, 0.25)' : 'none'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div
                      style={{
                        width: '38px',
                        height: '38px',
                        borderRadius: '10px',
                        backgroundColor: `${mode.color}22`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <Icon size={20} color={mode.color} />
                    </div>
                    <span style={{ fontSize: '11px', fontWeight: 700, padding: '3px 8px', borderRadius: '6px', backgroundColor: `${mode.color}22`, color: mode.color }}>
                      {mode.badge}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', margin: '0 0 6px 0' }}>
                    {mode.title}
                  </h4>
                  <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: 0, lineHeight: 1.5 }}>
                    {mode.subtitle}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #1f2937', paddingTop: '12px', fontSize: '12px', color: '#64748b' }}>
                  <span>Duration: <strong style={{ color: '#cbd5e1' }}>{mode.duration}</strong></span>
                  <span style={{ color: mode.color, fontWeight: 700 }}>
                    {mode.startsAtAptitude ? "Starts at Round 1 →" : "Direct Launch →"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sensory Configuration (Camera & Mic) */}
      <div style={{ backgroundColor: '#111827', borderRadius: '16px', border: '1px solid #1f2937', padding: '24px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc', margin: '0 0 14px 0' }}>
          Sensory Modality Settings
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div
            onClick={() => setEnableCamera(!enableCamera)}
            style={{
              padding: '16px',
              borderRadius: '12px',
              backgroundColor: enableCamera ? 'rgba(99, 102, 241, 0.12)' : '#090d16',
              border: enableCamera ? '1.5px solid #6366f1' : '1px solid #1f2937',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '14px'
            }}
          >
            <Camera size={22} color={enableCamera ? '#818cf8' : '#6b7280'} />
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: '#f8fafc' }}>
                Computer Vision Camera Tracking
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                Observable presentation cues, camera-facing consistency, posture
              </div>
            </div>
          </div>

          <div
            onClick={() => setEnableMicrophone(!enableMicrophone)}
            style={{
              padding: '16px',
              borderRadius: '12px',
              backgroundColor: enableMicrophone ? 'rgba(16, 185, 129, 0.12)' : '#090d16',
              border: enableMicrophone ? '1.5px solid #10b981' : '1px solid #1f2937',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '14px'
            }}
          >
            <Mic size={22} color={enableMicrophone ? '#34d399' : '#6b7280'} />
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: '#f8fafc' }}>
                Microphone & Speech-to-Text
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                Live speech recognition, speaking rate (WPM), acoustic volume
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Launch Action */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '10px' }}>
        <button
          onClick={handleLaunch}
          disabled={loading || !effectiveRole}
          style={{
            padding: '14px 32px',
            background: (!effectiveRole || loading) ? '#374151' : 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
            color: '#ffffff',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 800,
            fontSize: '15px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            cursor: (!effectiveRole || loading) ? 'not-allowed' : 'pointer',
            boxShadow: effectiveRole ? '0 8px 24px rgba(99, 102, 241, 0.35)' : 'none'
          }}
        >
          {loading ? (
            "Initializing Assessment..."
          ) : (
            <>
              <span>Begin Assessment Track</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>

    </div>
  );
}
