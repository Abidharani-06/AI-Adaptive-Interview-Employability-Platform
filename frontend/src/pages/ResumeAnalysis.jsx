import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Briefcase,
  GraduationCap,
  Layers,
  Code,
  Check,
  X,
  FileCheck,
  AlertCircle,
  HelpCircle,
  Target
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';

const STANDARD_ROLES = [
  "VLSI Design Engineer",
  "Embedded Systems Engineer",
  "AI/ML Engineer",
  "Data Scientist",
  "Data Analyst",
  "Cloud Engineer",
  "DevOps Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Software Engineer",
  "Cybersecurity Engineer",
  "Other / Custom Role"
];

export default function ResumeAnalysis() {
  const { user, uploadResume, parseResumeText, updateJobDescription, updateTargetRole } = useAuth();
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [resumeTextInput, setResumeTextInput] = useState('');
  const [useTextInput, setUseTextInput] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [updatingJD, setUpdatingJD] = useState(false);
  const [savingRole, setSavingRole] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [toast, setToast] = useState({ type: '', message: '' });

  // Target role selection state
  const [selectedRole, setSelectedRole] = useState(user?.targetRole || "");
  const [customRole, setCustomRole] = useState(
    user?.targetRole && !STANDARD_ROLES.slice(0, -1).includes(user.targetRole)
      ? user.targetRole
      : ""
  );

  // Job Description state
  const [jobTitle, setJobTitle] = useState(user?.jobDescription?.title || user?.targetRole || "");
  const [jobDescription, setJobDescription] = useState(
    user?.jobDescription?.text || ""
  );

  // Sync with user context updates
  useEffect(() => {
    if (user?.targetRole) {
      if (STANDARD_ROLES.slice(0, -1).includes(user.targetRole)) {
        setSelectedRole(user.targetRole);
      } else {
        setSelectedRole("Other / Custom Role");
        setCustomRole(user.targetRole);
      }
      if (!jobTitle) setJobTitle(user.targetRole);
    }
  }, [user?.targetRole]);

  useEffect(() => {
    if (user?.jobDescription) {
      setJobTitle(user.jobDescription.title || "");
      setJobDescription(user.jobDescription.text || "");
    }
  }, [user?.jobDescription]);

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast({ type: '', message: '' }), 4000);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Upload or parse resume
  const handleAnalyzeResume = async () => {
    setAnalyzing(true);
    try {
      let res;
      if (useTextInput) {
        if (!resumeTextInput.trim()) {
          showToast('error', 'Please enter or paste your resume text first.');
          setAnalyzing(false);
          return;
        }
        res = await parseResumeText(resumeTextInput, "Pasted_Resume.txt");
      } else {
        if (!file) {
          showToast('error', 'Please select or drop a PDF resume file.');
          setAnalyzing(false);
          return;
        }
        res = await uploadResume(file);
      }

      if (res.success) {
        showToast('success', res.message || 'Resume parsed successfully!');
        // If user hasn't selected a role, and AI suggested one, we don't force it, but offer it!
      } else {
        showToast('error', res.error || 'Failed to parse resume.');
      }
    } catch (err) {
      showToast('error', err.message || 'An error occurred during resume analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Explicitly save selected target role
  const handleSaveRole = async () => {
    const roleToSave = selectedRole === "Other / Custom Role" ? customRole.trim() : selectedRole;
    if (!roleToSave) {
      showToast('error', 'Please select or enter a target role.');
      return;
    }
    setSavingRole(true);
    try {
      const res = await updateTargetRole(roleToSave);
      if (res.success) {
        showToast('success', `Target role set to: ${roleToSave}`);
        setJobTitle(roleToSave);
      } else {
        showToast('error', res.error || 'Failed to update target role.');
      }
    } catch (err) {
      showToast('error', err.message);
    } finally {
      setSavingRole(false);
    }
  };

  // Accept AI suggested role
  const handleUseSuggestedRole = async (suggestedRole) => {
    setSelectedRole(
      STANDARD_ROLES.slice(0, -1).includes(suggestedRole) ? suggestedRole : "Other / Custom Role"
    );
    if (!STANDARD_ROLES.slice(0, -1).includes(suggestedRole)) {
      setCustomRole(suggestedRole);
    }
    setSavingRole(true);
    try {
      const res = await updateTargetRole(suggestedRole);
      if (res.success) {
        showToast('success', `Target role updated to AI suggested role: ${suggestedRole}`);
        setJobTitle(suggestedRole);
      } else {
        showToast('error', res.error || 'Failed to apply suggested role.');
      }
    } catch (err) {
      showToast('error', err.message);
    } finally {
      setSavingRole(false);
    }
  };

  // Match Job Description against extracted skills
  const handleCompareJD = async () => {
    const effectiveRole = selectedRole === "Other / Custom Role" ? customRole.trim() : selectedRole;
    const effectiveTitle = jobTitle.trim() || effectiveRole || "Target Role";
    
    if (!jobDescription.trim()) {
      showToast('error', 'Please enter a job description to compare requirements.');
      return;
    }

    setUpdatingJD(true);
    try {
      const res = await updateJobDescription(effectiveTitle, jobDescription, effectiveRole || null);
      if (res.success) {
        showToast('success', `Job requirements compared! Compatibility score: ${res.matchScore}%`);
      } else {
        showToast('error', res.error || 'Failed to compare job description.');
      }
    } catch (err) {
      showToast('error', err.message);
    } finally {
      setUpdatingJD(false);
    }
  };

  const candResume = user?.resume;
  const candJD = user?.jobDescription;
  const aiSuggestedRole = candResume?.aiSuggestedRole;
  const currentTargetRole = user?.targetRole;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h2 className="page-title">Resume & Job Description Analysis</h2>
          <p className="page-subtitle">
            Extract candidate technical competencies, projects, and analyze role alignment (Phases 2 & 3).
          </p>
        </div>
        <Button
          variant="primary"
          icon={ArrowRight}
          iconPosition="right"
          onClick={() => navigate('/interview-setup')}
        >
          Configure Mock Interview
        </Button>
      </div>

      {/* Notification Toast */}
      {toast.message && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 16px',
            backgroundColor: toast.type === 'error' ? '#fef2f2' : '#f0fdf4',
            border: `1px solid ${toast.type === 'error' ? '#fecaca' : '#bbf7d0'}`,
            borderRadius: '10px',
            color: toast.type === 'error' ? '#b91c1c' : '#166534',
            fontSize: '13.5px'
          }}
        >
          {toast.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Target Role & AI Suggestion Banner */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid #e2e8f0',
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              backgroundColor: currentTargetRole ? '#e0e7ff' : '#f1f5f9',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: currentTargetRole ? '#4338ca' : '#64748b'
            }}
          >
            <Target size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Target Role Status
            </div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: currentTargetRole ? 'var(--primary)' : '#64748b' }}>
              {currentTargetRole ? currentTargetRole : "Not selected"}
            </div>
          </div>
        </div>

        {/* AI Suggested Role Action Pill */}
        {aiSuggestedRole && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 16px',
              backgroundColor: '#eff6ff',
              borderRadius: '10px',
              border: '1px solid #bfdbfe'
            }}
          >
            <div>
              <span style={{ fontSize: '11px', fontWeight: 700, color: '#1e40af', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Sparkles size={12} /> AI Suggested Role
              </span>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#1e3a8a' }}>
                {aiSuggestedRole}
              </div>
            </div>
            {currentTargetRole !== aiSuggestedRole && (
              <Button
                variant="primary"
                size="sm"
                loading={savingRole}
                onClick={() => handleUseSuggestedRole(aiSuggestedRole)}
              >
                Use This Role
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Upload Zone & JD Context */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        
        {/* Left: Drag & Drop Resume Upload */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <FileText size={18} color="var(--primary)" /> Candidate Resume
            </h3>
            <button
              type="button"
              onClick={() => setUseTextInput(!useTextInput)}
              style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
            >
              {useTextInput ? "Switch to PDF Upload" : "Paste Resume Text"}
            </button>
          </div>

          {!useTextInput ? (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{
                border: dragActive ? '2px dashed var(--primary)' : '2px dashed #cbd5e1',
                borderRadius: '12px',
                padding: '32px 20px',
                textAlign: 'center',
                backgroundColor: dragActive ? '#f5f3ff' : '#f8fafc',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative'
              }}
            >
              <input
                type="file"
                accept=".pdf,.txt,.docx"
                onChange={handleFileChange}
                style={{
                  position: 'absolute',
                  inset: 0,
                  opacity: 0,
                  cursor: 'pointer',
                  width: '100%',
                  height: '100%'
                }}
              />
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <UploadCloud size={24} color="var(--primary)" />
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>
                  {file ? file.name : "Drag & drop candidate resume (PDF)"}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                  Supports standard single-column and multi-column PDF resumes.
                </p>
              </div>
            </div>
          ) : (
            <div>
              <textarea
                value={resumeTextInput}
                onChange={(e) => setResumeTextInput(e.target.value)}
                placeholder="Paste raw resume text, education, skills, and projects here..."
                rows={7}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '10px',
                  border: '1px solid var(--border-color)',
                  fontSize: '13px',
                  fontFamily: 'inherit',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          )}

          {candResume && (
            <div style={{ marginTop: '14px', padding: '10px 14px', backgroundColor: '#f1f5f9', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12.5px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileCheck size={16} color="#059669" />
                <span style={{ fontWeight: 600, color: '#334155' }}>Current: {candResume.fileName}</span>
              </div>
              <span style={{ color: '#64748b' }}>Uploaded: {candResume.uploadedAt}</span>
            </div>
          )}

          <div style={{ marginTop: '18px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <Button
              variant="primary"
              loading={analyzing}
              icon={Sparkles}
              onClick={handleAnalyzeResume}
            >
              {candResume ? "Re-Analyze Resume" : "Extract & Analyze Resume"}
            </Button>
          </div>
        </div>

        {/* Right: Target Role Selection & Job Description Matching */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Briefcase size={18} color="var(--primary)" /> Target Role & JD Matching
            </h3>
            <Badge variant={currentTargetRole ? "primary" : "neutral"}>
              {currentTargetRole ? "Role Configured" : "Unset"}
            </Badge>
          </div>

          {/* Target Role Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
              Select Target Role
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{ flex: 1, padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', backgroundColor: '#fff' }}
              >
                <option value="">-- Choose Target Role --</option>
                {STANDARD_ROLES.map((role) => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
              <Button
                variant="outline"
                size="sm"
                loading={savingRole}
                onClick={handleSaveRole}
              >
                Save Role
              </Button>
            </div>

            {selectedRole === "Other / Custom Role" && (
              <input
                type="text"
                placeholder="Enter custom role title (e.g. ASIC Verification Engineer)"
                value={customRole}
                onChange={(e) => setCustomRole(e.target.value)}
                style={{ width: '100%', marginTop: '8px', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            )}
          </div>

          {/* Job Description Title & Text */}
          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
              Job Title
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. VLSI Design Engineer / Junior Hardware Engineer"
              style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
              Job Description / Required Competencies
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste job description requirements, technical qualifications, or core domain skills here..."
              rows={4}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                fontSize: '12.5px',
                lineHeight: 1.5,
                outline: 'none',
                fontFamily: 'inherit',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <Button
            variant="primary"
            size="sm"
            loading={updatingJD}
            onClick={handleCompareJD}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            Compare Skills & Align JD
          </Button>
        </div>

      </div>

      {/* Extracted Profile Details (Dynamic from User Resume) */}
      {candResume ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Match Score Banner */}
          {candJD && (
            <div
              className="card"
              style={{
                background: 'linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%)',
                border: '1px solid #bbf7d0',
                padding: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '16px'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#166534', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Job Match Alignment
                  </span>
                  <Badge variant="success">{candJD.matchScore >= 70 ? "Strong Alignment" : "Developing Fit"}</Badge>
                </div>
                <div style={{ fontSize: '24px', fontWeight: 800, color: '#14532d' }}>
                  {candJD.matchScore}% Role Compatibility
                </div>
                <p style={{ fontSize: '13px', color: '#166534', margin: 0, marginTop: '2px' }}>
                  {candJD.matchedSkills?.length || 0} skills matched with JD criteria for <strong>{candJD.title}</strong>.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <Button
                  variant="primary"
                  onClick={() => navigate('/interview-setup')}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Start Personalized Mock
                </Button>
              </div>
            </div>
          )}

          {/* Candidate Competencies Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            
            {/* Extracted Technical Skills */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                  <Code size={18} color="var(--primary)" /> Extracted Technical Skills
                </h4>
                <Badge variant="primary">{candResume.skills?.length || 0} Skills</Badge>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {candResume.skills?.map((skill, i) => {
                  const isMatched = candJD?.matchedSkills?.includes(skill.toLowerCase());
                  return (
                    <span
                      key={i}
                      style={{
                        fontSize: '12.5px',
                        padding: '4px 10px',
                        borderRadius: '20px',
                        backgroundColor: isMatched ? '#ecfdf5' : '#f1f5f9',
                        color: isMatched ? '#047857' : '#334155',
                        border: isMatched ? '1px solid #a7f3d0' : '1px solid #e2e8f0',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px'
                      }}
                    >
                      {isMatched && <Check size={12} />}
                      {skill}
                    </span>
                  );
                })}
              </div>

              {candJD?.missingSkills?.length > 0 && (
                <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: '#dc2626', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <AlertTriangle size={14} /> Missing Required Skills from JD:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {candJD.missingSkills.map((ms, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: '11.5px',
                          padding: '3px 8px',
                          borderRadius: '16px',
                          backgroundColor: '#fef2f2',
                          color: '#b91c1c',
                          border: '1px solid #fecaca',
                          fontWeight: 600
                        }}
                      >
                        +{ms}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Extracted Projects */}
            <div className="card">
              <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <Layers size={18} color="var(--primary)" /> Resume Projects (Phase 3 Engine)
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {candResume.projects?.length > 0 ? (
                  candResume.projects.map((proj, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '10px 12px',
                        backgroundColor: '#f8fafc',
                        borderRadius: '8px',
                        border: '1px solid #e2e8f0',
                        fontSize: '12.5px',
                        color: '#1e293b',
                        lineHeight: 1.4,
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px'
                      }}
                    >
                      <span style={{ color: 'var(--primary)', fontWeight: 700 }}>#{i + 1}</span>
                      <span>{proj}</span>
                    </div>
                  ))
                ) : (
                  <div style={{ color: '#64748b', fontSize: '12.5px' }}>
                    No specific project keywords detected. General domain questions will be formulated.
                  </div>
                )}
              </div>

              <div style={{ marginTop: '14px', fontSize: '11.5px', color: '#64748b' }}>
                Project titles are automatically parsed by Phase 3 question engine to formulate tailored STAR prompts.
              </div>
            </div>

          </div>

          {/* Education & Experience Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
            <div className="card">
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <GraduationCap size={18} color="var(--primary)" /> Education & Department
              </h4>
              <p style={{ fontSize: '13px', color: '#334155', margin: 0, fontWeight: 600 }}>
                {candResume.education || user?.college || "Higher Education Degree"}
              </p>
              {candResume.department && (
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                  Specialization: <strong>{candResume.department}</strong>
                </div>
              )}
            </div>

            <div className="card">
              <h4 style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <Briefcase size={18} color="var(--primary)" /> Practical Experience & Certifications
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {candResume.internships?.length > 0 ? (
                  candResume.internships.map((intern, i) => (
                    <div key={i} style={{ fontSize: '12.5px', color: '#334155' }}>
                      • {intern}
                    </div>
                  ))
                ) : candResume.certifications?.length > 0 ? (
                  candResume.certifications.map((cert, i) => (
                    <div key={i} style={{ fontSize: '12.5px', color: '#334155' }}>
                      • {cert}
                    </div>
                  ))
                ) : (
                  <div style={{ fontSize: '12.5px', color: '#64748b' }}>
                    No internship or certification blocks detected.
                  </div>
                )}
              </div>
            </div>
          </div>

        </div>
      ) : (
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '14px',
            border: '1px dashed #cbd5e1',
            padding: '48px 24px',
            textAlign: 'center'
          }}
        >
          <FileText size={40} color="#94a3b8" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#334155' }}>
            No Resume Uploaded Yet
          </h3>
          <p style={{ fontSize: '13px', color: '#64748b', maxWidth: '420px', margin: '4px auto 16px auto' }}>
            Upload your resume PDF above or paste resume text to extract skills and compare against target job descriptions.
          </p>
        </div>
      )}

    </div>
  );
}
