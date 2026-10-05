import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Code2,
  MessageSquare,
  Mic,
  Camera,
  FileCheck,
  Play,
  FileUp,
  Map,
  ArrowUpRight,
  TrendingUp,
  AlertCircle,
  Calendar,
  Sparkles,
  ChevronRight,
  CheckCircle2,
  Clock,
  Layers,
  UserCheck,
  Target,
  FileQuestion,
  Award,
  Zap,
  BarChart3,
  Brain,
  HelpCircle,
  Activity
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Scorecard from '../components/Scorecard';
import Badge from '../components/Badge';
import Button from '../components/Button';
import ProgressChart from '../components/ProgressChart';
import aptitudeService from '../services/aptitudeService';

export default function Dashboard() {
  const { user, assessment, profileCompletion } = useAuth();
  const navigate = useNavigate();

  const [latestAptitude, setLatestAptitude] = useState(user?.latestAptitude || null);

  // Fetch latest aptitude attempt if not yet loaded in user context
  useEffect(() => {
    let isMounted = true;
    if (user?.latestAptitude) {
      setLatestAptitude(user.latestAptitude);
    } else {
      aptitudeService.getLatestAptitude()
        .then(res => {
          if (isMounted && res.success && res.attempt) {
            setLatestAptitude(res.attempt);
          }
        })
        .catch(() => {});
    }
    return () => { isMounted = false; };
  }, [user]);

  const candName = user?.name || user?.full_name || "Candidate";
  const targetRole = user?.targetRole || "Not selected";
  const aiSuggestedRole = user?.resume?.aiSuggestedRole || assessment?.candidate_profile?.ai_suggested_role || "Pending resume upload";
  const hasAssessment = !!assessment;
  const hasResume = !!user?.resume && user.resume.skills && user.resume.skills.length > 0;
  const hasJD = !!user?.jobDescription;
  const hasAptitude = !!latestAptitude;

  const readiness = assessment?.readiness || {
    score: 0,
    level: "Not evaluated yet",
    description: "Complete Round 1 Aptitude and Interview to generate your placement readiness score."
  };
  const compScores = assessment?.multimodal_assessment?.component_scores || {};
  const radarData = assessment?.visualization_data?.radar_chart || (hasAssessment ? [
    { dimension: "Technical", score: compScores.technical || 0 },
    { dimension: "HR NLP", score: compScores.hr_nlp || 0 },
    { dimension: "Speech", score: compScores.speech || 0 },
    { dimension: "Visual CV", score: compScores.computer_vision || 0 },
    { dimension: "Resume-JD", score: compScores.resume_jd || 0 },
    { dimension: "Aptitude", score: latestAptitude?.overallScore || 0 }
  ] : []);
  
  const timelineData = user?.interviewHistory || assessment?.progress_tracking?.timeline || [];
  const skillGaps = assessment?.skill_gaps || { high_priority: [], medium_priority: [], total_gaps: 0 };
  const roadmap = assessment?.learning_roadmap || null;

  // AI Career Intelligence Derived Insights
  const strongestSkill = (hasResume && user.resume.skills?.length > 0)
    ? user.resume.skills[0]
    : (assessment?.strengths?.[0] || "Foundational CS");

  const criticalGap = skillGaps?.prioritized_gaps?.[0]?.skill 
    || (latestAptitude?.weakTopics?.[0]?.topic ? `Aptitude: ${latestAptitude.weakTopics[0].topic}` : null)
    || (hasResume && targetRole !== "Not selected" ? "Data Structures & System Design" : "Complete Skills Audit");

  const readinessTrend = timelineData.length > 1
    ? `+${(timelineData[timelineData.length - 1].score - timelineData[timelineData.length - 2].score).toFixed(1)}% vs previous`
    : timelineData.length === 1
    ? "Baseline recorded"
    : "Awaiting first assessment";

  const nextBestAction = !hasResume
    ? "Upload your technical resume to unlock skill extraction and candidate-specific questions."
    : !hasAptitude
    ? "Take Round 1: Adaptive Aptitude Assessment (Quant, Reasoning, Verbal)."
    : !hasAssessment
    ? "Complete Round 2: AI HR & Behavioral Interview with Live Speech-to-Text."
    : skillGaps?.prioritized_gaps?.[0]
    ? `Review ${skillGaps.prioritized_gaps[0].skill} modules in your 5-Week Personalized Roadmap.`
    : "Take a full mock placement interview to benchmark readiness tier.";

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Hero Greeting & Action Header */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(30, 41, 59, 0.85) 50%, rgba(15, 23, 42, 0.95) 100%)',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          padding: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Employability Intelligence Center
            </span>
            <Badge variant={user?.isVerified ? 'success' : 'neutral'} dot size="sm">
              {user?.isVerified ? 'Verified Account' : 'Candidate'}
            </Badge>
          </div>

          <h2 style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.03em', margin: 0 }}>
            Welcome, {candName.split(' ')[0]} 👋
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', marginTop: '10px', fontSize: '13.5px' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Target Role: </span>
              <strong style={{ color: targetRole === "Not selected" ? '#f59e0b' : '#38bdf8' }}>
                {targetRole}
              </strong>
            </div>
            <div style={{ color: '#475569' }}>•</div>
            <div>
              <span style={{ color: '#94a3b8' }}>AI Suggested Role: </span>
              <strong style={{ color: '#a78bfa' }}>
                {aiSuggestedRole}
              </strong>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', position: 'relative', zIndex: 1 }}>
          <Button
            variant="outline"
            icon={FileUp}
            onClick={() => navigate('/resume')}
          >
            {hasResume ? "Update Resume" : "Upload Resume"}
          </Button>

          <Button
            variant="secondary"
            icon={Zap}
            onClick={() => navigate('/aptitude')}
          >
            {hasAptitude ? "Retake Round 1 Aptitude" : "Start Round 1 Aptitude"}
          </Button>

          <Button
            variant="primary"
            icon={Play}
            onClick={() => navigate('/interview-setup')}
          >
            {hasAssessment ? "Start Interview Drill" : "Start Full Interview"}
          </Button>
        </div>
      </div>

      {/* AI CAREER INTELLIGENCE / COMMAND CENTER (Requirement 19) */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(99, 102, 241, 0.06) 50%, rgba(17, 24, 39, 0.8) 100%)',
          border: '1px solid rgba(14, 165, 233, 0.25)',
          borderRadius: '16px',
          padding: '24px'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '10px', backgroundColor: 'rgba(14, 165, 233, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Brain size={20} color="#38bdf8" />
            </div>
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                AI Career Intelligence
              </h3>
              <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: 0 }}>
                Dynamic insights synthesized from verified candidate assessment data
              </p>
            </div>
          </div>
          <Badge variant="primary" size="sm">Real-time Telemetry</Badge>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          
          {/* 1. Strongest Skill */}
          <div style={{ padding: '16px', borderRadius: '12px', backgroundColor: 'rgba(17, 24, 39, 0.7)', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', marginBottom: '6px' }}>
              <CheckCircle2 size={14} /> Strongest Area
            </div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f1f5f9', textTransform: 'capitalize' }}>
              {strongestSkill}
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px', margin: 0 }}>
              High proficiency verified in profile & responses
            </p>
          </div>

          {/* 2. Critical Skill Gap */}
          <div style={{ padding: '16px', borderRadius: '12px', backgroundColor: 'rgba(17, 24, 39, 0.7)', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 700, color: '#f43f5e', textTransform: 'uppercase', marginBottom: '6px' }}>
              <AlertCircle size={14} /> Critical Gap
            </div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f1f5f9', textTransform: 'capitalize' }}>
              {criticalGap}
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px', margin: 0 }}>
              Priority benchmark item for placement clearance
            </p>
          </div>

          {/* 3. Recommended Role */}
          <div style={{ padding: '16px', borderRadius: '12px', backgroundColor: 'rgba(17, 24, 39, 0.7)', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase', marginBottom: '6px' }}>
              <Target size={14} /> Recommended Role
            </div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f1f5f9' }}>
              {aiSuggestedRole}
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px', margin: 0 }}>
              AI matched from skills, projects & background
            </p>
          </div>

          {/* 4. Readiness Trend */}
          <div style={{ padding: '16px', borderRadius: '12px', backgroundColor: 'rgba(17, 24, 39, 0.7)', border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '6px' }}>
              <TrendingUp size={14} /> Readiness Trend
            </div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f1f5f9' }}>
              {readinessTrend}
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px', margin: 0 }}>
              Longitudinal tracking over practice iterations
            </p>
          </div>

        </div>

        {/* 5. Next Best Action Callout */}
        <div style={{ marginTop: '16px', padding: '14px 18px', borderRadius: '10px', backgroundColor: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={18} color="#818cf8" style={{ flexShrink: 0 }} />
            <div>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Next Best Action:{" "}
              </span>
              <span style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 500 }}>
                {nextBestAction}
              </span>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            icon={ArrowUpRight}
            iconPosition="right"
            onClick={() => {
              if (!hasResume) navigate('/resume');
              else if (!hasAptitude) navigate('/aptitude');
              else if (!hasAssessment) navigate('/interview-setup');
              else navigate('/roadmap');
            }}
          >
            Execute Action
          </Button>
        </div>
      </div>

      {/* Multimodal Scorecards Grid (8 Modalities: Placement, Aptitude, Technical, HR, Comm, Speech, CV, Resume) */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
            Multimodal Assessment Modalities
          </h3>
          <span style={{ fontSize: '12.5px', color: '#94a3b8' }}>
            Data-driven evaluation across 6 distinct AI pipelines
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '16px' }}>
          
          {/* Overall Placement Readiness */}
          <Scorecard
            title="Placement Readiness"
            score={hasAssessment ? `${readiness.score}%` : "Not evaluated"}
            progress={hasAssessment ? readiness.score : 0}
            color="#06b6d4"
            subtitle={hasAssessment ? `Tier: ${readiness.level}` : "Requires interview"}
            icon={Award}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Round 1: Aptitude Assessment */}
          <Scorecard
            title="Round 1: Aptitude"
            score={hasAptitude ? `${latestAptitude.overallScore}%` : "Not completed"}
            progress={hasAptitude ? latestAptitude.overallScore : 0}
            color="#10b981"
            subtitle={hasAptitude ? `Q: ${latestAptitude.quantitativeScore}% | L: ${latestAptitude.reasoningScore}% | V: ${latestAptitude.verbalScore}%` : "Quant, Logic & Verbal"}
            icon={Zap}
            onClick={() => navigate('/aptitude')}
          />

          {/* Technical Problem Solving */}
          <Scorecard
            title="Technical Core"
            score={hasAssessment ? `${compScores.technical}%` : "Not evaluated"}
            progress={hasAssessment ? compScores.technical : 0}
            color="#6366f1"
            subtitle="Adaptive technical accuracy"
            icon={Code2}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Round 2: HR & Behavioral NLP */}
          <Scorecard
            title="Round 2: HR & STAR"
            score={hasAssessment ? `${compScores.hr_nlp}%` : "Not evaluated"}
            progress={hasAssessment ? compScores.hr_nlp : 0}
            color="#8b5cf6"
            subtitle="Semantic relevance & STAR structure"
            icon={MessageSquare}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Communication Score */}
          <Scorecard
            title="Communication"
            score={hasAssessment ? `${compScores.communication || Math.round(((compScores.speech || 75) + (compScores.hr_nlp || 75)) / 2)}%` : "Not evaluated"}
            progress={hasAssessment ? (compScores.communication || Math.round(((compScores.speech || 75) + (compScores.hr_nlp || 75)) / 2)) : 0}
            color="#ec4899"
            subtitle="Articulation & fluency"
            icon={Activity}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Speech & Acoustic Delivery */}
          <Scorecard
            title="Speech Delivery"
            score={hasAssessment ? `${compScores.speech}%` : "Not evaluated"}
            progress={hasAssessment ? compScores.speech : 0}
            color="#f59e0b"
            subtitle="WPM, pauses & volume stability"
            icon={Mic}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Observable Presentation (CV) */}
          <Scorecard
            title="Visual Presentation (CV)"
            score={hasAssessment ? `${compScores.computer_vision}%` : "Not evaluated"}
            progress={hasAssessment ? compScores.computer_vision : 0}
            color="#0ea5e9"
            subtitle="Gaze & posture consistency"
            icon={Camera}
            onClick={() => navigate(hasAssessment ? '/results' : '/interview-setup')}
          />

          {/* Resume & JD Alignment */}
          <Scorecard
            title="Resume & JD Match"
            score={user?.jobDescription ? `${user.jobDescription.matchScore}%` : hasAssessment ? `${compScores.resume_jd}%` : "Not evaluated"}
            progress={user?.jobDescription ? user.jobDescription.matchScore : hasAssessment ? compScores.resume_jd : 0}
            color="#14b8a6"
            subtitle={hasJD ? `Matched to ${user.jobDescription.title}` : "Upload JD to compare"}
            icon={FileCheck}
            onClick={() => navigate('/resume')}
          />

        </div>
      </div>

      {/* Main Analytics Row: Radar Chart + Prioritized Skill Gaps */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        
        {/* Left: 6-Dimension Radar Chart */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '24px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                  Multimodal Performance Dimensions
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Evaluated across Aptitude, NLP, Computer Vision, Speech, and Domain Alignment.
                </p>
              </div>
              <Badge variant={hasAssessment ? 'success' : 'neutral'}>
                {hasAssessment ? readiness.level : "Pending Data"}
              </Badge>
            </div>

            {hasAssessment || hasAptitude ? (
              <div style={{ height: '320px', width: '100%' }}>
                <ProgressChart type="radar" data={radarData} height={320} color="#06b6d4" />
              </div>
            ) : (
              <div
                style={{
                  height: '300px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px dashed #334155',
                  padding: '24px',
                  textAlign: 'center'
                }}
              >
                <Sparkles size={36} color="#64748b" style={{ marginBottom: '12px' }} />
                <div style={{ fontSize: '15px', fontWeight: 700, color: '#cbd5e1' }}>
                  No Assessment Radar Available
                </div>
                <p style={{ fontSize: '13px', color: '#94a3b8', maxWidth: '340px', marginTop: '4px' }}>
                  Complete Round 1 Aptitude or your first AI interview to populate the 6-dimension performance radar.
                </p>
                <div style={{ display: 'flex', gap: '10px', marginTop: '14px' }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => navigate('/aptitude')}
                  >
                    Start Round 1 Aptitude
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate('/interview-setup')}
                  >
                    Start Interview
                  </Button>
                </div>
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: '1px solid #1e293b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '12px',
              color: '#94a3b8'
            }}
          >
            <span>Fusion Weights: Tech (30%), HR (25%), Speech (15%), CV (15%), Match (15%)</span>
            <button
              onClick={() => navigate('/results')}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                cursor: 'pointer'
              }}
            >
              Full Report <ArrowUpRight size={14} />
            </button>
          </div>
        </div>

        {/* Right: Prioritized Skill Gaps */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '24px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                  Prioritized Skill Gaps
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  Classified into High, Medium, and Low severity.
                </p>
              </div>
              <Badge variant={skillGaps.total_gaps > 0 ? "warning" : "neutral"}>
                {skillGaps.total_gaps > 0 ? `${skillGaps.total_gaps} Detected` : "None recorded"}
              </Badge>
            </div>

            {skillGaps.total_gaps > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {skillGaps.prioritized_gaps?.slice(0, 4).map((gap, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 14px',
                      borderRadius: '10px',
                      backgroundColor: gap.priority === 'HIGH' ? 'rgba(239, 68, 68, 0.08)' : 'rgba(30, 41, 59, 0.6)',
                      border: gap.priority === 'HIGH' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid #1e293b',
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                      <AlertCircle
                        size={16}
                        color={gap.priority === 'HIGH' ? '#f43f5e' : '#f59e0b'}
                        style={{ marginTop: '2px', flexShrink: 0 }}
                      />
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', textTransform: 'capitalize' }}>
                            {gap.skill}
                          </span>
                          {gap.is_core && (
                            <span style={{ fontSize: '10.5px', padding: '1px 6px', borderRadius: '4px', backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', fontWeight: 600 }}>
                              Core Skill
                            </span>
                          )}
                        </div>
                        <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px', lineHeight: 1.4, margin: 0 }}>
                          {gap.reason}
                        </p>
                      </div>
                    </div>
                    <Badge variant={gap.priority === 'HIGH' ? 'danger' : 'warning'} size="sm">
                      {gap.priority}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div
                style={{
                  height: '240px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  borderRadius: '12px',
                  border: '1px dashed #334155',
                  padding: '24px',
                  textAlign: 'center'
                }}
              >
                <FileCheck size={32} color="#64748b" style={{ marginBottom: '10px' }} />
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#cbd5e1' }}>
                  No Skill Gaps Identified Yet
                </div>
                <p style={{ fontSize: '12.5px', color: '#94a3b8', maxWidth: '300px', marginTop: '4px' }}>
                  Upload your resume and select a target Job Description to detect priority gaps.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  style={{ marginTop: '12px' }}
                  onClick={() => navigate('/resume')}
                >
                  Analyze Resume
                </Button>
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: '1px solid #1e293b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '12px'
            }}
          >
            <span style={{ color: '#94a3b8' }}>Synthesized from resume & JD</span>
            <button
              onClick={() => navigate('/skill-gaps')}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                cursor: 'pointer'
              }}
            >
              View All Gaps <ChevronRight size={14} />
            </button>
          </div>
        </div>

      </div>

      {/* Progress & 5-Week Roadmap Preview Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px' }}>
        
        {/* Left: Attempt History */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                Recent Assessment History
              </h3>
              <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                Longitudinal progression across authenticated attempts.
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              icon={TrendingUp}
              onClick={() => navigate('/progress')}
            >
              Progress Hub
            </Button>
          </div>

          {timelineData.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #1e293b', color: '#94a3b8' }}>
                    <th style={{ padding: '10px 8px', fontWeight: 600 }}>Attempt</th>
                    <th style={{ padding: '10px 8px', fontWeight: 600 }}>Date</th>
                    <th style={{ padding: '10px 8px', fontWeight: 600 }}>Readiness</th>
                    <th style={{ padding: '10px 8px', fontWeight: 600 }}>Tier</th>
                    <th style={{ padding: '10px 8px', fontWeight: 600 }}>Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {timelineData.map((item, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                      <td style={{ padding: '12px 8px', fontWeight: 600, color: '#f8fafc' }}>
                        Attempt #{item.attempt || idx + 1}
                      </td>
                      <td style={{ padding: '12px 8px', color: '#94a3b8' }}>
                        {item.date || "Recent"}
                      </td>
                      <td style={{ padding: '12px 8px', fontWeight: 700, color: 'var(--primary)' }}>
                        {item.score}%
                      </td>
                      <td style={{ padding: '12px 8px' }}>
                        <Badge variant="success" size="sm">{item.readiness_level || "Evaluated"}</Badge>
                      </td>
                      <td style={{ padding: '12px 8px', color: '#34d399', fontWeight: 600, fontSize: '12px' }}>
                        {idx > 0 && timelineData[idx - 1] ? `+${(item.score - timelineData[idx - 1].score).toFixed(1)}%` : "Baseline"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ padding: '36px 20px', textAlign: 'center', color: '#94a3b8', fontSize: '13.5px' }}>
              No interview sessions completed yet. Attempt progression will record here automatically.
            </div>
          )}
        </div>

        {/* Right: 5-Week Roadmap Action Banner */}
        <div
          className="card"
          style={{
            background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%)',
            border: '1px solid #312e81',
            borderRadius: '16px',
            padding: '24px',
            color: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Calendar size={18} color="#38bdf8" />
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Adaptive Learning Path
              </span>
            </div>

            <h4 style={{ fontSize: '19px', fontWeight: 800, lineHeight: 1.3, marginBottom: '10px', color: '#f8fafc' }}>
              {roadmap ? "5-Week Placement Action Plan" : "Personalized Roadmap Awaiting Evaluation"}
            </h4>

            <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: 1.5, marginBottom: '16px' }}>
              {roadmap
                ? `Structured schedule addressing your verified gaps in ${targetRole} with milestone tracking.`
                : "Complete Round 1 Aptitude and an Interview to generate a tailored 5-week study roadmap."}
            </p>

            {roadmap && roadmap.weekly_action_plan && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                {roadmap.weekly_action_plan.slice(0, 3).map((w, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '8px', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1e293b' }}>
                    <span style={{ fontSize: '12.5px', color: '#f1f5f9', fontWeight: 600 }}>
                      Week {w.week}: {w.theme}
                    </span>
                    <Badge variant={w.completed ? "success" : "neutral"} size="sm">
                      {w.completed ? "Done" : "Upcoming"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Button
            variant="secondary"
            onClick={() => navigate(roadmap ? '/roadmap' : '/aptitude')}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {roadmap ? "Open 5-Week Roadmap" : "Start Round 1 to Unlock Roadmap"}
          </Button>
        </div>

      </div>

    </div>
  );
}
