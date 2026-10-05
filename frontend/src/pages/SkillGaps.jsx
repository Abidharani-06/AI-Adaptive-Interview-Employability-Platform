import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layers,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Filter,
  BookOpen,
  Sparkles,
  ExternalLink,
  FileQuestion,
  Target,
  Zap,
  TrendingUp,
  ShieldAlert
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';

// Actionable recommendation mapping derived from Phase 8 curriculum database
const RECOMMENDED_ACTIONS = {
  "data structures": "Practice arrays, linked lists, binary search trees, and graph cycle detection problems on LeetCode/HackerRank.",
  "algorithms": "Master time/space Big-O analysis, dynamic programming memoization, and BFS/DFS graph traversals.",
  "sql": "Practice complex multi-table INNER/LEFT joins, GROUP BY aggregations, and window functions (ROW_NUMBER, RANK).",
  "dbms": "Study ACID transaction isolation levels, 1NF to BCNF normalization, and B-Tree vs Hash indexing trade-offs.",
  "python": "Build modular object-oriented applications utilizing generators, decorators, and asynchronous programming with asyncio.",
  "machine learning": "Implement end-to-end scikit-learn pipelines with cross-validation, feature scaling, and ROC-AUC evaluation.",
  "deep learning": "Train convolutional and recurrent architectures using PyTorch/TensorFlow with early stopping and learning rate scheduling.",
  "docker": "Containerize multi-tier web applications using multi-stage Dockerfiles and compose orchestration with Redis and Postgres.",
  "kubernetes": "Deploy microservice clusters with Horizontal Pod Autoscaling, Ingress controllers, and health probes.",
  "system design": "Design scalable architectures handling horizontal scaling, database sharding, caching strategies, and CDN delivery.",
  "communication": "Structure responses using the STAR method (Situation, Task, Action, Result) with 120-150 WPM cadence.",
  "quantitative": "Review percentage shortcuts, time-speed-distance ratios, and work-rate algebra formulas.",
  "logical reasoning": "Practice blood relations, circular seating arrangements, and coding-decoding puzzle patterns.",
  "verbal ability": "Review subject-verb agreement rules, sentence correction idioms, and active-to-passive voice transformations."
};

function getRecommendationForSkill(skillName, priority) {
  const clean = (skillName || "").toLowerCase();
  for (const [key, action] of Object.entries(RECOMMENDED_ACTIONS)) {
    if (clean.includes(key) || key.includes(clean)) {
      return action;
    }
  }
  if (priority === 'HIGH') {
    return `Review foundational theory and implement 5 core practice projects targeting ${skillName} deliverables.`;
  }
  if (priority === 'MEDIUM') {
    return `Deepen practical competence in ${skillName} through intermediate problem-solving and documentation review.`;
  }
  return `Review best practices and syntax reference for ${skillName} to ensure placement interview fluency.`;
}

function getLevelsForPriority(priority, isCore) {
  if (priority === 'HIGH') {
    return {
      current: 'Weak / Novice',
      required: isCore ? 'Strong / Advanced' : 'Proficient',
      gap: 'High (Immediate Action Required)',
      badgeColor: '#f43f5e'
    };
  }
  if (priority === 'MEDIUM') {
    return {
      current: 'Developing / Basic',
      required: 'Proficient / Intermediate',
      gap: 'Moderate (Recommended)',
      badgeColor: '#f59e0b'
    };
  }
  return {
    current: 'Intermediate',
    required: 'Working Knowledge',
    gap: 'Low (Elective Optimization)',
    badgeColor: '#38bdf8'
  };
}

