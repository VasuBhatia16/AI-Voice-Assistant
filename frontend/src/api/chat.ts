import axios from "axios";

const BASE_URL = "http://localhost:8000/api/v1/chat";

export const sendMessage = async (prompt: string, sessionId: string) => {
  const res = await axios.post(`${BASE_URL}/reply`, { prompt, session_id: sessionId });
  return res.data;
};
