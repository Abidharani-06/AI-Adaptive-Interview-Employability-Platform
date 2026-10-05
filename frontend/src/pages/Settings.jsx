import React, { useState } from 'react';
import { 
  Camera, 
  Mic, 
  Bell, 
  ShieldCheck, 
  Sliders, 
  User, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  Trash2,
  Lock,
  Eye,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';
import storageService from '../services/storageService';

export default function Settings() {
  const { user, updateProfile, changePassword } = useAuth();

  // Settings State initialized dynamically from current user
  const [profileForm, setProfileForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    targetRole: user?.targetRole || '',
    college: user?.college || '',
    phone: user?.phone || '',
    location: user?.location || ''
  });

  const [interviewPrefs, setInterviewPrefs] = useState({
    defaultQuestions: 5,
    adaptiveDifficulty: true,
    enableTimer: true,
    detailedFeedback: true,
    speechAnalysis: true,
    visualAnalysis: true
  });

  const [devicePermissions, setDevicePermissions] = useState({
    camera: 'granted',
    mic: 'granted',
    speaker: 'granted'
  });

  const [notifications, setNotifications] = useState({
    interviewReminders: true,
    weeklyProgress: true,
    roadmapMilestones: true,
    skillAlerts: false
  });

  const [savedSuccess, setSavedSuccess] = useState(false);
  const [checkingDevices, setCheckingDevices] = useState(false);

  const handleSave = (e) => {
    if (e) e.preventDefault();
    updateProfile({
      name: profileForm.name,
      email: profileForm.email,
      targetRole: profileForm.targetRole,
      college: profileForm.college,
      phone: profileForm.phone,
      location: profileForm.location
    });
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleDeviceTest = async () => {
    setCheckingDevices(true);
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        setDevicePermissions({
          camera: 'granted',
          mic: 'granted',
          speaker: 'granted'
        });
        stream.getTracks().forEach(t => t.stop());
      }
    } catch (err) {
      setDevicePermissions(prev => ({
        ...prev,
        camera: 'prompt',
        mic: 'prompt'
      }));
    } finally {
      setCheckingDevices(false);
    }
  };

  const handleClearHistory = () => {
    if (window.confirm("Are you sure you want to reset your local candidate session cache? This will reset all demo and registered session records.")) {
      storageService.resetDemoData();
      window.location.reload();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
            Platform Settings & Preferences
          </h2>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Manage candidate account details, adaptive interview options, hardware permissions, and ethical privacy controls.
          </p>
        </div>
        <Button 
          variant="primary" 
          icon={Save}
          onClick={handleSave}
        >
          Save All Changes
        </Button>
      </div>

      {savedSuccess && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', color: '#166534', fontSize: '13px' }}>
          <CheckCircle2 size={16} color="#16a34a" />
          <span>Settings and candidate profile updated successfully!</span>
        </div>
      )}

      {/* Tabs / Sections Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px' }}>
        
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* Account Profile Card */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', paddingBottom: '12px', borderBottom: '1px solid var(--border-light)' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <User size={18} color="var(--primary)" />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                  Candidate Account Details
                </h3>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Used for report generation & placement evaluation</span>
              </div>
            </div>

            <form onSubmit={handleSave} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>Full Name</label>
                <input 
                  type="text" 
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({...profileForm, name: e.target.value})}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }} 
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>Email Address</label>
                <input 
                  type="email" 
                  value={profileForm.email}
                  onChange={(e) => setProfileForm({...profileForm, email: e.target.value})}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }} 
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>Target Role</label>
                <select 
                  value={profileForm.targetRole}
                  onChange={(e) => setProfileForm({...profileForm, targetRole: e.target.value})}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box', backgroundColor: '#fff' }} 
                >
                  <option value="">-- Choose Target Role --</option>
                  <option value="VLSI Design Engineer">VLSI Design Engineer</option>
                  <option value="Embedded Systems Engineer">Embedded Systems Engineer</option>
                  <option value="AI/ML Engineer">AI/ML Engineer</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="Data Analyst">Data Analyst</option>
                  <option value="Cloud Engineer">Cloud Engineer</option>
                  <option value="DevOps Engineer">DevOps Engineer</option>
                  <option value="Frontend Developer">Frontend Developer</option>
                  <option value="Backend Developer">Backend Developer</option>
                  <option value="Software Engineer">Software Engineer</option>
                  <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
                  <option value="Other / Custom Role">Other / Custom Role</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>College / Institution</label>
                <input 
                  type="text" 
                  value={profileForm.college}
                  onChange={(e) => setProfileForm({...profileForm, college: e.target.value})}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }} 
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>Phone Number</label>
                <input 
                  type="text" 
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm({...profileForm, phone: e.target.value})}
                  placeholder="+91 ..."
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }} 
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>Location</label>
                <input 
                  type="text" 
                  value={profileForm.location}
                  onChange={(e) => setProfileForm({...profileForm, location: e.target.value})}
                  placeholder="City, Country"
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '13px', boxSizing: 'border-box' }} 
                />
              </div>
            </form>
          </div>

          {/* Interview Configuration Card */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', paddingBottom: '12px', borderBottom: '1px solid var(--border-light)' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#f3e8ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Sliders size={18} color="#9333ea" />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                  Interview Session Defaults
                </h3>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Configure runtime parameters for mock viva sessions</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid var(--border-light)' }}>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>Adaptive Dynamic Difficulty</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Adjust next question difficulty dynamically based on real-time NLP accuracy</div>
                </div>
                <input 
                  type="checkbox" 
                  checked={interviewPrefs.adaptiveDifficulty}
                  onChange={(e) => setInterviewPrefs({...interviewPrefs, adaptiveDifficulty: e.target.checked})}
                  style={{ accentColor: 'var(--primary)', cursor: 'pointer' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid var(--border-light)' }}>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>Per-Question Countdown Timer</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Display visual clock during interview prompt answering</div>
                </div>
                <input 
                  type="checkbox" 
                  checked={interviewPrefs.enableTimer}
                  onChange={(e) => setInterviewPrefs({...interviewPrefs, enableTimer: e.target.checked})}
                  style={{ accentColor: 'var(--primary)', cursor: 'pointer' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>Default Questions Per Round</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Recommended mock session length</div>
                </div>
                <select 
                  value={interviewPrefs.defaultQuestions}
                  onChange={(e) => setInterviewPrefs({...interviewPrefs, defaultQuestions: parseInt(e.target.value)})}
                  style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '12.5px', backgroundColor: '#fff' }}
                >
                  <option value={3}>3 Questions (Quick Drill)</option>
                  <option value={5}>5 Questions (Standard Mock)</option>
                  <option value={8}>8 Questions (In-depth Viva)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Privacy & Ethical AI Disclosure Card */}
          <div className="card" style={{ background: 'linear-gradient(135deg, #f5f3ff 0%, #ffffff 50%, #eff6ff 100%)', border: '1px solid #c7d2fe' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--primary)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                  Privacy & Ethical AI Transparency Standards
                </h3>
                <Badge variant="info">Certified Ethical Assessment</Badge>
              </div>
            </div>

            <p style={{ fontSize: '12.5px', color: '#475569', lineHeight: 1.5, marginBottom: '14px' }}>
              Our platform adheres to strict AI fairness, privacy, and scientific standards. All computer vision and acoustic features measure <strong>observable physical cues</strong> to assist candidate placement readiness:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '12px', marginBottom: '14px' }}>
              <div style={{ padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, color: '#166534', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={14} color="#16a34a" /> Observable Cues:
                </div>
                <ul style={{ margin: 0, paddingLeft: '16px', color: '#475569', lineHeight: 1.5 }}>
                  <li>Camera-facing gaze consistency</li>
                  <li>Head orientation & posture stability</li>
                  <li>Speaking rate (WPM) & pauses</li>
                  <li>Filler word frequency</li>
                  <li>Semantic relevance & accuracy</li>
                </ul>
              </div>

              <div style={{ padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #fee2e2' }}>
                <div style={{ fontWeight: 700, color: '#b91c1c', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={14} color="#ef4444" /> Never Diagnosed:
                </div>
                <ul style={{ margin: 0, paddingLeft: '16px', color: '#475569', lineHeight: 1.5 }}>
                  <li>No emotion or mood detection</li>
                  <li>No personality diagnosis</li>
                  <li>No nervousness detection</li>
                  <li>No honesty or lie scoring</li>
                  <li>No guaranteed hiring claims</li>
                </ul>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', borderTop: '1px solid #e2e8f0', paddingTop: '10px' }}>
              <span style={{ color: '#64748b' }}>Media streams are processed in memory and never stored.</span>
              <button 
                type="button" 
                onClick={handleClearHistory} 
                style={{ background: 'none', border: 'none', color: '#dc2626', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
              >
                <Trash2 size={13} />
                Clear Local Storage Cache
              </button>
            </div>
          </div>

        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* Hardware & Permissions Card */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', paddingBottom: '10px', borderBottom: '1px solid var(--border-light)' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Hardware & Permissions
              </h3>
              <button 
                type="button"
                onClick={handleDeviceTest}
                disabled={checkingDevices}
                style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
              >
                <RefreshCw size={12} className={checkingDevices ? "animate-spin" : ""} />
                Test Devices
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Camera size={18} color="var(--text-secondary)" />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>Webcam Stream</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Observable presentation signals</div>
                  </div>
                </div>
                <Badge variant={devicePermissions.camera === 'granted' ? 'success' : 'warning'}>
                  {devicePermissions.camera === 'granted' ? 'Active' : 'Prompt'}
                </Badge>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Mic size={18} color="var(--text-secondary)" />
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>Microphone Input</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Acoustic pacing & WPM rate</div>
                  </div>
                </div>
                <Badge variant={devicePermissions.mic === 'granted' ? 'success' : 'warning'}>
                  {devicePermissions.mic === 'granted' ? 'Active' : 'Prompt'}
                </Badge>
              </div>
            </div>
          </div>

          {/* Notifications Card */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', paddingBottom: '10px', borderBottom: '1px solid var(--border-light)' }}>
              <Bell size={18} color="var(--text-secondary)" />
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Notification Preferences
              </h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
                <span style={{ color: 'var(--text-main)' }}>Interview practice reminders</span>
                <input 
                  type="checkbox" 
                  checked={notifications.interviewReminders}
                  onChange={(e) => setNotifications({...notifications, interviewReminders: e.target.checked})}
                  style={{ accentColor: 'var(--primary)' }}
                />
              </label>

              <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
                <span style={{ color: 'var(--text-main)' }}>Weekly progress summaries</span>
                <input 
                  type="checkbox" 
                  checked={notifications.weeklyProgress}
                  onChange={(e) => setNotifications({...notifications, weeklyProgress: e.target.checked})}
                  style={{ accentColor: 'var(--primary)' }}
                />
              </label>

              <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
                <span style={{ color: 'var(--text-main)' }}>Roadmap milestone alerts</span>
                <input 
                  type="checkbox" 
                  checked={notifications.roadmapMilestones}
                  onChange={(e) => setNotifications({...notifications, roadmapMilestones: e.target.checked})}
                  style={{ accentColor: 'var(--primary)' }}
                />
              </label>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
