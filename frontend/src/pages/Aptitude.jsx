import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Brain,
  Clock,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  ChevronLeft,
  Send,
  HelpCircle,
  Calculator,
  Compass,
  BookOpen,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import aptitudeService from '../services/aptitudeService';

export default function Aptitude() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const [attemptId, setAttemptId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);

  // answers map: question_id -> { selected_option, time_taken_seconds }
  const [answers, setAnswers] = useState({});
  const [flagged, setFlagged] = useState({});

  // Timers
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [questionSeconds, setQuestionSeconds] = useState(0);

  // Active section filter tab: 'all' | 'Quantitative Ability' | 'Logical Reasoning' | 'Verbal Ability'
  const [activeSection, setActiveSection] = useState('Quantitative Ability');

  // Submit confirmation modal
  const [showSubmitModal, setShowSubmitModal] = useState(false);

  // Fetch or initialize aptitude test on mount
  useEffect(() => {
    let isMounted = true;

    async function initTest() {
      try {
        setLoading(true);
        setErrorMsg('');

        // If an existing attemptId was passed in location.state
        const existingAttemptId = location.state?.attemptId;

        let res;
        if (existingAttemptId) {
          res = await aptitudeService.getAttemptQuestions(existingAttemptId);
          if (isMounted && res.success && res.questions) {
            setAttemptId(res.attemptId);
            setQuestions(res.questions);
            return;
          }
        }

        // Otherwise start fresh attempt
        const startRes = await aptitudeService.startAptitude({
          sessionId: location.state?.sessionId || null,
          questionsPerSection: 5
        });

        if (isMounted && startRes.success && startRes.questions) {
          setAttemptId(startRes.attemptId);
          setQuestions(startRes.questions);
        } else {
          setErrorMsg("Could not load aptitude questions. Please retry.");
        }
      } catch (err) {
        if (isMounted) {
          setErrorMsg(err.message || "Failed to initialize Round 1 Aptitude test.");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    initTest();

    return () => {
      isMounted = false;
    };
  }, [location.state]);

  // Overall and question-wise timer tick
  useEffect(() => {
    if (loading || submitting || questions.length === 0) return;

    const timer = setInterval(() => {
      setTotalSeconds(prev => prev + 1);
      setQuestionSeconds(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [loading, submitting, questions.length]);

  const currentQ = questions[currentIdx] || null;

  // Record answer selection
  const handleSelectOption = (opt) => {
    if (!currentQ) return;
    setAnswers(prev => ({
      ...prev,
      [currentQ.id]: {
        selected_option: opt,
        time_taken_seconds: (prev[currentQ.id]?.time_taken_seconds || 0) + questionSeconds
      }
    }));
    setQuestionSeconds(0);
  };

  const handleClearOption = () => {
    if (!currentQ) return;
    setAnswers(prev => {
      const copy = { ...prev };
      delete copy[currentQ.id];
      return copy;
    });
  };

  const toggleFlag = (qId) => {
    setFlagged(prev => ({
      ...prev,
      [qId]: !prev[qId]
    }));
  };

  const goToQuestion = (idx) => {
    if (currentQ) {
      // Accumulate elapsed seconds on current question
      setAnswers(prev => {
        if (prev[currentQ.id]) {
          return {
            ...prev,
            [currentQ.id]: {
              ...prev[currentQ.id],
              time_taken_seconds: (prev[currentQ.id].time_taken_seconds || 0) + questionSeconds
            }
          };
        }
        return prev;
      });
    }
    setQuestionSeconds(0);
    setCurrentIdx(idx);
    if (questions[idx]) {
      setActiveSection(questions[idx].section);
    }
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      goToQuestion(currentIdx + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      goToQuestion(currentIdx - 1);
    }
  };

  // Submit Aptitude Assessment
  const handleSubmitTest = async () => {
    if (submitting || !attemptId) return;

    setSubmitting(true);
    setErrorMsg('');

    try {
      // Format answers for submission
      const answerEntries = questions.map(q => {
        const recorded = answers[q.id];
        return {
          question_id: q.id,
          selected_option: recorded ? recorded.selected_option : null,
          time_taken_seconds: recorded ? recorded.time_taken_seconds : 0.0
        };
      });

      const res = await aptitudeService.submitAptitude({
        attemptId,
        answers: answerEntries
      });

      if (res.success && res.attempt) {
        navigate(`/aptitude/results/${attemptId}`, {
          state: {
            attempt: res.attempt,
            evaluation: res.evaluation,
            nextRound: res.nextRound
          }
        });
      } else {
        setErrorMsg("Failed to submit aptitude answers. Please try again.");
      }
    } catch (err) {
      setErrorMsg(err.message || "An error occurred during submission.");
    } finally {
      setSubmitting(false);
      setShowSubmitModal(false);
    }
  };

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Section stats
  const sectionsList = [
    { name: "Quantitative Ability", icon: Calculator, color: "#38bdf8" },
    { name: "Logical Reasoning", icon: Compass, color: "#818cf8" },
    { name: "Verbal Ability", icon: BookOpen, color: "#34d399" }
  ];

  const sectionQuestions = questions.filter(q => q.section === activeSection);
  const attemptedCount = Object.keys(answers).length;
  const unattemptedCount = Math.max(0, questions.length - attemptedCount);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#090d16', color: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              border: '3px solid #1f2937',
              borderTopColor: '#6366f1',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
              margin: '0 auto 16px auto'
            }}
          />
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          <h3 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Generating Adaptive Aptitude Round...</h3>
          <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '6px' }}>
            Randomizing balanced Quantitative, Logical, and Verbal questions.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#090d16', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* Top Test Header Bar */}
      <header
        style={{
          height: '68px',
          padding: '0 28px',
          backgroundColor: '#0f172a',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 40
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.35)'
            }}
          >
            <Brain size={20} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: 800, color: '#f8fafc' }}>
                Round 1: Aptitude Assessment
              </span>
              <span style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.15)', padding: '2px 8px', borderRadius: '4px', textTransform: 'uppercase' }}>
                Adaptive
              </span>
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0 }}>
              Quantitative Ability • Logical Reasoning • Verbal Ability
            </p>
          </div>
        </div>

        {/* Center Live Timer */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '7px 16px',
            backgroundColor: '#1e293b',
            borderRadius: '10px',
            border: '1px solid #334155'
          }}
        >
          <Clock size={16} color="#38bdf8" />
          <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 500 }}>Time Elapsed:</span>
          <span style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc', fontVariantNumeric: 'tabular-nums' }}>
            {formatTimer(totalSeconds)}
          </span>
        </div>

        {/* Right Action: Finish & Submit */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ textAlign: 'right' }} className="hidden-mobile">
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>Answered:</span>{' '}
            <strong style={{ fontSize: '13px', color: '#34d399' }}>{attemptedCount}</strong>
            <span style={{ fontSize: '12px', color: '#64748b' }}> / {questions.length}</span>
          </div>
          <button
            onClick={() => setShowSubmitModal(true)}
            style={{
              padding: '9px 20px',
              backgroundColor: '#6366f1',
              color: '#ffffff',
              borderRadius: '9px',
              border: 'none',
              fontWeight: 700,
              fontSize: '13.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)'
            }}
          >
            <span>Submit Round 1</span>
            <Send size={14} />
          </button>
        </div>
      </header>

      {/* Main Test Layout (3 Columns: Section Tabs, Question Arena, Question Navigator) */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        
        {/* Left Arena: Question View & Options */}
        <main style={{ flex: 1, padding: '28px 36px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
          
          {/* Section Selector Tabs */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', flexWrap: 'wrap' }}>
            {sectionsList.map(sec => {
              const Icon = sec.icon;
              const isActive = activeSection === sec.name;
              const secQs = questions.filter(q => q.section === sec.name);
              const secAnsCount = secQs.filter(q => !!answers[q.id]).length;

              return (
                <button
                  key={sec.name}
                  onClick={() => {
                    setActiveSection(sec.name);
                    const firstInSec = questions.findIndex(q => q.section === sec.name);
                    if (firstInSec !== -1) goToQuestion(firstInSec);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '9px 16px',
                    borderRadius: '10px',
                    backgroundColor: isActive ? 'rgba(99, 102, 241, 0.15)' : '#111827',
                    border: isActive ? '1.5px solid #6366f1' : '1px solid #1f2937',
                    color: isActive ? '#a5b4fc' : '#9ca3af',
                    fontWeight: 700,
                    fontSize: '13px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <Icon size={15} color={isActive ? sec.color : '#6b7280'} />
                  <span>{sec.name}</span>
                  <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', backgroundColor: isActive ? 'rgba(99, 102, 241, 0.3)' : '#1f2937', color: '#f8fafc' }}>
                    {secAnsCount}/{secQs.length}
                  </span>
                </button>
              );
            })}
          </div>

          {errorMsg && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '13px', marginBottom: '20px' }}>
              <AlertCircle size={16} color="#ef4444" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Current Question Card */}
          {currentQ ? (
            <div
              style={{
                backgroundColor: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '16px',
                padding: '30px',
                display: 'flex',
                flexDirection: 'column',
                gap: '24px',
                boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35)'
              }}
            >
              {/* Question Header & Meta */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '13px', fontWeight: 800, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Question {currentIdx + 1} of {questions.length}
                  </span>
                  <span style={{ fontSize: '11px', fontWeight: 600, color: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                    {currentQ.topic}
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      backgroundColor: currentQ.difficulty === 'Easy' ? 'rgba(16, 185, 129, 0.15)' : currentQ.difficulty === 'Hard' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: currentQ.difficulty === 'Easy' ? '#34d399' : currentQ.difficulty === 'Hard' ? '#f87171' : '#fbbf24'
                    }}
                  >
                    {currentQ.difficulty}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    type="button"
                    onClick={() => toggleFlag(currentQ.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      backgroundColor: flagged[currentQ.id] ? 'rgba(245, 158, 11, 0.2)' : 'transparent',
                      border: flagged[currentQ.id] ? '1px solid #f59e0b' : '1px solid #374151',
                      color: flagged[currentQ.id] ? '#fbbf24' : '#9ca3af',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    <span>{flagged[currentQ.id] ? "★ Flagged for Review" : "☆ Flag Question"}</span>
                  </button>
                </div>
              </div>

              {/* Question Text */}
              <div style={{ fontSize: '17px', fontWeight: 600, color: '#f8fafc', lineHeight: 1.6 }}>
                {currentQ.question}
              </div>

              {/* Options List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {currentQ.options.map((opt, optIdx) => {
                  const optionLetters = ['A', 'B', 'C', 'D', 'E'];
                  const letter = optionLetters[optIdx] || String(optIdx + 1);
                  const isSelected = answers[currentQ.id]?.selected_option === opt;

                  return (
                    <div
                      key={opt}
                      onClick={() => handleSelectOption(opt)}
                      style={{
                        padding: '14px 18px',
                        borderRadius: '12px',
                        backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : '#0f172a',
                        border: isSelected ? '1.5px solid #6366f1' : '1px solid #1f2937',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '14px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        boxShadow: isSelected ? '0 0 0 2px rgba(99, 102, 241, 0.25)' : 'none'
                      }}
                    >
                      <div
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '8px',
                          backgroundColor: isSelected ? '#6366f1' : '#1e293b',
                          color: '#ffffff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: '13px',
                          flexShrink: 0
                        }}
                      >
                        {letter}
                      </div>
                      <span style={{ fontSize: '15px', color: isSelected ? '#ffffff' : '#e2e8f0', fontWeight: isSelected ? 600 : 400 }}>
                        {opt}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Navigation & Clear Selection */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #1f2937', paddingTop: '18px', marginTop: '10px' }}>
                <div>
                  {answers[currentQ.id] && (
                    <button
                      type="button"
                      onClick={handleClearOption}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: '#94a3b8',
                        fontSize: '12.5px',
                        cursor: 'pointer',
                        padding: '4px 8px'
                      }}
                    >
                      <RotateCcw size={13} />
                      <span>Clear Response</span>
                    </button>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    type="button"
                    disabled={currentIdx === 0}
                    onClick={handlePrev}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: currentIdx === 0 ? '#1e293b' : '#1f2937',
                      color: currentIdx === 0 ? '#4b5563' : '#f8fafc',
                      borderRadius: '8px',
                      border: '1px solid #374151',
                      fontSize: '13px',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      cursor: currentIdx === 0 ? 'not-allowed' : 'pointer'
                    }}
                  >
                    <ChevronLeft size={16} />
                    <span>Previous</span>
                  </button>

                  {currentIdx < questions.length - 1 ? (
                    <button
                      type="button"
                      onClick={handleNext}
                      style={{
                        padding: '8px 18px',
                        backgroundColor: '#6366f1',
                        color: '#ffffff',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '13px',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        cursor: 'pointer'
                      }}
                    >
                      <span>Next Question</span>
                      <ChevronRight size={16} />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setShowSubmitModal(true)}
                      style={{
                        padding: '8px 20px',
                        backgroundColor: '#10b981',
                        color: '#ffffff',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '13px',
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        cursor: 'pointer'
                      }}
                    >
                      <span>Review & Submit</span>
                      <Send size={14} />
                    </button>
                  )}
                </div>
              </div>

            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
              No questions found for this test.
            </div>
          )}

        </main>

        {/* Right Sidebar: Question Palette & Progress Map */}
        <aside
          style={{
            width: '280px',
            backgroundColor: '#0f172a',
            borderLeft: '1px solid #1e293b',
            padding: '24px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }}
          className="hidden-mobile"
        >
          <div>
            <h4 style={{ fontSize: '14px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
              Question Palette
            </h4>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
              Click any question number to jump directly.
            </p>
          </div>

          {/* Legend */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', color: '#94a3b8' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '3px', backgroundColor: '#10b981' }} />
              <span>Answered</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '3px', backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <span>Unattempted</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '3px', backgroundColor: '#f59e0b' }} />
              <span>Flagged</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '3px', border: '2px solid #6366f1' }} />
              <span>Current</span>
            </div>
          </div>

          {/* Palette Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', overflowY: 'auto' }}>
            {questions.map((q, idx) => {
              const isAnswered = !!answers[q.id];
              const isCurrent = idx === currentIdx;
              const isFlagged = !!flagged[q.id];

              let bg = '#111827';
              let textCol = '#9ca3af';
              let border = '1px solid #1f2937';

              if (isAnswered) {
                bg = 'rgba(16, 185, 129, 0.2)';
                textCol = '#34d399';
                border = '1px solid #10b981';
              }
              if (isFlagged) {
                bg = 'rgba(245, 158, 11, 0.2)';
                textCol = '#fbbf24';
                border = '1px solid #f59e0b';
              }
              if (isCurrent) {
                border = '2px solid #6366f1';
              }

              return (
                <button
                  key={q.id}
                  onClick={() => goToQuestion(idx)}
                  style={{
                    height: '38px',
                    borderRadius: '8px',
                    backgroundColor: bg,
                    border,
                    color: textCol,
                    fontWeight: 700,
                    fontSize: '13px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>

          {/* Diagnostic Note */}
          <div style={{ padding: '14px', backgroundColor: '#111827', borderRadius: '10px', border: '1px solid #1f2937', marginTop: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#818cf8', fontSize: '12px', fontWeight: 700 }}>
              <ShieldCheck size={14} />
              <span>Adaptive Scoring</span>
            </div>
            <p style={{ fontSize: '11px', color: '#94a3b8', margin: '4px 0 0 0', lineHeight: 1.4 }}>
              Difficulty progresses based on topic precision. Results directly guide your personalized improvement roadmap.
            </p>
          </div>
        </aside>

      </div>

      {/* Final Submit Confirmation Modal */}
      {showSubmitModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '20px'
          }}
        >
          <div
            style={{
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: '18px',
              padding: '28px',
              width: '100%',
              maxWidth: '460px',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Brain size={22} color="#818cf8" />
              </div>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                  Submit Round 1 Aptitude?
                </h3>
                <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: '2px 0 0 0' }}>
                  Confirm submission to evaluate section-wise scores.
                </p>
              </div>
            </div>

            {/* Summary Counters */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
              <div style={{ padding: '14px', backgroundColor: '#0f172a', borderRadius: '10px', border: '1px solid #1f2937', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: '#34d399' }}>{attemptedCount}</div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>Questions Answered</div>
              </div>
              <div style={{ padding: '14px', backgroundColor: '#0f172a', borderRadius: '10px', border: '1px solid #1f2937', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: unattemptedCount > 0 ? '#f59e0b' : '#94a3b8' }}>
                  {unattemptedCount}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>Unattempted</div>
              </div>
            </div>

            <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: 1.5, marginBottom: '24px' }}>
              Upon submission, your section-wise accuracy, response times, and topic strengths will be evaluated. You will proceed to <strong>Round 2: AI HR Interview</strong>.
            </p>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={() => setShowSubmitModal(false)}
                style={{
                  padding: '10px 18px',
                  backgroundColor: '#1f2937',
                  color: '#e2e8f0',
                  borderRadius: '10px',
                  border: '1px solid #374151',
                  fontWeight: 600,
                  fontSize: '13.5px',
                  cursor: 'pointer'
                }}
              >
                Back to Questions
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={handleSubmitTest}
                style={{
                  padding: '10px 22px',
                  background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                  color: '#ffffff',
                  borderRadius: '10px',
                  border: 'none',
                  fontWeight: 700,
                  fontSize: '13.5px',
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {submitting ? "Scoring Round 1..." : "Confirm & Complete"}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
