import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles,
  User,
  Mail,
  Lock,
  Building2,
  GraduationCap,
  BookOpen,
  Calendar,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  Phone,
  MapPin,
  Clock,
  ShieldCheck,
  Send,
  KeyRound,
  ArrowRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/authService';
import CollegeCombobox from '../components/CollegeCombobox';
import Button from '../components/Button';

export default function Register() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    gender: 'Prefer not to say',
    dob: '',
    college: '',
    customCollege: '',
    degree: 'B.E.',
    department: 'Computer Science & Engineering',
    yearOfStudy: '3rd Year',
    graduationYear: '2026',
    city: '',
    targetRole: 'AI/ML Software Engineer',
    password: '',
    confirmPassword: '',
    otp: ''
  });

  const [isOtherCollege, setIsOtherCollege] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // OTP State Management
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [devOtpHint, setDevOtpHint] = useState('');
  const [otpMessage, setOtpMessage] = useState('');

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  // Cooldown countdown timer
  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setInterval(() => {
        setResendCooldown(prev => prev - 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const calculatePasswordStrength = (pass) => {
    let score = 0;
    if (pass.length >= 8) score++;
    if (/[A-Z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;
    return score;
  };

  const strength = calculatePasswordStrength(formData.password);

  // Send Email OTP
  const handleSendOtp = async () => {
    setErrorMessage('');
    setOtpMessage('');
    if (!formData.email.trim() || !formData.email.includes('@')) {
      setErrorMessage("Please enter a valid email address before requesting an OTP.");
      return;
    }

    setSendingOtp(true);
    try {
      const res = await authService.sendOtp(formData.email);
      if (res.success) {
        setOtpSent(true);
        setResendCooldown(60);
        setOtpMessage("Verification code sent to your email. (Valid for 5 minutes)");
        if (res.devOtp) {
          setDevOtpHint(res.devOtp);
        }
      } else {
        setErrorMessage(res.detail || "Failed to send verification code.");
      }
    } catch (err) {
      setErrorMessage(err.message || "Failed to send verification code.");
    } finally {
      setSendingOtp(false);
    }
  };

  // Verify Email OTP
  const handleVerifyOtp = async () => {
    setErrorMessage('');
    if (!formData.otp.trim() || formData.otp.trim().length !== 6) {
      setErrorMessage("Please enter the 6-digit verification code sent to your email.");
      return;
    }

    setVerifyingOtp(true);
    try {
      const res = await authService.verifyOtp(formData.email, formData.otp.trim());
      if (res.success && res.verified) {
        setOtpVerified(true);
        setOtpMessage("Email verified successfully! You may now complete registration.");
      } else {
        setErrorMessage(res.detail || "Invalid verification code.");
      }
    } catch (err) {
      setErrorMessage(err.message || "Invalid or expired verification code.");
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Final Registration Submission
  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!formData.name.trim()) {
      setErrorMessage("Please enter your full name.");
      return;
    }

    if (!formData.email.trim()) {
      setErrorMessage("Please enter a valid email address.");
      return;
    }

    if (!otpVerified) {
      setErrorMessage("Please verify your email with the 6-digit code before registering.");
      return;
    }

    const effectiveCollege = isOtherCollege
      ? formData.customCollege.trim()
      : formData.college.trim();

    if (!effectiveCollege) {
      setErrorMessage("Please select or specify your college / university.");
      return;
    }

    if (formData.password.length < 6) {
      setErrorMessage("Password must be at least 6 characters long.");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setErrorMessage("Password confirmation does not match password.");
      return;
    }

    setLoading(true);
    try {
      const res = await register({
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim() || null,
        gender: formData.gender,
        dob: formData.dob || null,
        college: effectiveCollege,
        degree: formData.degree,
        department: formData.department,
        yearOfStudy: formData.yearOfStudy,
        graduationYear: formData.graduationYear,
        city: formData.city.trim() || null,
        targetRole: formData.targetRole.trim() || null,
        otp: formData.otp.trim(),
        password: formData.password,
        confirmPassword: formData.confirmPassword
      }, true);

      if (res.success) {
        navigate('/dashboard');
      } else {
        setErrorMessage(res.error || "Failed to create candidate account.");
      }
    } catch (err) {
      setErrorMessage(err.message || "An unexpected error occurred during registration.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', backgroundColor: '#090d16', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* Left Branding Pane */}
      <div
        style={{
          flex: '1',
          background: 'linear-gradient(145deg, #090d16 0%, #0f172a 40%, #1e1b4b 100%)',
          color: '#ffffff',
          padding: '60px 48px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          borderRight: '1px solid rgba(255, 255, 255, 0.08)'
        }}
        className="hidden-mobile"
      >
        <div>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 8px 24px rgba(99, 102, 241, 0.45)'
              }}
            >
              <Sparkles size={24} color="#ffffff" />
            </div>
            <div>
              <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                AI Employability Platform
              </div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Next-Gen Placement Suite
              </div>
            </div>
          </div>

          <h2 style={{ fontSize: '30px', fontWeight: 800, lineHeight: 1.3, letterSpacing: '-0.02em', marginBottom: '18px', color: '#f8fafc' }}>
            Elevate Your Placement Readiness with Multimodal AI.
          </h2>
          <p style={{ fontSize: '14.5px', color: '#94a3b8', lineHeight: 1.6, maxWidth: '460px', marginBottom: '36px' }}>
            Experience an enterprise-grade assessment platform featuring Round 1 Adaptive Aptitude, Round 2 AI HR Behavioral with live speech-to-text, computer vision observable signals, and personalized learning roadmaps.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '8px', backgroundColor: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <CheckCircle2 size={16} color="#818cf8" />
              </div>
              <div>
                <strong style={{ fontSize: '14px', color: '#f1f5f9' }}>Round 1: 3-Tier Adaptive Aptitude</strong>
                <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: '2px 0 0 0' }}>Quantitative Ability, Logical Reasoning, and Verbal Ability with deep diagnostic topic analytics.</p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <CheckCircle2 size={16} color="#38bdf8" />
              </div>
              <div>
                <strong style={{ fontSize: '14px', color: '#f1f5f9' }}>Round 2: AI HR & Speech-to-Text</strong>
                <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: '2px 0 0 0' }}>Live conversational responses transcribed in real time and evaluated via NLP STAR metrics.</p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <CheckCircle2 size={16} color="#34d399" />
              </div>
              <div>
                <strong style={{ fontSize: '14px', color: '#f1f5f9' }}>Strict Candidate Data Isolation</strong>
                <p style={{ fontSize: '12.5px', color: '#94a3b8', margin: '2px 0 0 0' }}>Each candidate owns isolated sessions, custom resumes, tailored skill gaps, and roadmap milestones.</p>
              </div>
            </div>
          </div>
        </div>

        <div style={{ fontSize: '12px', color: '#64748b', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px' }}>
          Secure Candidate Identity Verification • AES-256 Hashing • 2026 Hackathon Edition
        </div>
      </div>

      {/* Right Form Pane */}
      <div
        style={{
          flex: '1.3',
          padding: '48px 40px',
          overflowY: 'auto',
          maxHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-start'
        }}
      >
        <div style={{ width: '100%', maxWidth: '620px' }}>
          
          <div style={{ marginBottom: '28px' }}>
            <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.03em', margin: 0 }}>
              Create Candidate Account
            </h1>
            <p style={{ fontSize: '13.5px', color: '#94a3b8', marginTop: '6px' }}>
              Already registered?{' '}
              <Link to="/login" style={{ color: '#818cf8', fontWeight: 600 }}>
                Log in to dashboard
              </Link>
            </p>
          </div>

          {errorMessage && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 16px', backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '13.5px', marginBottom: '20px' }}>
              <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
              <span>{errorMessage}</span>
            </div>
          )}

          {otpMessage && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 16px', backgroundColor: otpVerified ? 'rgba(16, 185, 129, 0.12)' : 'rgba(99, 102, 241, 0.12)', border: `1px solid ${otpVerified ? 'rgba(16, 185, 129, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`, borderRadius: '10px', color: otpVerified ? '#6ee7b7' : '#a5b4fc', fontSize: '13.5px', marginBottom: '20px' }}>
              <CheckCircle2 size={18} color={otpVerified ? "#10b981" : "#818cf8"} style={{ flexShrink: 0 }} />
              <span>{otpMessage}</span>
            </div>
          )}

          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Section A: Personal & Contact */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                1. Personal Details
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                  Full Name <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <div style={{ position: 'relative' }}>
                  <User size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                  <input
                    type="text"
                    required
                    placeholder="e.g. Abidharani A"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Phone Number
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Phone size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                      type="tel"
                      placeholder="e.g. +91 9876543210"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Gender
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={formData.dob}
                    onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13px', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    City / District
                  </label>
                  <div style={{ position: 'relative' }}>
                    <MapPin size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                      type="text"
                      placeholder="e.g. Chennai / Coimbatore"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Section B: Email & OTP Verification */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  2. Email & 6-Digit OTP Verification
                </div>
                {otpVerified ? (
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#34d399', backgroundColor: 'rgba(16, 185, 129, 0.15)', padding: '3px 8px', borderRadius: '6px' }}>
                    ✓ Verified
                  </span>
                ) : (
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#fbbf24', backgroundColor: 'rgba(245, 158, 11, 0.15)', padding: '3px 8px', borderRadius: '6px' }}>
                    Verification Required
                  </span>
                )}
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                  Email Address <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <div style={{ position: 'relative', flex: 1 }}>
                    <Mail size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                      type="email"
                      required
                      disabled={otpVerified}
                      placeholder="e.g. candidate@university.edu"
                      value={formData.email}
                      onChange={(e) => {
                        setFormData({ ...formData, email: e.target.value });
                        setOtpVerified(false);
                      }}
                      style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                    />
                  </div>
                  <button
                    type="button"
                    disabled={sendingOtp || resendCooldown > 0 || otpVerified}
                    onClick={handleSendOtp}
                    style={{
                      padding: '10px 18px',
                      backgroundColor: otpVerified ? '#1f2937' : resendCooldown > 0 ? '#1f2937' : '#6366f1',
                      color: '#ffffff',
                      borderRadius: '10px',
                      fontWeight: 600,
                      fontSize: '13px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      cursor: otpVerified || resendCooldown > 0 ? 'not-allowed' : 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {sendingOtp ? (
                      "Sending..."
                    ) : otpVerified ? (
                      "Verified"
                    ) : resendCooldown > 0 ? (
                      `Resend (${resendCooldown}s)`
                    ) : otpSent ? (
                      "Resend OTP"
                    ) : (
                      "Send OTP"
                    )}
                  </button>
                </div>
              </div>

              {/* OTP Input Field */}
              {otpSent && !otpVerified && (
                <div style={{ padding: '14px', backgroundColor: '#0f172a', borderRadius: '10px', border: '1px dashed #6366f1' }}>
                  <label style={{ display: 'block', fontSize: '12.5px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Enter 6-Digit OTP Code
                  </label>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                      <KeyRound size={16} color="#818cf8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                      <input
                        type="text"
                        maxLength={6}
                        placeholder="e.g. 542918"
                        value={formData.otp}
                        onChange={(e) => setFormData({ ...formData, otp: e.target.value.replace(/[^0-9]/g, '') })}
                        style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#111827', border: '1px solid #4b5563', borderRadius: '8px', color: '#f8fafc', fontSize: '15px', fontWeight: 700, letterSpacing: '4px', outline: 'none' }}
                      />
                    </div>
                    <button
                      type="button"
                      disabled={verifyingOtp || formData.otp.length !== 6}
                      onClick={handleVerifyOtp}
                      style={{
                        padding: '10px 18px',
                        backgroundColor: '#10b981',
                        color: '#ffffff',
                        borderRadius: '8px',
                        fontWeight: 600,
                        fontSize: '13px',
                        cursor: verifyingOtp || formData.otp.length !== 6 ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {verifyingOtp ? "Verifying..." : "Verify OTP"}
                    </button>
                  </div>

                  {devOtpHint && (
                    <div style={{ marginTop: '8px', fontSize: '12px', color: '#a5b4fc', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>Local Test OTP: <strong>{devOtpHint}</strong></span>
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, otp: devOtpHint })}
                        style={{ color: '#38bdf8', textDecoration: 'underline', fontSize: '11.5px', cursor: 'pointer' }}
                      >
                        Auto-fill
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Section C: Academic Background */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                3. Academic Profile
              </div>

              {/* College Dropdown (Tamil Nadu Registry) */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                  College / University (Tamil Nadu) <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <CollegeCombobox
                  value={formData.college}
                  onChange={(val) => setFormData({ ...formData, college: val })}
                  onOtherSelected={(isOther) => setIsOtherCollege(isOther)}
                />
              </div>

              {/* If "Other" selected, manual input appears */}
              {isOtherCollege && (
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Specify College Name (Manual Entry) <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Enter official college name..."
                    value={formData.customCollege}
                    onChange={(e) => setFormData({ ...formData, customCollege: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #6366f1', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  />
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Degree Program
                  </label>
                  <select
                    value={formData.degree}
                    onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  >
                    <option value="B.E.">Bachelor of Engineering (B.E.)</option>
                    <option value="B.Tech">Bachelor of Technology (B.Tech)</option>
                    <option value="M.E.">Master of Engineering (M.E.)</option>
                    <option value="M.Tech">Master of Technology (M.Tech)</option>
                    <option value="MCA">Master of Computer Applications (MCA)</option>
                    <option value="M.Sc">Master of Science (M.Sc)</option>
                    <option value="B.Sc">Bachelor of Science (B.Sc)</option>
                    <option value="BCA">Bachelor of Computer Applications (BCA)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Department / Branch
                  </label>
                  <select
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  >
                    <option value="Computer Science & Engineering">Computer Science & Engineering (CSE)</option>
                    <option value="Artificial Intelligence & Data Science">AI & Data Science (AI & DS)</option>
                    <option value="Artificial Intelligence & Machine Learning">AI & Machine Learning (AI & ML)</option>
                    <option value="Information Technology">Information Technology (IT)</option>
                    <option value="Electronics & Communication Engineering">Electronics & Communication (ECE)</option>
                    <option value="Electrical & Electronics Engineering">Electrical & Electronics (EEE)</option>
                    <option value="Mechanical Engineering">Mechanical Engineering</option>
                    <option value="VLSI & Embedded Systems">VLSI & Embedded Systems</option>
                    <option value="Other Engineering">Other Engineering</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Year of Study
                  </label>
                  <select
                    value={formData.yearOfStudy}
                    onChange={(e) => setFormData({ ...formData, yearOfStudy: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  >
                    <option value="1st Year">1st Year</option>
                    <option value="2nd Year">2nd Year</option>
                    <option value="3rd Year">3rd Year</option>
                    <option value="4th Year / Final Year">4th Year / Final Year</option>
                    <option value="Graduate / Alumnus">Graduate / Alumnus</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Graduation Year
                  </label>
                  <select
                    value={formData.graduationYear}
                    onChange={(e) => setFormData({ ...formData, graduationYear: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  >
                    <option value="2024">2024</option>
                    <option value="2025">2025</option>
                    <option value="2026">2026</option>
                    <option value="2027">2027</option>
                    <option value="2028">2028</option>
                    <option value="2029">2029</option>
                  </select>
                </div>
              </div>

              {/* Target Role (Optional during registration) */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                  Target Role (Optional at Registration)
                </label>
                <div style={{ position: 'relative' }}>
                  <Briefcase size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                  <input
                    type="text"
                    placeholder="e.g. AI/ML Software Engineer, Full Stack Developer, VLSI Design Engineer"
                    value={formData.targetRole}
                    onChange={(e) => setFormData({ ...formData, targetRole: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                  />
                </div>
              </div>
            </div>

            {/* Section D: Security & Password */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                4. Account Security
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Password <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      placeholder="Minimum 6 characters"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      style={{ width: '100%', padding: '10px 36px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
                    Confirm Password <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} color="#6b7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      required
                      placeholder="Re-enter password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      style={{ width: '100%', padding: '10px 36px 10px 38px', backgroundColor: '#0f172a', border: '1px solid #374151', borderRadius: '10px', color: '#f8fafc', fontSize: '13.5px', outline: 'none' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }}
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Password strength meter */}
              {formData.password && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ display: 'flex', gap: '4px', flex: 1 }}>
                    {[1, 2, 3, 4].map(level => (
                      <div
                        key={level}
                        style={{
                          height: '4px',
                          flex: 1,
                          borderRadius: '2px',
                          backgroundColor: strength >= level ? (strength >= 3 ? '#10b981' : '#f59e0b') : '#374151'
                        }}
                      />
                    ))}
                  </div>
                  <span style={{ fontSize: '11px', color: strength >= 3 ? '#10b981' : '#94a3b8' }}>
                    {strength <= 1 ? "Weak" : strength === 2 ? "Moderate" : strength === 3 ? "Good" : "Strong"}
                  </span>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !otpVerified}
              style={{
                padding: '13px 24px',
                background: otpVerified
                  ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
                  : '#374151',
                color: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                fontWeight: 700,
                fontSize: '15px',
                letterSpacing: '-0.01em',
                cursor: loading || !otpVerified ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: otpVerified ? '0 8px 20px rgba(99, 102, 241, 0.35)' : 'none',
                transition: 'all 0.2s ease',
                marginTop: '6px'
              }}
            >
              {loading ? (
                "Creating Account..."
              ) : (
                <>
                  <span>Complete Verified Registration</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>

            {!otpVerified && (
              <p style={{ fontSize: '12px', color: '#94a3b8', textAlign: 'center', margin: 0 }}>
                Please click <strong>Send OTP</strong> above to verify your email before submitting.
              </p>
            )}
          </form>

        </div>
      </div>
    </div>
  );
}
