import axios from "axios";

export async function searchCandidates(payload) {
  const res = await axios.post("http://localhost:8000/api/v1/search", payload);
  return res.data;
}
