/**
 * Multi-User Storage & Session Service
 * -------------------------------------
 * Handles candidate account persistence, session tokens, "Remember Me" logic,
 * and user-specific data isolation.
 * 
 * Supports:
 * - Session-based login (sessionStorage - cleared on tab/browser close)
 * - Persistent login (localStorage - preserved across sessions when Remember Me is enabled)
 * - Candidate profile, resume, interview attempts, and multimodal assessment storage per user.
 */

import { DEMO_CANDIDATES } from "../demoData/sampleCandidates";

const USERS_KEY = "ai_interview_users_registry_v2";
const ACTIVE_ID_KEY = "ai_interview_active_user_id";
const REMEMBER_ME_KEY = "ai_interview_remember_me";

// Simple non-reversible string digest for client-side demo safety (never store plaintext)
export function hashPassword(str) {
  let hash = 0;
  if (!str || str.length === 0) return "0";
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return "h_" + Math.abs(hash).toString(36);
}

// Initialize seed users if storage is empty
function initUsersRegistry() {
  const existing = localStorage.getItem(USERS_KEY);
  if (!existing) {
    const registry = {};
    DEMO_CANDIDATES.forEach((cand) => {
      registry[cand.id] = {
        ...cand,
        passwordHash: hashPassword("password123"),
        createdAt: "2026-09-01T00:00:00.000Z"
      };
    });
    localStorage.setItem(USERS_KEY, JSON.stringify(registry));
    return registry;
  }
  try {
    return JSON.parse(existing);
  } catch (e) {
    return {};
  }
}

export const storageService = {
  getUsersRegistry() {
    return initUsersRegistry();
  },

  saveUsersRegistry(registry) {
    localStorage.setItem(USERS_KEY, JSON.stringify(registry));
  },

  getUserById(userId) {
    if (!userId) return null;
    const registry = this.getUsersRegistry();
    return registry[userId] || null;
  },

  getUserByEmail(email) {
    if (!email) return null;
    const registry = this.getUsersRegistry();
    const cleanEmail = email.trim().toLowerCase();
    for (const id in registry) {
      if (registry[id].email.toLowerCase() === cleanEmail) {
        return registry[id];
      }
    }
    return null;
  },

  createUser(userData) {
    const registry = this.getUsersRegistry();
    const id = "usr_" + Date.now() + "_" + Math.random().toString(36).substring(2, 7);
    const newUser = {
      id,
      name: userData.name || "Candidate",
      email: userData.email.trim().toLowerCase(),
      college: userData.college || "Engineering College",
      targetRole: userData.targetRole || "Software Engineer",
      phone: userData.phone || "",
      location: userData.location || "",
      avatar: userData.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(userData.name || 'Candidate')}`,
      passwordHash: hashPassword(userData.password || "password123"),
      isDemo: false,
      createdAt: new Date().toISOString(),
      resume: null,
      jobDescription: null,
      currentAssessment: null,
      interviewHistory: []
    };

    registry[id] = newUser;
    this.saveUsersRegistry(registry);
    return newUser;
  },

  updateUser(userId, updates) {
    const registry = this.getUsersRegistry();
    if (!registry[userId]) return null;

    registry[userId] = {
      ...registry[userId],
      ...updates
    };
    this.saveUsersRegistry(registry);
    return registry[userId];
  },

  getActiveUser() {
    // Check sessionStorage first (active tab session)
    let activeId = sessionStorage.getItem(ACTIVE_ID_KEY);
    
    // If not in sessionStorage, check localStorage if "Remember Me" was enabled
    if (!activeId) {
      const isRemembered = localStorage.getItem(REMEMBER_ME_KEY) === "true";
      if (isRemembered) {
        activeId = localStorage.getItem(ACTIVE_ID_KEY);
      }
    }

    if (!activeId) return null;
    return this.getUserById(activeId);
  },

  setActiveUser(user, rememberMe = false) {
    if (!user) return;
    const id = user.id;

    if (rememberMe) {
      localStorage.setItem(ACTIVE_ID_KEY, id);
      localStorage.setItem(REMEMBER_ME_KEY, "true");
      sessionStorage.removeItem(ACTIVE_ID_KEY);
    } else {
      sessionStorage.setItem(ACTIVE_ID_KEY, id);
      localStorage.removeItem(ACTIVE_ID_KEY);
      localStorage.removeItem(REMEMBER_ME_KEY);
    }
  },

  clearActiveUser() {
    sessionStorage.removeItem(ACTIVE_ID_KEY);
    localStorage.removeItem(ACTIVE_ID_KEY);
    localStorage.removeItem(REMEMBER_ME_KEY);
  },

  getAllUsers() {
    const registry = this.getUsersRegistry();
    return Object.values(registry);
  },

  resetDemoData() {
    localStorage.removeItem(USERS_KEY);
    this.clearActiveUser();
    return initUsersRegistry();
  }
};

export default storageService;
