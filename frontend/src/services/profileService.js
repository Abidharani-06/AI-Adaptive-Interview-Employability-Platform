import apiFetch from './api';

export const profileService = {
  async getProfile() {
    return await apiFetch('/profile');
  },

  async updateProfile(updates) {
    return await apiFetch('/profile', {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  },

  async changePassword(oldPassword, newPassword) {
    return await apiFetch('/profile/password', {
      method: 'PUT',
      body: JSON.stringify({ oldPassword, newPassword })
    });
  }
};

export default profileService;
