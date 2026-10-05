import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom';
import {
  Brain,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  HelpCircle,
  Calculator,
  Compass,
  BookOpen,
  Award,
  Zap,
  Target,
  Sparkles,
  BarChart2,
  MessageSquare
} from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { useAuth } from '../context/AuthContext';
import aptitudeService from '../services/aptitudeService';
import interviewService from '../services/interviewService';

export default function AptitudeResults() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { attemptId } = useParams();
  const location = useLocation();

  const [loading, setLoading] = useState(!location.state?.attempt);
  const [attempt, setAttempt] = useState(location.state?.attempt || null);
  const [answerLogs, setAnswerLogs] = useState([]);
  const [startingHR, setStartingHR] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch results if not provided in location state
  useEffect(() => {
    if (attempt) return;

    let isMounted = true;
    async function fetchResults() {
      try {
        setLoading(true);
        const idToFetch = attemptId || 'latest';
        let res;
        if (idToFetch === 'latest') {
          res = await aptitudeService.getLatestAptitude();
        } else {
          res = await aptitudeService.getAptitudeResults(idToFetch);
        }

        if (isMounted && res.success && res.attempt) {
          setAttempt(res.attempt);
          if (res.answerLogs) setAnswerLogs(res.answerLogs);
        } else {
          setErrorMsg("Could not locate aptitude assessment results.");
        }
      } catch (err) {
        if (isMounted) setErrorMsg(err.message || "Failed to load aptitude results.");
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchResults();

    return () => {
      isMounted = false;
    };
  }, [attemptId, attempt]);

  // Proceed directly to Round 2 — AI HR Interview
  const handleProceedToHR = async () => {
    setStartingHR(true);
    try {
      const targetRole = user?.targetRole || "Software Engineer";
      const setupRes = await interviewService.setupSession({
        roundId: "hr",
        roundType: "HR & STAR Behavioral Round",
        targetRole,
        questionCount: 4,
        difficulty: "adaptive",
        enableCamera: true,
        enableMicrophone: true
      });

      if (setupRes.success && setupRes.session) {
        navigate('/interview', {
          state: {
            session: setupRes.session,
            sessionConfig: {
              roundId: "hr",
              roundType: "Round 2: AI HR & Behavioral Interview",
              targetRole,
              currentRoundNumber: 2,
              totalRounds: 4,
              aptitudeAttemptId: attempt?.id,
              enableCamera: true,
              enableMicrophone: true
            }
          }
        });
      } else {
        // Fallback directly to interview setup
        navigate('/interview-setup');
      }
    } catch (err) {
      console.error("[AptitudeResults] Proceed to HR error:", err);
      navigate('/interview-setup');
    } finally {
      setStartingHR(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '3px solid #1f2937',
              borderTopColor: '#6366f1',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
              margin: '0 auto 16px auto'
            }}
          />
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          <p style={{ color: '#94a3b8', fontSize: '14px', fontWeight: 600 }}>Loading Aptitude Diagnostic Report...</p>
        </div>
      </div>
    );
  }

  if (!attempt) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', backgroundColor: '#111827', borderRadius: '16px', border: '1px solid #1f2937', margin: '40px auto', maxWidth: '600px' }}>
        <AlertCircle size={40} color="#f59e0b" style={{ margin: '0 auto 16px auto' }} />
        <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>No Aptitude Assessment Found</h3>
        <p style={{ fontSize: '13.5px', color: '#94a3b8', marginTop: '8px', lineHeight: 1.5 }}>
          You have not completed Round 1 Aptitude yet. Take the adaptive test to evaluate your Quantitative, Logical, and Verbal competencies.
        </p>
        <button
          onClick={() => navigate('/aptitude')}
          style={{
            marginTop: '20px',
            padding: '10px 24px',
            backgroundColor: '#6366f1',
            color: '#ffffff',
            borderRadius: '10px',
            border: 'none',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Start Round 1 Aptitude
        </button>
      </div>
    );
  }

  const overallScore = attempt.overallScore ?? 0;
  const quantScore = attempt.quantitativeScore ?? 0;
  const logicScore = attempt.reasoningScore ?? 0;
  const verbalScore = attempt.verbalScore ?? 0;
  const accuracy = attempt.accuracy ?? 0;
  const avgTime = attempt.averageResponseTime ?? 0;
  const strongTopics = attempt.strongTopics || [];
  const weakTopics = attempt.weakTopics || [];
  const diffPerf = attempt.difficultyPerformance || {};

  // Radar Data for Section Competencies
  const radarData = [
    { section: "Quantitative", score: quantScore, fullMark: 100 },
    { section: "Logical Reasoning", score: logicScore, fullMark: 100 },
    { section: "Verbal Ability", score: verbalScore, fullMark: 100 },
    { section: "Accuracy", score: accuracy, fullMark: 100 }
  ];

  // Difficulty performance bar chart data
  const diffBarData = [
    { level: "Easy", accuracy: diffPerf.Easy ? diffPerf.Easy.accuracy : 80 },
    { level: "Medium", accuracy: diffPerf.Medium ? diffPerf.Medium.accuracy : 65 },
    { level: "Hard", accuracy: diffPerf.Hard ? diffPerf.Hard.accuracy : 50 }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
      
      {/* Round 1 Banner with Hackathon Round Flow */}
      <div
        style={{
          background: 'linear-gradient(135deg, #111827 0%, #1e1b4b 60%, #311042 100%)',
          borderRadius: '20px',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          padding: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '24px',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 800, color: '#34d399', backgroundColor: 'rgba(16, 185, 129, 0.15)', padding: '3px 10px', borderRadius: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              ✓ Round 1 Completed
            </span>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>•</span>
            <span style={{ fontSize: '13px', color: '#a5b4fc', fontWeight: 600 }}>Aptitude Assessment</span>
          </div>
          <h2 style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em', margin: 0 }}>
            Round 1 Evaluation: {overallScore}%
          </h2>
          <p style={{ fontSize: '14px', color: '#cbd5e1', marginTop: '8px', maxWidth: '640px', lineHeight: 1.5 }}>
            Your cognitive reasoning, quantitative problem solving, and contextual verbal proficiency have been analyzed. Next up: <strong>Round 2 — AI HR Interview</strong> with real-time speech analysis.
          </p>
        </div>

        {/* Big Action CTA: Proceed to Round 2 */}
        <button
          onClick={handleProceedToHR}
          disabled={startingHR}
          style={{
            padding: '14px 28px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: '#ffffff',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 800,
            fontSize: '15px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            cursor: startingHR ? 'not-allowed' : 'pointer',
            boxShadow: '0 8px 24px rgba(16, 185, 129, 0.35)',
            transition: 'all 0.2s ease'
          }}
        >
          {startingHR ? (
            "Initializing Round 2..."
          ) : (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.85 }}>Next Round</span>
                <span>Round 2 — AI HR Interview</span>
              </div>
              <ArrowRight size={20} />
            </>
          )}
        </button>
      </div>

      {/* Assessment Progression Stepper */}
      <div
        style={{
          backgroundColor: '#111827',
          borderRadius: '16px',
          border: '1px solid #1f2937',
          padding: '18px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#10b981', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            ✓
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#34d399' }}>ROUND 1</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>Aptitude Assessment ({overallScore}%)</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#6366f1', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            ●
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#818cf8' }}>ROUND 2</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>AI HR Interview (Next)</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', opacity: 0.6 }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#1f2937', border: '1px solid #374151', color: '#9ca3af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            3
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#9ca3af' }}>ROUND 3</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Adaptive Technical</div>
          </div>
        </div>

        <div style={{ width: '30px', height: '1px', backgroundColor: '#374151' }} className="hidden-mobile" />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', opacity: 0.6 }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#1f2937', border: '1px solid #374151', color: '#9ca3af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: 800 }}>
            4
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#9ca3af' }}>ROUND 4</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Multimodal Final</div>
          </div>
        </div>
      </div>

      {/* 4 Key Metric Metric Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        
        {/* Card 1: Quantitative */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Quantitative Ability
            </span>
            <Calculator size={18} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#38bdf8' }}>
            {quantScore}%
          </div>
          <div style={{ width: '100%', height: '6px', backgroundColor: '#1e293b', borderRadius: '3px', marginTop: '12px', overflow: 'hidden' }}>
            <div style={{ width: `${quantScore}%`, height: '100%', backgroundColor: '#38bdf8', transition: 'width 0.4s ease' }} />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '8px', margin: 0 }}>
            Arithmetic, algebra, and problem-solving.
          </p>
        </div>

        {/* Card 2: Logical Reasoning */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Logical Reasoning
            </span>
            <Compass size={18} color="#818cf8" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#818cf8' }}>
            {logicScore}%
          </div>
          <div style={{ width: '100%', height: '6px', backgroundColor: '#1e293b', borderRadius: '3px', marginTop: '12px', overflow: 'hidden' }}>
            <div style={{ width: `${logicScore}%`, height: '100%', backgroundColor: '#818cf8', transition: 'width 0.4s ease' }} />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '8px', margin: 0 }}>
            Series, puzzles, deductions, and syllogisms.
          </p>
        </div>

        {/* Card 3: Verbal Ability */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Verbal Ability
            </span>
            <BookOpen size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399' }}>
            {verbalScore}%
          </div>
          <div style={{ width: '100%', height: '6px', backgroundColor: '#1e293b', borderRadius: '3px', marginTop: '12px', overflow: 'hidden' }}>
            <div style={{ width: `${verbalScore}%`, height: '100%', backgroundColor: '#34d399', transition: 'width 0.4s ease' }} />
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '8px', margin: 0 }}>
            Grammar, comprehension, and vocabulary.
          </p>
        </div>

        {/* Card 4: Accuracy & Pacing */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Precision & Pacing
            </span>
            <Zap size={18} color="#f59e0b" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#f59e0b' }}>
              {accuracy}%
            </div>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>accuracy</span>
          </div>
          <p style={{ fontSize: '13px', color: '#cbd5e1', marginTop: '10px', margin: 0 }}>
            Avg. time: <strong style={{ color: '#f8fafc' }}>{avgTime}s</strong> per question
          </p>
        </div>

      </div>

      {/* Visual Analytics Grid: Radar Chart + Difficulty Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '20px' }}>
        
        {/* Radar Chart: Section Profile */}
        <div
          style={{
            backgroundColor: '#111827',
            border: '1px solid #1f2937',
            borderRadius: '16px',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Aptitude Dimensional Radar
            </h3>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', marginTop: '2px' }}>
              Relative proficiency profile across tested cognitive domains.
            </p>
          </div>

          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="section" tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }} />
                <PolarRadiusAxis stroke="#4b5563" domain={[0, 100]} />
                <Radar name="Aptitude" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Difficulty Breakdown & Topic Diagnostics */}
        <div
          style={{
            backgroundColor: '#111827',
            border: '1px solid #1f2937',
            borderRadius: '16px',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '20px'
          }}
        >
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Adaptive Topic Diagnostics
            </h3>
            <p style={{ fontSize: '12.5px', color: '#94a3b8', marginTop: '2px' }}>
              Strong competencies and identified priority focus areas.
            </p>
          </div>

          {/* Strong Topics */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
              ✓ Strong Topics
            </div>
            {strongTopics.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {strongTopics.map(t => (
                  <span
                    key={typeof t === 'string' ? t : t.topic}
                    style={{
                      padding: '5px 12px',
                      backgroundColor: 'rgba(16, 185, 129, 0.15)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      borderRadius: '8px',
                      color: '#6ee7b7',
                      fontSize: '12.5px',
                      fontWeight: 600
                    }}
                  >
                    {typeof t === 'string' ? t : t.topic}
                  </span>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '12.5px', color: '#64748b', margin: 0 }}>Comprehensive practice recommended across topics.</p>
            )}
          </div>

          {/* Weak Topics */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
              ⚠ Areas Requiring Reinforcement
            </div>
            {weakTopics.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {weakTopics.map(t => (
                  <span
                    key={typeof t === 'string' ? t : t.topic}
                    style={{
                      padding: '5px 12px',
                      backgroundColor: 'rgba(239, 68, 68, 0.15)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: '8px',
                      color: '#fca5a5',
                      fontSize: '12.5px',
                      fontWeight: 600
                    }}
                  >
                    {typeof t === 'string' ? t : t.topic}
                  </span>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '12.5px', color: '#6ee7b7', margin: 0 }}>Consistent accuracy across all evaluated sections!</p>
            )}
          </div>

          {/* Next Step Action Card */}
          <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #1e293b' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
              Placement Roadmap Integration
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              Identified weak aptitude topics are automatically sequenced into your dynamic 5-week learning roadmap for targeted drill practice.
            </p>
          </div>
        </div>

      </div>

      {/* Bottom CTA Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', flexWrap: 'wrap', gap: '16px' }}>
        <button
          onClick={() => navigate('/aptitude')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#1f2937',
            color: '#f8fafc',
            borderRadius: '10px',
            border: '1px solid #374151',
            fontWeight: 600,
            fontSize: '13.5px',
            cursor: 'pointer'
          }}
        >
          Retake Aptitude Assessment
        </button>

        <button
          onClick={handleProceedToHR}
          disabled={startingHR}
          style={{
            padding: '12px 28px',
            background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
            color: '#ffffff',
            borderRadius: '10px',
            border: 'none',
            fontWeight: 700,
            fontSize: '14.5px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: startingHR ? 'not-allowed' : 'pointer',
            boxShadow: '0 6px 18px rgba(99, 102, 241, 0.35)'
          }}
        >
          <span>{startingHR ? "Starting Round 2..." : "Continue to Round 2 (AI HR Interview)"}</span>
          <ArrowRight size={17} />
        </button>
      </div>

    </div>
  );
}
