import axios from "axios";

export async function sendFeedback({ candidateId, feedbackType }) {
  return axios.post("http://localhost:8000/api/v1/feedback", {
    candidateId,
    feedbackType,
  });
}
