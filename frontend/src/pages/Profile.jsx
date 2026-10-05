import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  GraduationCap,
  Briefcase,
  Edit3,
  Award,
  BookOpen,
  Code,
  FolderGit2,
  Calendar,
  CheckCircle2,
  Sparkles,
  Phone,
  MapPin,
  FileText,
  Lock,
  LogOut,
  AlertCircle,
  Building,
  Target
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

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

export default function Profile() {
  const { user, updateProfile, changePassword, logout, assessment, profileCompletion } = useAuth();
  const navigate = useNavigate();

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState({ type: '', text: '' });

  const [editData, setEditData] = useState({
    name: user?.name || "",
    college: user?.college || "",
    degree: user?.degree || "",
    department: user?.department || "",
    graduationYear: user?.graduationYear || "",
    targetRole: user?.targetRole || "",
    phone: user?.phone || "",
    location: user?.location || ""
  });

  useEffect(() => {
    if (user) {
      setEditData({
        name: user.name || "",
        college: user.college || "",
        degree: user.degree || "",
        department: user.department || "",
        graduationYear: user.graduationYear || "",
        targetRole: user.targetRole || "",
        phone: user.phone || "",
        location: user.location || ""
      });
    }
  }, [user]);

  const [passwords, setPasswords] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordMsg, setPasswordMsg] = useState({ type: '', text: '' });

  const candResume = user?.resume;
  const candSkills = candResume?.skills || (assessment?.candidate?.skills) || [];
  const candProjects = candResume?.projects || (assessment?.candidate?.projects) || [];
  const candInternships = candResume?.internships || (assessment?.candidate?.internships) || [];
  const candCerts = candResume?.certifications || (assessment?.candidate?.certifications) || [];
  const interviewHistory = user?.interviewHistory || assessment?.progress_tracking?.timeline || [];

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await updateProfile(editData);
      if (res.success) {
        setIsEditOpen(false);
        setToast({ type: 'success', text: 'Profile updated successfully!' });
        setTimeout(() => setToast({ type: '', text: '' }), 3500);
      } else {
        setToast({ type: 'error', text: res.error || 'Failed to update profile.' });
      }
    } catch (err) {
      setToast({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordMsg({ type: '', text: '' });

    if (passwords.newPassword !== passwords.confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }
    if (passwords.newPassword.length < 6) {
      setPasswordMsg({ type: 'error', text: 'Password must be at least 6 characters.' });
      return;
    }

    try {
      const res = await changePassword(passwords.oldPassword, passwords.newPassword);
      if (res.success) {
        setPasswordMsg({ type: 'success', text: 'Password successfully updated.' });
        setTimeout(() => {
          setIsPasswordOpen(false);
          setPasswords({ oldPassword: '', newPassword: '', confirmPassword: '' });
          setPasswordMsg({ type: '', text: '' });
        }, 1500);
      } else {
        setPasswordMsg({ type: 'error', text: res.error || res.detail || 'Failed to update password.' });
      }
    } catch (err) {
      setPasswordMsg({ type: 'error', text: err.message });
    }
  };

  const missingProfileItems = [];
  if (!candResume) missingProfileItems.push("Candidate Resume");
  if (!user?.phone || !user?.location) missingProfileItems.push("Contact / Location");
  if (!user?.targetRole) missingProfileItems.push("Target Role");
  if (interviewHistory.length === 0) missingProfileItems.push("Completed Mock Interview");

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Toast Alert */}
      {toast.text && (
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
          <span>{toast.text}</span>
        </div>
      )}

      {/* Header Profile Hero Card */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f5f3ff 60%, #eef2ff 100%)',
          border: '1px solid #e0e7ff',
          padding: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '24px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <img
            src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250"}
            alt={user?.name || "Candidate"}
            style={{
              width: '90px',
              height: '90px',
              borderRadius: '50%',
              objectFit: 'cover',
              border: '3px solid #ffffff',
              boxShadow: '0 4px 14px rgba(79, 70, 229, 0.25)'
            }}
          />

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
                {user?.name || "Candidate"}
              </h2>
              <Badge variant={user?.isDemo ? 'neutral' : 'primary'}>
                {user?.isDemo ? 'Demo Persona' : 'Authenticated User'}
              </Badge>
            </div>

            <div style={{ fontSize: '15px', fontWeight: 700, color: user?.targetRole ? 'var(--primary)' : '#d97706', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Target size={16} />
              Target Role: {user?.targetRole || "Not selected"}
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px' }}>
              {user?.college && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Building size={15} color="var(--text-muted)" />
                  {user.college}
                </span>
              )}
              {user?.department && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <GraduationCap size={15} color="var(--text-muted)" />
                  {user.degree ? `${user.degree} - ` : ''}{user.department} {user.graduationYear ? `(${user.graduationYear})` : ''}
                </span>
              )}
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Mail size={15} color="var(--text-muted)" />
                {user?.email}
              </span>
              {user?.phone && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Phone size={15} color="var(--text-muted)" />
                  {user.phone}
                </span>
              )}
              {user?.location && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <MapPin size={15} color="var(--text-muted)" />
                  {user.location}
                </span>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <Button
            variant="outline"
            icon={Edit3}
            onClick={() => setIsEditOpen(true)}
          >
            Edit Profile
          </Button>
          <Button
            variant="outline"
            icon={Lock}
            onClick={() => setIsPasswordOpen(true)}
          >
            Security
          </Button>
          <Button
            variant="danger"
            icon={LogOut}
            onClick={() => {
              logout();
              navigate('/login');
            }}
          >
            Logout
          </Button>
        </div>
      </div>

      {/* Profile Completion & Interview Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        
        {/* Profile Completion Card */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Profile Completion
            </span>
            <span style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary)' }}>
              {profileCompletion}%
            </span>
          </div>

          <div style={{ height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ width: `${profileCompletion}%`, height: '100%', backgroundColor: '#6366f1', transition: 'width 0.4s ease' }} />
          </div>

          {missingProfileItems.length > 0 ? (
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              <strong>Pending: </strong> {missingProfileItems.join(" • ")}
            </div>
          ) : (
            <div style={{ fontSize: '12px', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={14} /> Profile 100% complete & placement ready!
            </div>
          )}
        </div>

        {/* Interview Statistics */}
        <div className="card" style={{ padding: '24px' }}>
          <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
            Interview Activity
          </span>
          <div style={{ display: 'flex', gap: '24px', marginTop: '10px' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)' }}>
                {interviewHistory.length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mocks Taken</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary)' }}>
                {assessment?.readiness?.score ? `${assessment.readiness.score}%` : "Pending"}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Current Score</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: '#059669' }}>
                {assessment?.readiness?.level || "Not evaluated"}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Readiness Tier</div>
            </div>
          </div>
        </div>

        {/* Resume Status Card */}
        <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Resume Status
            </span>
            <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', marginTop: '6px' }}>
              {candResume ? candResume.fileName : "No Resume Uploaded"}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              {candResume ? `${candSkills.length} skills extracted` : "Upload to personalize your questions"}
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            style={{ marginTop: '10px', alignSelf: 'flex-start' }}
            onClick={() => navigate('/resume')}
          >
            {candResume ? "Re-upload Resume" : "Upload Resume Now"}
          </Button>
        </div>

      </div>

      {/* Main Grid: Skills & Projects */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        
        {/* Extracted Skills */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Code size={18} color="var(--primary)" /> Candidate Skills
            </h3>
            <Badge variant="primary">{candSkills.length} Skills</Badge>
          </div>

          {candSkills.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {candSkills.map((skill, i) => (
                <span
                  key={i}
                  style={{
                    fontSize: '12.5px',
                    padding: '4px 10px',
                    borderRadius: '20px',
                    backgroundColor: '#f1f5f9',
                    color: '#334155',
                    border: '1px solid #e2e8f0',
                    fontWeight: 600
                  }}
                >
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
              No skills added yet. Upload your resume to extract your technical skillset.
            </div>
          )}
        </div>

        {/* Extracted Projects */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <FolderGit2 size={18} color="var(--primary)" /> Declared Projects
            </h3>
            <Badge variant="info">{candProjects.length} Projects</Badge>
          </div>

          {candProjects.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {candProjects.map((proj, i) => (
                <div
                  key={i}
                  style={{
                    padding: '10px 14px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    fontSize: '12.5px',
                    color: '#1e293b'
                  }}
                >
                  <strong style={{ color: 'var(--primary)' }}>#{i + 1}</strong> {proj}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
              No projects recorded yet.
            </div>
          )}
        </div>

      </div>

      {/* Edit Profile Modal */}
      <Modal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        title="Edit Candidate Profile"
      >
        <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Full Name</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              required
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px', boxSizing: 'border-box' }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>College / University</label>
              <input
                type="text"
                value={editData.college}
                onChange={(e) => setEditData({ ...editData, college: e.target.value })}
                placeholder="e.g. National Institute of Tech"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Department / Branch</label>
              <input
                type="text"
                value={editData.department}
                onChange={(e) => setEditData({ ...editData, department: e.target.value })}
                placeholder="e.g. ECE / VLSI / CSE"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Degree</label>
              <input
                type="text"
                value={editData.degree}
                onChange={(e) => setEditData({ ...editData, degree: e.target.value })}
                placeholder="e.g. B.Tech / B.E."
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Graduation Year</label>
              <input
                type="text"
                value={editData.graduationYear}
                onChange={(e) => setEditData({ ...editData, graduationYear: e.target.value })}
                placeholder="e.g. 2026"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Target Role</label>
            <select
              value={editData.targetRole}
              onChange={(e) => setEditData({ ...editData, targetRole: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px', boxSizing: 'border-box', backgroundColor: '#fff' }}
            >
              <option value="">-- Choose Target Role --</option>
              {STANDARD_ROLES.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Phone Number</label>
              <input
                type="text"
                value={editData.phone}
                onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                placeholder="+91 98765 43210"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Location</label>
              <input
                type="text"
                value={editData.location}
                onChange={(e) => setEditData({ ...editData, location: e.target.value })}
                placeholder="City, State"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
            <Button variant="outline" type="button" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" loading={saving}>
              Save Profile
            </Button>
          </div>
        </form>
      </Modal>

      {/* Change Password Modal */}
      <Modal
        isOpen={isPasswordOpen}
        onClose={() => setIsPasswordOpen(false)}
        title="Update Account Password"
      >
        <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {passwordMsg.text && (
            <div style={{ padding: '8px 12px', borderRadius: '6px', fontSize: '13px', backgroundColor: passwordMsg.type === 'error' ? '#fef2f2' : '#f0fdf4', color: passwordMsg.type === 'error' ? '#b91c1c' : '#15803d' }}>
              {passwordMsg.text}
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Current Password</label>
            <input
              type="password"
              value={passwords.oldPassword}
              onChange={(e) => setPasswords({ ...passwords, oldPassword: e.target.value })}
              required
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>New Password</label>
            <input
              type="password"
              value={passwords.newPassword}
              onChange={(e) => setPasswords({ ...passwords, newPassword: e.target.value })}
              required
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Confirm New Password</label>
            <input
              type="password"
              value={passwords.confirmPassword}
              onChange={(e) => setPasswords({ ...passwords, confirmPassword: e.target.value })}
              required
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '14px', boxSizing: 'border-box' }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <Button variant="outline" type="button" onClick={() => setIsPasswordOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Update Password
            </Button>
          </div>
        </form>
      </Modal>

    </div>
  );
}
