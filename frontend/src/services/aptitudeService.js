import apiFetch from './api';

export const aptitudeService = {
  /**
   * Initializes a new Round 1 Aptitude Assessment session.
   * Selects randomized questions across Quantitative, Logical, and Verbal sections.
   */
  async startAptitude({ sessionId = null, questionsPerSection = 5 } = {}) {
    return await apiFetch('/aptitude/start', {
      method: 'POST',
      body: JSON.stringify({
        sessionId,
        questionsPerSection
      })
    });
  },

  /**
   * Retrieves client-safe questions for an active attempt.
   */
  async getAttemptQuestions(attemptId) {
    return await apiFetch(`/aptitude/questions/${attemptId}`);
  },

  /**
   * Submits candidate answers for multi-dimensional scoring and weak-topic diagnostics.
   * answers format: [{ question_id, selected_option, time_taken_seconds }]
   */
  async submitAptitude({ attemptId, answers }) {
    return await apiFetch('/aptitude/submit', {
      method: 'POST',
      body: JSON.stringify({
        attemptId,
        answers
      })
    });
  },

  /**
   * Retrieves full evaluation report and answer logs for an attempt.
   */
  async getAptitudeResults(attemptId) {
    return await apiFetch(`/aptitude/results/${attemptId}`);
  },

  /**
   * Retrieves the candidate's latest completed aptitude assessment.
   */
  async getLatestAptitude() {
    return await apiFetch('/aptitude/latest');
  }
};

export default aptitudeService;
