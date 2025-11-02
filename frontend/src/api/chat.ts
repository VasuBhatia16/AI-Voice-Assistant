import axios from "axios";
const isDev = import.meta.env.DEV;

export const BASE_URL = isDev
  ? "http://localhost:8000/api/v1/chat"
  : import.meta.env.VITE_API_URL;
export const sendMessage = async (prompt: string, sessionId: string) => {
  const res = await axios.post(`${BASE_URL}/chat/reply`, { prompt, session_id: sessionId });
  return res.data;
};
