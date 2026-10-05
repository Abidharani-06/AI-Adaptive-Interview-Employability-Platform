import apiFetch from './api';

export const interviewService = {
  async setupSession(config) {
    return await apiFetch('/interviews/setup', {
      method: 'POST',
      body: JSON.stringify({
        roundId: config.roundId || 'full',
        roundType: config.roundType || 'Full Mock Interview',
        targetRole: config.targetRole,
        questionCount: config.questionCount || 5,
        difficulty: config.difficulty || 'adaptive',
        enableCamera: config.enableCamera !== false,
        enableMicrophone: config.enableMicrophone !== false
      })
    });
  },

  async getSession(sessionId) {
    return await apiFetch(`/interviews/${sessionId}`);
  },

  async completeSession(sessionId, answers, cvResults = null, speechResults = null) {
    return await apiFetch(`/interviews/${sessionId}/complete`, {
      method: 'POST',
      body: JSON.stringify({
        answers,
        cvResults,
        speechResults
      })
    });
  }
};

export default interviewService;
