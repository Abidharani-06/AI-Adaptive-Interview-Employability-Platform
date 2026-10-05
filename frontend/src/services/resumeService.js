import apiFetch from './api';

export const resumeService = {
  async uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);

    return await apiFetch('/resumes/upload', {
      method: 'POST',
      body: formData
    });
  },

  async parseResumeText(rawText, fileName = "Pasted_Resume.txt") {
    return await apiFetch('/resumes/parse-text', {
      method: 'POST',
      body: JSON.stringify({ rawText, fileName })
    });
  },

  async getCurrentResume() {
    return await apiFetch('/resumes/current');
  }
};

export default resumeService;
