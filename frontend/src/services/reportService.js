import apiFetch, { API_BASE_URL, getToken } from './api';

export const reportService = {
  /**
   * Fetches report records for the authenticated candidate.
   */
  async getReports() {
    return await apiFetch('/assessments/reports');
  },

  /**
   * Returns direct download URL for candidate report format (json, html, markdown, csv).
   */
  getDownloadReportUrl(format = 'json') {
    const token = getToken();
    return `${API_BASE_URL}/assessments/reports/download/${format.toLowerCase()}?token=${token || ''}`;
  },

  /**
   * Triggers download with authorization header or fallback blob download.
   */
  async downloadReport(format = 'json', fallbackData = null) {
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/assessments/reports/download/${format.toLowerCase()}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `employability_report.${format.toLowerCase()}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        return { success: true };
      }
    } catch (e) {
      console.warn("Backend report download failed, attempting fallback:", e.message);
    }

    // Client-side fallback if backend file was not persisted on disk
    if (fallbackData) {
      let content = "";
      let mimeType = "application/json";
      let ext = format.toLowerCase();

      if (ext === 'json') {
        content = JSON.stringify(fallbackData, null, 2);
        mimeType = "application/json";
      } else if (ext === 'csv') {
        const rows = [
          ["Metric", "Score"],
          ["Overall Employability", fallbackData.readiness?.score || 0],
          ["Technical", fallbackData.multimodal_assessment?.component_scores?.technical || 0],
          ["HR NLP", fallbackData.multimodal_assessment?.component_scores?.hr_nlp || 0],
          ["Speech", fallbackData.multimodal_assessment?.component_scores?.speech || 0],
          ["Computer Vision", fallbackData.multimodal_assessment?.component_scores?.computer_vision || 0],
          ["Resume Match", fallbackData.multimodal_assessment?.component_scores?.resume_jd || 0]
        ];
        content = rows.map(r => r.join(",")).join("\n");
        mimeType = "text/csv";
      } else if (ext === 'html') {
        content = `<!DOCTYPE html><html><head><title>Employability Assessment Report</title></head><body><h1>Placement Readiness Report</h1><pre>${JSON.stringify(fallbackData, null, 2)}</pre></body></html>`;
        mimeType = "text/html";
      } else {
        content = `# Placement Readiness Assessment\n\nOverall Score: ${fallbackData.readiness?.score || 0}%\nReadiness Tier: ${fallbackData.readiness?.level || 'N/A'}`;
        mimeType = "text/markdown";
      }

      const blob = new Blob([content], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `employability_assessment_report.${ext}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      return { success: true };
    }

    return { success: false, error: "Download failed" };
  }
};

export default reportService;
