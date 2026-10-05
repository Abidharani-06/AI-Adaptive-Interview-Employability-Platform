import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles,
  Lock,
  Mail,
  Eye,
  EyeOff,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Badge from '../components/Badge';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
  const [resetSent, setResetSent] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setErrorMessage('');

    if (!email.trim() || !password) {
      setErrorMessage('Please enter both email address and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await login(email.trim(), password, rememberMe);
      if (res.success) {
        navigate('/dashboard');
      } else {
        setErrorMessage(res.error || 'Invalid credentials. Please verify your email and password.');
      }
    } catch (err) {
      setErrorMessage(err.message || 'An error occurred during authentication.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrorMessage('Please enter your email address to receive password reset instructions.');
      return;
    }
    setResetSent(true);
    setTimeout(() => {
      setResetSent(false);
      setForgotPasswordOpen(false);
    }, 3500);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', backgroundColor: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* Left Branding & Benefits Showcase */}
      <div
        style={{
          flex: '1.1',
          background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)',
          color: '#ffffff',
          padding: '60px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'relative',
          overflow: 'hidden'
        }}
        className="hidden-mobile"
      >
        <div style={{ position: 'relative', zIndex: 2 }}>
          {/* Logo & Headline */}
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
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)'
              }}
            >
              <Sparkles size={24} color="#ffffff" />
            </div>
            <div>
              <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                AI Interview
              </div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Multimodal Placement & Employability Platform
              </div>
            </div>
          </div>

          <h1 style={{ fontSize: '36px', fontWeight: 800, lineHeight: 1.25, letterSpacing: '-0.03em', marginBottom: '20px', color: '#f8fafc' }}>
            Precision Technical & Behavioral Preparation for High-Impact Careers.
          </h1>
          <p style={{ fontSize: '15px', color: '#cbd5e1', lineHeight: 1.6, maxWidth: '520px', marginBottom: '36px' }}>
            A rigorous, multi-user interview intelligence platform powered by adaptive technical problem solving, STAR behavioral NLP, observable computer vision cues, and acoustic speech delivery analysis.
          </p>

          {/* Pillars */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '480px' }}>
            {[
              { title: 'Resume & JD Competency Extraction', desc: 'Instant extraction of technical skills and high-priority preparation gaps across any engineering discipline.' },
              { title: 'Adaptive Technical Mock Sessions', desc: 'Questions dynamically personalized to your actual resume projects and selected target role.' },
              { title: 'HR & STAR Behavioral NLP', desc: 'Objective scoring of Situation, Task, Action, and measurable Results with real-time feedback.' },
              { title: 'Observable Presentation Signals', desc: 'Camera-facing gaze alignment, posture stability, and acoustic speaking rate analysis.' },
              { title: 'Dynamic Personalized Roadmap', desc: 'Tailored multi-week milestone schedule generated directly from your identified skill gaps.' }
            ].map((feat, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <CheckCircle2 size={18} color="#38bdf8" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <strong style={{ fontSize: '13.5px', color: '#f1f5f9' }}>{feat.title}</strong>
                  <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>{feat.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Ethical AI Certification Footer */}
        <div style={{ position: 'relative', zIndex: 2, display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px', color: '#94a3b8', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '20px' }}>
          <ShieldCheck size={16} color="#4ade80" />
          <span>Compliant with Ethical AI Standards: Observable presentation cues only. Zero psychological or emotion claims.</span>
        </div>
      </div>

      {/* Right Column: Authentication Form */}
      <div
        style={{
          flex: '1',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '40px 24px',
          overflowY: 'auto'
        }}
      >
        <div style={{ width: '100%', maxWidth: '420px' }}>
          
          <div className="card" style={{ padding: '36px', boxShadow: '0 8px 30px rgba(0,0,0,0.06)', borderRadius: '16px' }}>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '6px' }}>
                AI Interview Platform
              </div>
              <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
                Candidate Sign In
              </h2>
              <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '6px', margin: 0 }}>
                Enter your credentials to access your personalized dashboard.
              </p>
            </div>

            {errorMessage && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 14px',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  color: '#991b1b',
                  borderRadius: '8px',
                  fontSize: '13px',
                  marginBottom: '20px'
                }}
              >
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{errorMessage}</span>
              </div>
            )}

            {resetSent && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 14px',
                  backgroundColor: '#f0fdf4',
                  border: '1px solid #bbf7d0',
                  color: '#166534',
                  borderRadius: '8px',
                  fontSize: '13px',
                  marginBottom: '20px'
                }}
              >
                <CheckCircle2 size={16} color="#16a34a" style={{ flexShrink: 0 }} />
                <span>Password reset instructions have been sent to your email.</span>
              </div>
            )}

            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Email */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Email Address
                </label>
                <div style={{ position: 'relative' }}>
                  <Mail
                    size={18}
                    color="var(--text-muted)"
                    style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                  />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="candidate@university.edu"
                    required
                    style={{
                      width: '100%',
                      padding: '10px 12px 10px 38px',
                      borderRadius: '8px',
                      border: '1px solid var(--border-color)',
                      fontSize: '13.5px',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setForgotPasswordOpen(!forgotPasswordOpen)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--primary)',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      padding: 0
                    }}
                  >
                    Forgot Password?
                  </button>
                </div>
                <div style={{ position: 'relative' }}>
                  <Lock
                    size={18}
                    color="var(--text-muted)"
                    style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                  />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your account password"
                    required
                    style={{
                      width: '100%',
                      padding: '10px 38px 10px 38px',
                      borderRadius: '8px',
                      border: '1px solid var(--border-color)',
                      fontSize: '13.5px',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: 'var(--text-muted)',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  id="rememberMe"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--primary)', cursor: 'pointer' }}
                />
                <label htmlFor="rememberMe" style={{ fontSize: '13px', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                  Remember me on this browser
                </label>
              </div>

              {/* Login Button */}
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                icon={ArrowRight}
                iconPosition="right"
                style={{ width: '100%', justifyContent: 'center', marginTop: '6px' }}
              >
                Sign In to Dashboard
              </Button>
            </form>

            {/* Forgot Password Drawer */}
            {forgotPasswordOpen && (
              <div style={{ marginTop: '18px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                  Enter your email above and click below to reset your password:
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleForgotPassword}
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  Send Reset Link
                </Button>
              </div>
            )}

            {/* Create Account Link */}
            <div
              style={{
                marginTop: '24px',
                paddingTop: '20px',
                borderTop: '1px solid var(--border-color)',
                textAlign: 'center',
                fontSize: '13.5px',
                color: 'var(--text-secondary)'
              }}
            >
              Don't have an account?{' '}
              <Link
                to="/register"
                style={{
                  color: 'var(--primary)',
                  fontWeight: 700,
                  textDecoration: 'none'
                }}
              >
                Create Account / Register
              </Link>
            </div>

          </div>

        </div>
      </div>

    </div>
  );
}
