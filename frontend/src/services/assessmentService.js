import apiFetch, { API_BASE_URL, getToken } from './api';

export const assessmentService = {
  async getLatestAssessment() {
    return await apiFetch('/assessments/latest');
  },

  async getSkillGaps() {
    return await apiFetch('/assessments/skill-gaps');
  },

  async getRoadmap() {
    return await apiFetch('/assessments/roadmap');
  },

  async getFeedback() {
    return await apiFetch('/assessments/feedback');
  },

  async getProgress() {
    return await apiFetch('/assessments/progress');
  },

  async getReports() {
    return await apiFetch('/assessments/reports');
  },

  getDownloadUrl(format) {
    const token = getToken();
    return `${API_BASE_URL}/assessments/reports/download/${format}?token=${token || ''}`;
  }
};

export default assessmentService;
