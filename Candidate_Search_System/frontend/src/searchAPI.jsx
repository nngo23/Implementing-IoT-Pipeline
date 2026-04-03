import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

/**
 * Send voice-transcribed query to backend search
 */
export const searchCandidatesVoice = async ({ query, distribution }) => {
  if (!query || query.trim().split(" ").length < 1) {
    throw new Error("At least one keyword/job title is required.");
  }

  const payload = {
    query,
    distribution, // "slack" or "email"
  };

  const response = await axios.post(`${API_BASE}/search`, payload);
  return response.data || null;
};
