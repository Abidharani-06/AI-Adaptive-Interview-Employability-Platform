import apiFetch, { setToken, clearToken } from './api';

export const authService = {
  /**
   * Dispatches a 6-digit email OTP for candidate identity verification.
   */
  async sendOtp(email) {
    return await apiFetch('/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ email: email.trim().toLowerCase() })
    });
  },

  /**
   * Validates the candidate's 6-digit OTP code against the backend hash.
   */
  async verifyOtp(email, otp) {
    return await apiFetch('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        otp: otp.trim()
      })
    });
  },

  /**
   * Completes candidate registration with verified profile attributes.
   */
  async register(userData, rememberMe = true) {
    const payload = {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      confirmPassword: userData.confirmPassword,
      phone: userData.phone || null,
      gender: userData.gender || null,
      dob: userData.dob || null,
      college: userData.college || "",
      degree: userData.degree || "",
      department: userData.department || "",
      yearOfStudy: userData.yearOfStudy || null,
      graduationYear: userData.graduationYear || "",
      city: userData.city || null,
      targetRole: userData.targetRole || null,
      otp: userData.otp || null,
      rememberMe
    };

    const res = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (res.token) {
      setToken(res.token, rememberMe);
    }
    return res;
  },

  async login(email, password, rememberMe = true) {
    const payload = {
      email: email.trim().toLowerCase(),
      password,
      rememberMe
    };

    const res = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (res.token) {
      setToken(res.token, rememberMe);
    }
    return res;
  },

  async logout() {
    try {
      await apiFetch('/auth/logout', { method: 'POST' });
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      clearToken();
    }
    return { success: true };
  },

  async getCurrentUser() {
    return await apiFetch('/auth/me');
  }
};

export default authService;
