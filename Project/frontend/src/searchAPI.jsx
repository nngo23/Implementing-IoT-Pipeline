import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export const searchCandidates = async ({
  query,
  top_k = 5,
  industry = null,
  salary_range = null,
  location_filter = null,
}) => {
  try {
    const response = await axios.post(`${API_BASE}/search`, {
      query,
      top_k,
      industry,
      salary_range,
      location_filter,
    });
    return response.data || null;
  } catch (err) {
    if (err.response?.status === 404) {
      // No results is NOT an error for UI
      return [];
    }
    throw err;
  }
};

export const sendFeedbackAPI = async ({
  candidateId,
  feedbackType,
  reason = null,
}) => {
  const response = await axios.post(`${API_BASE}/feedback`, {
    candidate_id: candidateId,
    feedback_type: feedbackType,
    reason,
  });
  return response.data;
};
