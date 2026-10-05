import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  BookOpen,
  Code,
  Layers,
  HelpCircle,
  FileQuestion,
  Target,
  Zap,
  Award,
  Play,
  Check
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';

export default function LearningRoadmap() {
  const { user, assessment } = useAuth();
  const navigate = useNavigate();

  const [completedTasks, setCompletedTasks] = useState({
    "w1_t0": true,
    "w1_t1": true
  });

  const candName = assessment?.candidate?.name || user?.name || user?.full_name || "Candidate";
  const targetRole = user?.targetRole || assessment?.job_alignment?.target_role || "Software Engineer";
  const latestAptitude = user?.latestAptitude || null;

  // Derive dynamic 5-week plan if assessment is present, or synthesize baseline from target role / aptitude
  const defaultWeeks = [
    {
      week: 1,
      theme: "Foundations & Quantitative Remediation",
      goal: `Establish algorithmic foundations and address quantitative problem-solving gaps relevant to ${targetRole}.`,
      target_topics: latestAptitude?.weakTopics?.slice(0, 2).map(w => w.topic) || ["Data Structures", "Percentages & Profit-Loss", "Core Syntax"],
      objectives: [
        "Implement fundamental memory structures (Arrays, Linked Lists, Hash Maps) from scratch.",
        "Solve 15 medium-level practice problems covering quantitative aptitude formulas.",
        "Review time & space complexity analysis (Big-O notation)."
      ],
      milestone: "Pass Week 1 Diagnostic Quiz with ≥ 75% accuracy.",
      recommended_assessment: "Round 1 Aptitude Practice Drill",
      completed: true
    },
    {
      week: 2,
      theme: "Advanced Problem Solving & Logical Reasoning",
      goal: "Master recursive paradigms, dynamic programming patterns, and analytical reasoning puzzles.",
      target_topics: ["Dynamic Programming", "Graph Traversals (BFS/DFS)", "Logical Deduction & Puzzles"],
      objectives: [
        "Implement iterative and recursive binary tree traversals.",
        "Solve 10 LeetCode Medium problems covering sliding window and two-pointer techniques.",
        "Practice 15 syllogism and seating arrangement reasoning problems."
      ],
      milestone: "Successfully implement an LRU Cache and bipartite graph check.",
      recommended_assessment: "Technical Problem-Solving Evaluation",
      completed: false
    },
    {
      week: 3,
      theme: "Communication & STAR Behavioral Mastery",
      goal: "Refine speech cadence, eliminate filler words, and structure behavioral responses with STAR methodology.",
      target_topics: ["STAR Behavioral Framework", "Speech Pacing (130-150 WPM)", "Conflict Resolution & Leadership"],
      objectives: [
        "Script and record 5 STAR responses for common behavioral prompts.",
        "Practice delivering answers via microphone with real-time Speech-to-Text transcription.",
        "Ensure concise 90-120 second responses with clear quantified impact."
      ],
      milestone: "Achieve ≥ 80% semantic relevance and STAR structure score.",
      recommended_assessment: "Round 2 AI HR Interview with STT",
      completed: false
    },
    {
      week: 4,
      theme: "Role-Specific Architecture & Systems",
      goal: `Deepen production-grade competence in ${targetRole} technologies and architecture trade-offs.`,
      target_topics: ["System Design & Caching", "Database Indexing & ACID", "Containerization & APIs"],
      objectives: [
        "Design a scalable microservices architecture incorporating Redis caching and message queues.",
        "Optimize complex SQL multi-table joins and analyze query execution plans.",
        "Containerize an application utilizing Docker multi-stage builds."
      ],
      milestone: "Complete architecture blueprint with documented latency and throughput targets.",
      recommended_assessment: "Role-Specific Technical Drill",
      completed: false
    },
    {
      week: 5,
      theme: "Full Placement Mock Interview & Polishing",
      goal: "Synthesize all modalities under timed pressure with computer vision and acoustic telemetry active.",
      target_topics: ["Multimodal Fusion", "Camera-Facing Consistency", "Adaptive Difficulty Clearance"],
      objectives: [
        "Complete a full 4-round employability simulation (Aptitude + HR + Technical + CV).",
        "Maintain upright posture stability and > 85% camera-facing gaze ratio.",
        "Review final placement readiness report and recruiter summary artifacts."
      ],
      milestone: "Achieve Tier 1 (Ready) Placement Employability Score ≥ 78%.",
      recommended_assessment: "Full Employability Placement Mock",
      completed: false
    }
  ];

  const rawPlan = assessment?.learning_roadmap?.weekly_action_plan;
  const weeks = (rawPlan && rawPlan.length === 5)
    ? rawPlan.map((w, i) => ({
        ...w,
        goal: w.milestone || defaultWeeks[i].goal,
        recommended_assessment: defaultWeeks[i].recommended_assessment
      }))
    : defaultWeeks;

  const totalHours = assessment?.learning_roadmap?.total_estimated_hours || 80;

  const toggleTask = (key) => {
    setCompletedTasks(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 8 Adaptive Learning Path
            </span>
            <Badge variant="primary">5-Week Placement Curriculum</Badge>
          </div>
          <h2 className="page-title">Personalized Employability Roadmap</h2>
          <p className="page-subtitle">
            Dynamic weekly milestone path synthesized from <strong>{candName}'s</strong> verified skill gaps, aptitude results, and <strong>{targetRole}</strong> benchmarks.
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
            icon={Play}
            onClick={() => navigate('/interview-setup')}
          >
            Practice Interview
          </Button>
        </div>
      </div>

      {/* Meta Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          padding: '20px 24px',
          background: 'linear-gradient(135deg, #111827 0%, #1e293b 100%)',
          border: '1px solid #1e293b',
          borderRadius: '16px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '12px', backgroundColor: 'rgba(14, 165, 233, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Calendar size={22} color="#38bdf8" />
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc' }}>
              Curriculum for {targetRole}
            </div>
            <div style={{ fontSize: '12.5px', color: '#94a3b8' }}>
              Estimated Investment: ~{totalHours} Guided Hours across 5 Milestone Weeks
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px', fontSize: '13px', color: '#cbd5e1' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#10b981' }} />
            Completed Modules
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#06b6d4' }} />
            Active Milestone
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#64748b' }} />
            Upcoming
          </span>
        </div>
      </div>

      {/* 5-Week Action Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {weeks.map((weekItem, idx) => {
          const isWeekCompleted = weekItem.completed || idx === 0;
          const isActive = idx === 1;

          return (
            <div
              key={idx}
              className="card"
              style={{
                position: 'relative',
                borderLeft: isWeekCompleted ? '4px solid #10b981' : isActive ? '4px solid #06b6d4' : '4px solid #334155',
                padding: '26px',
                background: '#111827',
                border: '1px solid #1e293b'
              }}
            >
              {/* Header: Week number, title, status */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: isWeekCompleted ? '#34d399' : isActive ? '#38bdf8' : '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                      WEEK {weekItem.week}
                    </span>
                    <Badge variant={isWeekCompleted ? 'success' : isActive ? 'primary' : 'neutral'} size="sm">
                      {isWeekCompleted ? 'Completed' : isActive ? 'Active Focus' : 'Upcoming'}
                    </Badge>
                  </div>
                  <h3 style={{ fontSize: '19px', fontWeight: 800, color: '#f8fafc', marginTop: '6px', margin: 0 }}>
                    {weekItem.theme}
                  </h3>
                </div>

                {/* Topic tags */}
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {weekItem.target_topics?.map((topic, i) => (
                    <span key={i} style={{ fontSize: '11.5px', padding: '4px 10px', borderRadius: '6px', backgroundColor: 'rgba(30, 41, 59, 0.8)', border: '1px solid #334155', color: '#cbd5e1', fontWeight: 600 }}>
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              {/* Goal Description */}
              <div style={{ fontSize: '13.5px', color: '#cbd5e1', lineHeight: 1.5, marginBottom: '16px' }}>
                <strong style={{ color: '#f8fafc' }}>Primary Goal: </strong>
                {weekItem.goal}
              </div>

              {/* Milestone & Recommended Assessment Row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px', marginBottom: '18px' }}>
                <div style={{ padding: '12px 14px', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid #1e293b', fontSize: '13px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '2px' }}>
                    Target Milestone
                  </div>
                  <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{weekItem.milestone}</span>
                </div>

                <div style={{ padding: '12px 14px', backgroundColor: 'rgba(99, 102, 241, 0.08)', borderRadius: '10px', border: '1px solid rgba(99, 102, 241, 0.25)', fontSize: '13px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', marginBottom: '2px' }}>
                      Recommended Assessment
                    </div>
                    <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{weekItem.recommended_assessment}</span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      if (weekItem.recommended_assessment.includes('Aptitude')) navigate('/aptitude');
                      else navigate('/interview-setup');
                    }}
                  >
                    Start
                  </Button>
                </div>
              </div>

              {/* Practice Tasks */}
              <div>
                <div style={{ fontSize: '12px', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '10px' }}>
                  Practice Deliverables
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {weekItem.objectives?.map((obj, i) => {
                    const taskKey = `w${weekItem.week}_t${i}`;
                    const isChecked = completedTasks[taskKey] || (isWeekCompleted && completedTasks[taskKey] !== false);

                    return (
                      <div
                        key={i}
                        onClick={() => toggleTask(taskKey)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          padding: '10px 14px',
                          borderRadius: '8px',
                          backgroundColor: isChecked ? 'rgba(16, 185, 129, 0.06)' : 'rgba(30, 41, 59, 0.4)',
                          border: isChecked ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid #1e293b',
                          fontSize: '13px',
                          color: isChecked ? '#94a3b8' : '#f1f5f9',
                          textDecoration: isChecked ? 'line-through' : 'none',
                          cursor: 'pointer',
                          userSelect: 'none',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={!!isChecked}
                          onChange={() => {}}
                          style={{ accentColor: '#06b6d4', width: '16px', height: '16px', cursor: 'pointer' }}
                        />
                        <span>{obj}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