export default function SkillGaps() {
  const { user, assessment } = useAuth();
  const navigate = useNavigate();

  const [filter, setFilter] = useState('ALL');

  const targetRole = user?.targetRole || assessment?.job_alignment?.target_role || "Not selected";
  
  // Synthesize skill gaps from assessment or from user job description missing skills
  const rawGaps = assessment?.skill_gaps || {
    total_gaps: user?.jobDescription?.missingSkills?.length || 0,
    high_priority_count: Math.min(3, user?.jobDescription?.missingSkills?.length || 0),
    medium_priority_count: Math.max(0, (user?.jobDescription?.missingSkills?.length || 0) - 3),
    low_priority_count: 0,
    prioritized_gaps: (user?.jobDescription?.missingSkills || []).map((skill, idx) => ({
      skill,
      priority: idx < 3 ? "HIGH" : idx < 6 ? "MEDIUM" : "LOW",
      reason: idx < 3 ? `Core foundational skill required for ${targetRole} deliverables.` : "Secondary role proficiency required by benchmark JD.",
      is_core: idx < 3,
      target: idx < 3 ? "Advanced" : "Intermediate"
    }))
  };

  const allGaps = rawGaps.prioritized_gaps || [];

  if (allGaps.length === 0 && !assessment) {
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
          No Skill Gaps Identified Yet
        </h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', maxWidth: '460px', marginBottom: '24px', lineHeight: 1.5 }}>
          Upload your technical resume and configure your target role to generate prioritized skill gap recommendations.
        </p>
        <Button variant="primary" icon={Sparkles} onClick={() => navigate('/resume')}>
          Upload Resume to Extract Gaps
        </Button>
      </div>
    );
  }

  const highGaps = allGaps.filter(g => g.priority === 'HIGH');
  const mediumGaps = allGaps.filter(g => g.priority === 'MEDIUM');
  const lowGaps = allGaps.filter(g => g.priority === 'LOW');

  const filteredGaps = filter === 'ALL'
    ? allGaps
    : allGaps.filter(g => g.priority === filter);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 8 Skill Gap Prioritization
            </span>
            <Badge variant="primary">Target: {targetRole}</Badge>
          </div>
          <h2 className="page-title">Candidate Skill Gap Intelligence</h2>
          <p className="page-subtitle">
            Classified into High, Medium, and Low priority gaps with concrete practice recommendations.
          </p>
        </div>
        <Button
          variant="primary"
          icon={ArrowRight}
          iconPosition="right"
          onClick={() => navigate('/roadmap')}
        >
          View 5-Week Action Plan
        </Button>
      </div>

      {/* KPI Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        
        {/* Total Gaps */}
        <div className="card" style={{ borderLeft: '4px solid #06b6d4', padding: '20px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Total Gaps Detected
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', marginTop: '4px' }}>
            {allGaps.length}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            Across tech, aptitude & delivery
          </div>
        </div>

        {/* High Priority */}
        <div className="card" style={{ borderLeft: '4px solid #f43f5e', padding: '20px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            High Priority (Immediate)
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: '#f43f5e', marginTop: '4px' }}>
            {highGaps.length}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            Mandatory for placement clearance
          </div>
        </div>

        {/* Medium Priority */}
        <div className="card" style={{ borderLeft: '4px solid #f59e0b', padding: '20px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Medium Priority
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: '#f59e0b', marginTop: '4px' }}>
            {mediumGaps.length}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            Secondary role proficiencies
          </div>
        </div>

        {/* Low Priority */}
        <div className="card" style={{ borderLeft: '4px solid #38bdf8', padding: '20px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Low Priority
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
            {lowGaps.length}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            Elective / Polish areas
          </div>
        </div>

      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {[
          { id: 'ALL', label: `All Gaps (${allGaps.length})` },
          { id: 'HIGH', label: `High Priority (${highGaps.length})` },
          { id: 'MEDIUM', label: `Medium Priority (${mediumGaps.length})` },
          { id: 'LOW', label: `Low Priority (${lowGaps.length})` }
        ].map((item) => (
          <button
            key={item.id}
            onClick={() => setFilter(item.id)}
            style={{
              padding: '8px 18px',
              borderRadius: '8px',
              border: filter === item.id ? '1px solid var(--primary)' : '1px solid #1e293b',
              backgroundColor: filter === item.id ? 'var(--primary)' : '#111827',
              color: filter === item.id ? '#090d16' : '#cbd5e1',
              fontSize: '13px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Gaps List Cards (Requirement 20: Current level, Required level, Gap, Reason, Recommended action) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {filteredGaps.map((gap, idx) => {
          const isCore = gap.is_core || gap.priority === 'HIGH';
          const levels = getLevelsForPriority(gap.priority, isCore);
          const recommendation = getRecommendationForSkill(gap.skill, gap.priority);

          return (
            <div
              key={idx}
              className="card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                padding: '24px',
                borderTop: gap.priority === 'HIGH' 
                  ? '3px solid #f43f5e' 
                  : gap.priority === 'MEDIUM' 
                  ? '3px solid #f59e0b' 
                  : '3px solid #38bdf8'
              }}
            >
              <div>
                {/* Header row: Skill title + Priority badge */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', textTransform: 'capitalize' }}>
                      {gap.skill}
                    </span>
                    {isCore && (
                      <span style={{ fontSize: '10.5px', padding: '2px 8px', borderRadius: '4px', backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', fontWeight: 700 }}>
                        Core Required
                      </span>
                    )}
                  </div>
                  <Badge variant={gap.priority === 'HIGH' ? 'danger' : gap.priority === 'MEDIUM' ? 'warning' : 'primary'}>
                    {gap.priority} PRIORITY
                  </Badge>
                </div>

                {/* Reason */}
                <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: 1.5, margin: 0, marginBottom: '16px' }}>
                  {gap.reason}
                </p>

                {/* Level Matrix: Current, Required, Gap */}
                <div style={{ padding: '14px', borderRadius: '10px', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px', fontSize: '12.5px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8' }}>Current Level:</span>
                    <strong style={{ color: '#f43f5e' }}>{levels.current}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8' }}>Required Level:</span>
                    <strong style={{ color: '#34d399' }}>{levels.required}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#94a3b8' }}>Gap Severity:</span>
                    <strong style={{ color: levels.badgeColor }}>{levels.gap}</strong>
                  </div>
                </div>

                {/* Recommended Action */}
                <div style={{ padding: '12px 14px', borderRadius: '10px', backgroundColor: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 800, color: '#818cf8', textTransform: 'uppercase', marginBottom: '4px' }}>
                    <Sparkles size={13} /> Recommended Action
                  </div>
                  <p style={{ fontSize: '12.5px', color: '#e2e8f0', margin: 0, lineHeight: 1.45 }}>
                    {recommendation}
                  </p>
                </div>
              </div>

              {/* Bottom footer: Roadmap link */}
              <div style={{ marginTop: '20px', paddingTop: '14px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600 }}>
                  Integrated in 5-Week Roadmap
                </span>
                <button
                  onClick={() => navigate('/roadmap')}
                  style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12.5px' }}
                >
                  Action Plan <ArrowRight size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
