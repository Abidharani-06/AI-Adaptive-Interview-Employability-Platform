import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import authService from '../services/authService';
import profileService from '../services/profileService';
import resumeService from '../services/resumeService';
import jobService from '../services/jobService';
import interviewService from '../services/interviewService';
import { getToken, clearToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(() => getToken());
  const [loading, setLoading] = useState(true);

  // Initialize and validate authenticated session on mount or token change
  const refreshUser = useCallback(async () => {
    const existingToken = getToken();
    if (!existingToken) {
      setUser(null);
      setTokenState(null);
      setLoading(false);
      return null;
    }

    try {
      const res = await authService.getCurrentUser();
      if (res.success && res.user) {
        setUser(res.user);
        setTokenState(existingToken);
        return res.user;
      } else {
        clearToken();
        setUser(null);
        setTokenState(null);
        return null;
      }
    } catch (err) {
      console.warn("[AuthContext] Session verification failed or expired:", err.message);
      clearToken();
      setUser(null);
      setTokenState(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Compute onboarding state for current candidate
  const onboardingState = useMemo(() => {
    if (!user) return 'LOGGED_OUT';
    if (!user.resume) return 'NO_RESUME';
    if (!user.targetRole) return 'NO_TARGET_ROLE';
    if (!user.currentAssessment) return 'NO_ASSESSMENT';
    if (!user.interviewHistory || user.interviewHistory.length <= 1) return 'HAS_ASSESSMENT';
    return 'RETURNING_USER';
  }, [user]);

  // Compute dynamic profile completion percentage
  const profileCompletion = useMemo(() => {
    if (!user) return 0;
    let score = 0;
    // Basic account credentials
    if (user.name && user.email) score += 20;
    if (user.college) score += 10;
    if (user.targetRole) score += 15;
    if (user.phone || user.location) score += 10;
    // Resume parsed
    if (user.resume && user.resume.skills && user.resume.skills.length > 0) score += 25;
    // Completed at least one mock interview
    if (user.currentAssessment) score += 20;
    return Math.min(100, score);
  }, [user]);

  // Login handler
  const login = async (email, password, rememberMe = true) => {
    try {
      const res = await authService.login(email, password, rememberMe);
      if (res.success && res.user) {
        setTokenState(res.token);
        // Refresh full user state including resume and assessment
        await refreshUser();
        return { success: true, user: res.user };
      }
      return { success: false, error: res.detail || "Login failed." };
    } catch (err) {
      return { success: false, error: err.message || "Invalid credentials." };
    }
  };

  // Register handler
  const register = async (userData, rememberMe = true) => {
    try {
      const res = await authService.register(userData, rememberMe);
      if (res.success && res.user) {
        setTokenState(res.token);
        await refreshUser();
        return { success: true, user: res.user };
      }
      return { success: false, error: res.detail || "Registration failed." };
    } catch (err) {
      return { success: false, error: err.message || "Registration failed." };
    }
  };

  // Logout handler
  const logout = async () => {
    try {
      await authService.logout();
    } catch (e) {
      // Ignore
    } finally {
      setUser(null);
      setTokenState(null);
    }
  };

  // Update profile
  const updateProfile = async (updates) => {
    try {
      const res = await profileService.updateProfile(updates);
      if (res.success && res.user) {
        setUser(prev => ({ ...prev, ...res.user }));
        return { success: true, user: res.user };
      }
      return { success: false, error: res.detail || "Failed to update profile." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Change password
  const changePassword = async (oldPassword, newPassword) => {
    try {
      const res = await profileService.changePassword(oldPassword, newPassword);
      return res;
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Upload and parse resume PDF
  const uploadResume = async (file) => {
    try {
      const res = await resumeService.uploadResume(file);
      if (res.success) {
        await refreshUser();
        return res;
      }
      return { success: false, error: "Resume upload failed." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Parse raw text resume
  const parseResumeText = async (rawText, fileName) => {
    try {
      const res = await resumeService.parseResumeText(rawText, fileName);
      if (res.success) {
        await refreshUser();
        return res;
      }
      return { success: false, error: "Resume parsing failed." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Match Job Description and update target role
  const updateJobDescription = async (title, descriptionText, targetRole) => {
    try {
      const res = await jobService.matchJob(title, descriptionText, targetRole);
      if (res.success) {
        await refreshUser();
        return res;
      }
      return { success: false, error: "Job matching failed." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Explicitly select or update target role
  const updateTargetRole = async (targetRole) => {
    try {
      const res = await jobService.updateTargetRole(targetRole);
      if (res.success) {
        setUser(prev => ({ ...prev, targetRole: res.targetRole }));
        return res;
      }
      return { success: false, error: "Failed to update target role." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Complete interview session and evaluate
  const completeInterview = async (sessionId, answers, cvResults = null, speechResults = null) => {
    try {
      const res = await interviewService.completeSession(sessionId, answers, cvResults, speechResults);
      if (res.success && res.assessment) {
        await refreshUser();
        return res;
      }
      return { success: false, error: "Evaluation failed." };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const assessment = user?.currentAssessment || null;

  return (
    <AuthContext.Provider
      value={{
        user,
        currentUser: user,
        candidate: user,
        assessment,
        isAuthenticated: !!user && !!token,
        loading,
        onboardingState,
        profileCompletion,
        login,
        register,
        logout,
        updateProfile,
        changePassword,
        uploadResume,
        parseResumeText,
        updateJobDescription,
        updateTargetRole,
        completeInterview,
        refreshUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export default AuthContext;
