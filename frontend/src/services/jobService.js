import apiFetch from './api';

export const jobService = {
  async matchJob(title, descriptionText, targetRole) {
    return await apiFetch('/jobs/match', {
      method: 'POST',
      body: JSON.stringify({
        title,
        descriptionText,
        targetRole
      })
    });
  },

  async updateTargetRole(targetRole) {
    return await apiFetch('/jobs/target-role', {
      method: 'PUT',
      body: JSON.stringify({ targetRole })
    });
  },

  async getCurrentJob() {
    return await apiFetch('/jobs/current');
  }
};

export default jobService;
